import json
import boto3

ec2_client = boto3.client('ec2')

def lambda_handler(event, context):
    # TODO implement start
    response = ec2_client.start_instances(
        InstanceIds=[
            'string',
        ],
        AdditionalInfo='string',
        DryRun=True | False
    )
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }
