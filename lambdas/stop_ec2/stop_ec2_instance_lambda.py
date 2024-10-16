import json
import logging
import sys

import boto3

ec2_client = boto3.client('ec2')
logger = logging.getLogger(__name__)

logger.setLevel("INFO")
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def lambda_handler(event, context):
    # TODO implement stop
    response = ec2_client.describe_instances()
    logger.info('Test log')
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }
