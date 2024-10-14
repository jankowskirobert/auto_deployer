import boto3

client_role_iam = boto3.client("iam")

response = client_role_iam.create_role(
    RoleName='lambda-executor-role',
    AssumeRolePolicyDocument='string',
    Description='string',
    MaxSessionDuration=123,
    PermissionsBoundary='string',
    Tags=[
        {
            'Key': 'string',
            'Value': 'string'
        },
    ]
)