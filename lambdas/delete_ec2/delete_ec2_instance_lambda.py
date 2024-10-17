import json
import logging
import sys

import boto3

ec2_client = boto3.client('ec2')

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def lambda_handler(event, context):
    instance_id = event['instanceId']
    try:
        response = ec2_client.terminate_instances(
            InstanceIds=[
                instance_id,
            ]
        )
        logger.info('Instance has been Deleted [instance_id=%s]', instance_id)
        return {
            'statusCode': 200,
            'body': json.dumps(response)
        }
    except Exception as exp:
        logger.error('Could not delete instance [instance_id=%s]', instance_id)
        logger.error(exp)
        return {
            'error': 'Could not stop instance',
            'errorReason': str(exp)
        }