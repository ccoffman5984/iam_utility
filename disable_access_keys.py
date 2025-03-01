# use python sdk to disable iam access keys older than 30 days

import boto3
import datetime as dt
from datetime import date
import os
import sys


account_id=sys.argv[1]

# assume role to disable access keys

sts_client = boto3.client('sts')
assumed_role_object=sts_client.assume_role( RoleArn=f'arn:aws:iam::{account_id}:role/DisableAccessKeys', RoleSessionName="AssumeRoleSession" )
credentials=assumed_role_object['Credentials']

#print(f'TOKEN: {credentials["SessionToken"]}')

os.environ['AWS_ACCESS_KEY_ID'] = credentials['AccessKeyId']
os.environ['AWS_SECRET_ACCESS_KEY'] = credentials['SecretAccessKey']
os.environ['AWS_SESSION_TOKEN'] = credentials['SessionToken']
# create a session      

session = boto3.Session()
client = session.client('iam')
response = client.list_users()

current_date = date.today()
# Get the current date in the format of YYYY-MM-DD
current_date = current_date.strftime("%Y-%m-%d")
d1 = dt.datetime.strptime(current_date, "%Y-%m-%d").date()

for user in response['Users']:
    
   response = client.list_access_keys(UserName=user['UserName'])    

   for key in response['AccessKeyMetadata']: 

      access_key_id = key['AccessKeyId']
      create_date = key['CreateDate'].strftime("%Y-%m-%d")

      print(f'IAM: {user} Access Key: {access_key_id} was created on {create_date}')

      d2 = dt.datetime.strptime(create_date, "%Y-%m-%d").date()
      age = abs((d2 - d1).days)

      if age > 30:
         client.update_access_key(AccessKeyId=access_key_id, Status='Inactive', UserName=user['UserName'])
         print(f'Access Key {access_key_id} is older than 30 days and has been disabled')
