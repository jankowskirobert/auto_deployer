import logging
import hashlib
import boto3


logger = logging.getLogger("main")


class LambdaAdapter:

    def __init__(self):
        self.lambda_client = boto3.client('lambda')

    def grant_permission(self, lambda_name: str, statement_id: str, region: str, account_id: str, gateway_api_id: str, http_method: str, endpoint: str):

        short_hash = hashlib.shake_256(statement_id.encode()).hexdigest(5)
        try:
            self.lambda_client.add_permission(
                FunctionName=lambda_name,
                StatementId=statement_id+'-'+short_hash,
                Action='lambda:InvokeFunction',
                Principal='apigateway.amazonaws.com',
                SourceArn=f'arn:aws:execute-api:{region}:{account_id}:{gateway_api_id}/*/{http_method}/{endpoint}'
            )
        except Exception as exp:
            logger.error("Could not attach permissions to function")
            logger.error(exp)

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
            logger.info('Successfully created function [function_name=%s]', function_name)
        except Exception as exp:
            logger.error('Could not create new function [function_name=%s]', function_name)
            logger.error(exp)

    def delete_function(self, function_name: str):
        try:
            self.lambda_client.delete_function(
                FunctionName=function_name
            )
        except Exception as exp:
            logger.warning('Cannot remove function [function_name=%s]', function_name)
            logger.error(exp)
