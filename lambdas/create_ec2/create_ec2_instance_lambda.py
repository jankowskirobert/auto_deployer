import json
import logging
import sys

import boto3

ec2_client = boto3.client('ec2')
client = boto3.client('s3')
ssm_client = boto3.client('ssm')

logger = logging.getLogger(__name__)
logger.setLevel("INFO")
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_default_vpc_for_account():
    response = ec2_client.describe_vpcs(
        Filters=[{
            'Name': 'isDefault', 'Values': ['true']
        }]
    )
    return response['Vpcs'][0]['VpcId']


def create_security_group_for_instance(vpc_id: str, security_group_name: str) -> str:
    response = ec2_client.create_security_group(
        Description='MyTestInstanceSecGroup',
        GroupName=security_group_name,
        VpcId=vpc_id
    )
    return response['GroupId']


def add_inbound_permissions(security_group_id: str):
    ec2_client.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            {
                'IpProtocol': 'tcp',
                'FromPort': 22,
                'ToPort': 22,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            }

        ]
    )


def create_subnet(vpc_id: str, region: str):
    response = ec2_client.create_subnet(
        VpcId=vpc_id,
        CidrBlock='172.31.8.0/20',
        AvailabilityZone=region
    )
    return response['Subnet']['SubnetId']


def create_free_tier_instance(key_name: str, security_group_id: str, instance_name: str) -> str:
    try:
        response = ec2_client.run_instances(
            ImageId='ami-00385a401487aefa4',
            KeyName=key_name,
            MinCount=1,
            MaxCount=1,
            SecurityGroupIds=[security_group_id],
            # SubnetId='',
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Name', 'Value': instance_name
                        }
                    ]
                }
            ]

        )
        return response['Instances'][0]['InstanceId']
    except Exception as exp:
        logger.error('Could not create instance')

def create_key_pair(key_pair_name: str) -> dict:
    bucket_name = get_bucket_for_pem()
    already_existing_key_response = ec2_client.describe_key_pairs(
        Filters=[
            {
                'Name': 'key-name',
                'Values': [key_pair_name]
            }
        ]
    )
    if len(already_existing_key_response['KeyPairs']) > 0:
        logger.info('Key creating interrupted, Key already exists')
        return {
            'user_name': 'ec2-user'
        }
    else:
        response = ec2_client.create_key_pair(KeyName=key_pair_name)
        key_material = response['KeyMaterial']
        object_name = upload_key_to_s3(bucket_name, key_material, key_pair_name)
        logger.info('Key has been created, check s3 bucket')
        return {
            'user_name': 'ec2-user',
            'ssh_pem': {
                'bucket': bucket_name,
                'object': object_name
            }
        }


def upload_key_to_s3(bucket_name, key_material, key_pair_name) -> str:
    s3_key_response = client.put_object(
        Body=key_material.encode('ascii'),
        Bucket=bucket_name,
        Key=key_pair_name + '-instance-key.pem'
    )
    return key_pair_name + '-instance-key.pem'


def get_bucket_for_pem() -> str:
    response = ssm_client.get_parameter(
        Name='pems-bucket-name',
        WithDecryption=False
    )
    return response['Parameter']['Value']


def execute():
    instance_name = 'testing-instance-12'
    default_vpc_id = get_default_vpc_for_account()
    security_group_id = create_security_group_for_instance(default_vpc_id, instance_name + '_security-group')
    pair_response = create_key_pair(instance_name)
    create_free_tier_instance(instance_name, security_group_id, instance_name)
    add_inbound_permissions(security_group_id)
    return pair_response

def lambda_handler(event, context):
    # TODO implement start
    creds = execute()
    return {
        'statusCode': 200,
        'body': json.dumps(creds)
    }
