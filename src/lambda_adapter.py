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

    def create_lambda_function(self, function_name: str):
        response = self.lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.12',
            Role='arn:aws:iam::927409320646:role/lambda-execution-manual',
            Handler='start_ec2_instance_lambda.lambda_handler',
            Code={
                # 'ZipFile': b'bytes',
                'S3Bucket': 'robertjankowski-test-test-3',
                'S3Key': 'test-key'
            },
            Description='string',
            Timeout=15,
            MemorySize=128,
            Publish=True | False,

            PackageType='Zip',

            Architectures=[
                'x86_64',
            ],

        )


if __name__ == '__main__':
    setup_basic_logger()
    lambda_adapter = LambdaAdapter()
    lambda_adapter.create_lambda_function('testing')
