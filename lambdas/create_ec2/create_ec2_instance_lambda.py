import logging
import sys
import uuid

import boto3

ec2_client = boto3.client('ec2')
client = boto3.client('s3')
ssm_client = boto3.client('ssm')

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def create_common_tag_for_execution(execution_id: str, resource_type: str):
    return [
        {
            'ResourceType': resource_type,
            'Tags': [
                {
                    'Key': 'ToolExecutionId',
                    'Value': execution_id
                },
            ]
        },
    ]


def get_default_vpc_for_account():
    response = ec2_client.describe_vpcs(
        Filters=[{
            'Name': 'isDefault', 'Values': ['true']
        }]
    )
    return response['Vpcs'][0]['VpcId']


def create_security_group_for_instance(execution_id: str, vpc_id: str, security_group_name: str) -> str | None:
    tag_spec = TagSpecification('security-group')
    tag_spec.add_tag('tool-execution-id', execution_id)
    try:
        response = ec2_client.create_security_group(
            Description='MyTestInstanceSecGroup',
            GroupName=security_group_name,
            VpcId=vpc_id,
            TagSpecifications=[tag_spec.build()]
        )
        logger.info('Security group created [security_group_name=%s]', security_group_name)
        return response['GroupId']
    except Exception as exp:
        logger.error('Could not create security group [security_group_name=%s]', security_group_name)
        logger.error(exp)
        return


def add_inbound_permissions(security_group_id: str):
    try:
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
        logger.info('Successfully authorized security group [security_group_id=%s]', security_group_id)
    except Exception as exp:
        logger.error('Could not authorize security group [security_group_id=%s]', security_group_id)
        logger.error(exp)


def create_subnet(vpc_id: str, region: str):
    response = ec2_client.create_subnet(
        VpcId=vpc_id,
        CidrBlock='172.31.8.0/20',
        AvailabilityZone=region

    )
    return response['Subnet']['SubnetId']


def create_free_tier_instance(execution_id: str, image_id: str, key_name: str, security_group_id: str, instance_name: str, instance_type: str) -> str | None:
    tag_spec = TagSpecification('instance')
    tag_spec.add_tag('Name', instance_name)
    tag_spec.add_tag('ToolExecutionId', execution_id)
    try:
        response = ec2_client.run_instances(
            ImageId=image_id,
            KeyName=key_name,
            MinCount=1,
            MaxCount=1,
            InstanceType=instance_type,
            SecurityGroupIds=[security_group_id],
            # SubnetId='',
            TagSpecifications=[
                tag_spec.build()
            ]

        )
        logger.info('Successfully created and started new instance [instance_name=%s]', instance_name)
        return response['Instances'][0]['InstanceId']
    except Exception as exp:
        logger.error('Could not create instance [instance_name=%s]', instance_name)
        logger.error(exp)


def create_key_pair(key_pair_name: str) -> dict:
    bucket_name = get_bucket_for_pem()
    try:
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
    except Exception as exp:
        logger.error('Something went wrong accessing key pair [key_pair_name=%s]', key_pair_name)
        logger.error(exp)


def upload_key_to_s3(bucket_name, key_material, key_pair_name) -> str:
    try:
        s3_key_response = client.put_object(
            Body=key_material.encode('ascii'),
            Bucket=bucket_name,
            Key=key_pair_name + '-instance-key.pem'
        )
        logger.info("Successfully uploaded pem into S3")
        return key_pair_name + '-instance-key.pem'
    except Exception as exp:
        logger.error('Could not upload pem to S3')
        logger.error(exp)


def get_bucket_for_pem() -> str:
    response = ssm_client.get_parameter(
        Name='pems-bucket-name',
        WithDecryption=False
    )
    return response['Parameter']['Value']


def execute(instance_name, instance_type, key_pair_name, image_id):
    execution_id = str(uuid.uuid4())
    default_vpc_id = get_default_vpc_for_account()
    security_group_id = create_security_group_for_instance(execution_id, default_vpc_id, instance_name + '_security-group')
    pair_response = create_key_pair(key_pair_name)
    instance_id = create_free_tier_instance(execution_id, image_id, key_pair_name, security_group_id, instance_name, instance_type)
    add_inbound_permissions(security_group_id)
    return pair_response | {'instanceId': instance_id}


def lambda_handler(event, context):
    try:
        instance_name = event['instanceName']
        instance_type = event['instanceType']
        key_pair_name = event['keyPairName']
        image_id = event['imageId']
        logger.info('instance_name=%s | instance_type=%s | key_pair_name=%s | image_id=%s', instance_name, instance_type, key_pair_name, image_id)
        creds = execute(instance_name, instance_type, key_pair_name, image_id)
        return creds
    except Exception as exp:
        return {
            'error': 'Could not stop instance',
            'errorReason': str(exp)
        }


class TagSpecification:

    def __init__(self, resource_type: str):
        self.resource_type = resource_type
        self.tags = []

    def add_tag(self, key: str, val: str):
        self.tags.append({
            'Key': key,
            'Value': val
        })

    def build(self):
        return {
            'ResourceType': self.resource_type,
            'Tags': self.tags
        }
