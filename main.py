#!/usr/bin/env python3
from boto3.session import Session
import re
from sso import get_account_roles, get_accounts, get_oidc_token
from cloudformation import list_stacks

import csv

def main():
  session = Session()
  token = get_oidc_token(session)
  access_token = token['accessToken']
  accounts = get_accounts(session, access_token)

  with open('stacks.csv', 'w+') as f:
    writer = csv.DictWriter(f, fieldnames=[
      'accountName', 
      'accountId',
      'stackName',
      'stackType',
      'stackVersion'
    ])
    writer.writeheader()

    for account in accounts:
      account_name = account['accountName']
      account_id = account['accountId']
      for role in get_account_roles(session, access_token, account_id):
          role_name = role['roleName']
          if role_name == 'di-support-readonly':
            sso = session.client('sso')
            role_creds = sso.get_role_credentials(
              roleName=role['roleName'],
              accountId=account_id,
              accessToken=access_token,
            )['roleCredentials']
            session = Session(
              region_name='eu-west-2',
              aws_access_key_id=role_creds['accessKeyId'],
              aws_secret_access_key=role_creds['secretAccessKey'],
              aws_session_token=role_creds['sessionToken'],
            )

            stacks = list_stacks(session)

            for stack in stacks:
              name = stack['StackName']
              description = stack.get('Description', '')
              m = re.match('^(di-)?devplatform-deploy ([a-z\-]+) template version: v([\d\.]+)', description)
              if m:
                writer.writerow({
                  'accountId': account_id,
                  'accountName': account_name,
                  'stackName': name,
                  'stackType': m.group(2),
                  'stackVersion': m.group(3)
                })




if __name__ == '__main__':
  main()
