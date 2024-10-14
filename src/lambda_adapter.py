import logging

import boto3

from src.sys_utils import setup_basic_logger

logger = logging.getLogger("main")


class LambdaAdapter:

    def __init__(self):
        self.lambda_client = boto3.client('lambda')

    def grant_permission(self, lambda_arn: str, statement_id: str, actiom_name: str, principal: str, source_arn: str):
        response = self.lambda_client.add_permission(
            FunctionName=lambda_arn,
            StatementId='string',
            Action='string',
            Principal='string',
            SourceArn='string',
            FunctionUrlAuthType='NONE'
        )

    def create_lambda_function(
        self,
        function_name: str,
        role_arn: str,
        handler_path: str,
        s3_bucket_name: str,
        s3_key_name: str
    ):
        try:
            response = self.lambda_client.create_function(
                FunctionName=function_name,
                Runtime='python3.12',
                Role=role_arn,
                Handler=handler_path,
                Code={
                    # 'ZipFile': b'bytes',
                    'S3Bucket': s3_bucket_name,
                    'S3Key': s3_key_name
                },
                Timeout=15,
                MemorySize=128,
                Publish=True | False,
                PackageType='Zip',
                Architectures=[
                    'x86_64',
                ],
            )
            print(response)
            logger.info('Successfully created function [function_name=%s]', function_name)
        except Exception as exp:
            logger.error('Could not create new function [function_name=%s]', function_name)

    def delete_function(self, function_name: str):
        response = self.lambda_client.delete_function(
            FunctionName=function_name
        )


if __name__ == '__main__':
    setup_basic_logger()
    lambda_adapter = LambdaAdapter()
    lambda_adapter.create_lambda_function(
        'testing',
        'arn:aws:iam::927409320646:role/lambda-execution-manual',
        'start_ec2_instance_lambda.lambda_handler',
        'robertjankowski-test-test-3',
        'test-key'
    )
