from boto3.session import Session

def list_stacks(session: Session):
  cfn = session.client('cloudformation')

  paginator = cfn.get_paginator('describe_stacks').paginate()

  for page in paginator:
    for stack in page['Stacks']:
      yield stack
