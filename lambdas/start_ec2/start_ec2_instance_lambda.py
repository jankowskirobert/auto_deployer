import json
import boto3

ec2_client = boto3.client('ec2')

def lambda_handler(event, context):
    # TODO implement start
    response = ec2_client.describe_instances()
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }
