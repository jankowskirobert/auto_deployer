import logging

from src.file_utils import create_lambdas_file_zip
from src.lambda_adapter import LambdaAdapter
from src.s3_adapter import S3Adapter

logger = logging.getLogger("main")

lambda_adapter = LambdaAdapter()
adapter = S3Adapter()


def upload_lambdas_to_s3_bucket(
    lambda_functions_bucket_name: str,
    lambdas_zip_path: str,
    lambdas_file_s3_object_key: str,
    s3_region='eu-west-1'
):
    is_bucket_exists = adapter.check_if_bucket_exists(lambda_functions_bucket_name)
    if is_bucket_exists:
        adapter.upload_file_to_s3(lambdas_zip_path, lambda_functions_bucket_name, lambdas_file_s3_object_key)
        logger.info('Bucket found and file uploaded')
    else:
        logger.warning('No bucket found, creating new')
        adapter.create_s3_bucket(lambda_functions_bucket_name, s3_region)
        adapter.upload_file_to_s3(lambdas_zip_path, lambda_functions_bucket_name, lambdas_file_s3_object_key)


def execute_flow():

    zip_and_push_function(zipped_file='start_ec2',
                          handler='start_ec2_instance_lambda.lambda_handler',
                          function_name='startEC2Instance')
    zip_and_push_function(zipped_file='stop_ec2',
                          handler='stop_ec2_instance_lambda.lambda_handler',
                          function_name='stopEC2Instance')


def zip_and_push_function(zipped_file,
                          handler,
                          function_name):
    bucket_name = 'robertjankowski-py-lambdas'
    key_name = 'files'
    if (create_lambdas_file_zip('lambdas/' + zipped_file, zipped_file, 'zip')):
        upload_lambdas_to_s3_bucket(
            lambda_functions_bucket_name=bucket_name,
            lambdas_zip_path='./'+zipped_file+'.zip',
            lambdas_file_s3_object_key=zipped_file,
        )
        lambda_adapter.create_lambda_function(
            function_name,
            'arn:aws:iam::927409320646:role/lambda-execution-manual',
            handler,
            bucket_name,
            zipped_file
        )
