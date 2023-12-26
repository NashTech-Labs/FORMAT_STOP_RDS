#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import boto3 

def lambda_handler(event, context):
    client_sns = boto3.client('sns')
    message = "" 
    client = boto3.client('ec2') 
    id = boto3.client('sts').get_caller_identity().get('Account')   
    
    #------------------------------EC2-----------------------------------------------------------------
    
    ec2_regions = [region['RegionName'] for region in client.describe_regions()['Regions']]
    
    for region in ec2_regions:   
        ec2 = boto3.resource('ec2',region_name=region)    
        instances = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
        RunningInstances = [instance.id for instance in instances]
          
        if len(RunningInstances) > 0:         
            for each in range(len(RunningInstances)):
                ec2_client = boto3.client('ec2',region_name=region)
                ec2_resp = ec2_client.describe_instances(InstanceIds=RunningInstances)
                for resp in ec2_resp['Reservations']:   
                    for each in resp['Instances']:
                        message += "EC2" + "\n"      
                        message += "Instance Id : " + each['InstanceId'] + "\n" 
                        message += "Region Name : " + each['Placement']['AvailabilityZone'] + "\n"
                        for t in each['Tags']:
                            if t['Key'] == 'Name':   
                                message += "Name : " + t['Value'] + "\n"        #name 
                            if t['Key'] == 'LastStartedBy':   
                                message += "Last started by : " + t['Value'] + "\n"
                        message += "Status : "+ "STOPPED" +"\n"
                        message += "-------------------------------------------------------------------------------------" + "\n"
                  # perform the shutdown   
                shuttingDown = ec2.instances.filter(InstanceIds=RunningInstances).stop()
              # print (shuttingDown)   
              
              
    #--------------------------RDS-----------------------------------------------------------------------------
            

    for ls in ec2_regions:    
        rds_client = boto3.client('rds',region_name=ls)    
        instances = rds_client.describe_db_instances()               
        for each in range(len(instances['DBInstances'])):   
            available = [i['DBInstanceIdentifier'] for i in instances['DBInstances'] if i['DBInstanceStatus'] == 'available']
            if len(available) > 0:
                Flag = True
                message += "RDS" + "\n"        
                message += "Name : " + instances['DBInstances'][each]['DBInstanceIdentifier'] +"\n"
                message += "ID : " + instances['DBInstances'][each]['DbiResourceId'] +'\n'
                message += "Last Started By : " + str(instances['DBInstances'][each]['TagList'][1]['Value']) +"\n"              
                message += "Status : " + "STOPPED" + "\n"
                message += "--------------------------------------------------------------------------------------" + "\n"
            
                #-------REMOVE THE COMMENTS TO STOP THE RDS------------------
              
                for x in available:
                    response = rds_client.stop_db_instance(
                    DBInstanceIdentifier = x
                    )       
              
      
    #-------------------------------message delivery work---------------------------------------------------------------
    if message == "":   
        message =" No EC2 or RDS instances are running currently!!!"
        resp = client_sns.publish(TargetArn="arn:aws:sns:ap-south-1:322971359654:rds_ec2_info", Message=message, Subject="RDS and EC2 Detail")
    else:
        resp = client_sns.publish(TargetArn="arn:aws:sns:ap-south-1:322971359654:rds_ec2_info", Message=message, Subject="RDS and EC2 Detail")   
        print(message)
        
        
        #    Please change the TargetArn to "arn:aws:sns:ap-south-1:322971359654:RDS_EC2_Status"    
        #   it has the neccesary subsciptions
