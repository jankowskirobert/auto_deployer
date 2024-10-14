import logging

import boto3

logger = logging.getLogger("main")


class S3Adapter:

    def __init__(self):
        self.s3_resource = boto3.resource('s3')
        self.s3_client = boto3.client('s3')

    def check_if_bucket_exists(self, bucket_name: str) -> bool:
        try:
            self.s3_client.head_bucket(
                Bucket=bucket_name
            )
            logger.info('Bucket has been checked and it exists [bucket_name=%s]', bucket_name)
            return True
        except Exception as exp:
            logger.error('Failed to check bucket on S3')
            return False

    def upload_file_to_s3(self, filepath: str, bucket_name: str, object_key: str):
        try:
            self.s3_resource.meta.client.upload_file(
                filepath,
                bucket_name,
                object_key
            )
            logger.info('File has been successfully uploaded [bucket_name=%s]', bucket_name)
        except Exception as exp:
            logger.error('Failed to upload file to bucket on S3')

    def create_s3_bucket(self, bucket_name: str, location: str):
        try:
            self.s3_client.create_bucket(
                ACL='private',
                Bucket=bucket_name,
                CreateBucketConfiguration={
                    'LocationConstraint': location
                },
                ObjectLockEnabledForBucket=False,
                ObjectOwnership='BucketOwnerPreferred'
            )
            logger.info('Bucket has been successfully created [bucket_name=%s]', bucket_name)
        except Exception as exp:
            logger.error('Failed to create bucket on S3')
