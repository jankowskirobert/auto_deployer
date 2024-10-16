import logging


from src.api_gateway_adapter import ApiGatewayAdapter
from src.file_utils import create_lambdas_file_zip
from src.lambda_adapter import LambdaAdapter
from src.s3_adapter import S3Adapter
from src.ssm_adapter import SystemManagerAdapter
from src.sys_utils import load_config

logger = logging.getLogger("main")

lambda_adapter = LambdaAdapter()
s3_adapter = S3Adapter()
api_gateway_adapter = ApiGatewayAdapter()
ssm_adapter = SystemManagerAdapter()
config = load_config()

def upload_lambdas_to_s3_bucket(
    lambda_functions_bucket_name: str,
    lambdas_zip_path: str,
    lambdas_file_s3_object_key: str,
    s3_region='eu-west-1'
):
    is_bucket_exists = s3_adapter.check_if_bucket_exists(lambda_functions_bucket_name)
    if is_bucket_exists:
        s3_adapter.upload_file_to_s3(lambdas_zip_path, lambda_functions_bucket_name, lambdas_file_s3_object_key)
        logger.info('Bucket found and file uploaded')
    else:
        logger.warning('No bucket found, creating new')
        s3_adapter.create_s3_bucket(lambda_functions_bucket_name, s3_region)
        s3_adapter.upload_file_to_s3(lambdas_zip_path, lambda_functions_bucket_name, lambdas_file_s3_object_key)


def execute_flow():
    # clean old functions
    lambda_adapter.delete_function('startEC2Instance')
    lambda_adapter.delete_function('stopEC2Instance')
    # clean old s3 objects
    s3_adapter.delete_s3_objects_from_bucket(
        'robertjankowski-py-lambdas',
        ['start_ec2', 'stop_ec2', 'create_ec2']
    )
    # publish parameters
    setup_ssm_parameters()
    # reupload
    zip_and_push_function(zipped_file='start_ec2',
                          handler='start_ec2_instance_lambda.lambda_handler',
                          function_name='startEC2Instance')
    zip_and_push_function(zipped_file='stop_ec2',
                          handler='stop_ec2_instance_lambda.lambda_handler',
                          function_name='stopEC2Instance')
    zip_and_push_function(zipped_file='create_ec2',
                          handler='create_ec2_instance_lambda.lambda_handler',
                          function_name='createEC2Instance')

    _rest_api_id, root_resource_id = api_gateway_adapter.create_rest_api("ForLambda6")

    create_api_method_for_lambda(_rest_api_id, root_resource_id, 'GET', 'startEC2Instance', 'start-ec2', 'Start EC2 Instance', 'eu-west-1', '927409320646')
    lambda_adapter.grant_permission('startEC2Instance', 'start-ec2-instance-permission-for-api', 'eu-west-1', '927409320646', _rest_api_id, 'GET', 'start-ec2')

    create_api_method_for_lambda(_rest_api_id, root_resource_id, 'GET', 'stopEC2Instance', 'stop-ec2', 'Stop EC2 Instance', 'eu-west-1', '927409320646')
    lambda_adapter.grant_permission('stopEC2Instance', 'stop-ec2-instance-permission-for-api', 'eu-west-1', '927409320646', _rest_api_id, 'GET', 'stop-ec2')

    create_api_method_for_lambda(_rest_api_id, root_resource_id, 'GET', 'createEC2Instance', 'create-ec2', 'Create EC2 Instance', 'eu-west-1', '927409320646')
    lambda_adapter.grant_permission('createEC2Instance', 'create-ec2-instance-permission-for-api', 'eu-west-1', '927409320646', _rest_api_id, 'GET', 'create-ec2')


def zip_and_push_function(zipped_file,
                          handler,
                          function_name):
    bucket_name = 'robertjankowski-py-lambdas'
    if (create_lambdas_file_zip('lambdas/' + zipped_file, zipped_file, 'zip')):
        upload_lambdas_to_s3_bucket(
            lambda_functions_bucket_name=bucket_name,
            lambdas_zip_path='./' + zipped_file + '.zip',
            lambdas_file_s3_object_key=zipped_file,
        )
        lambda_adapter.create_lambda_function(
            function_name,
            'arn:aws:iam::927409320646:role/lambda-execution-manual',
            handler,
            bucket_name,
            zipped_file
        )


def create_api_method_for_lambda(rest_api_id: str, root_resource_id: str, http_method: str, lambda_name: str, url_path: str, description: str, region: str, account_id: str):
    # boto3.client('sts').get_caller_identity().get('Account')
    lambda_arn = f'arn:aws:lambda:{region}:{account_id}:function:{lambda_name}'
    region = 'eu-west-1'

    _resource_id = api_gateway_adapter.create_resource(
        rest_api_id,
        root_resource_id,
        url_path
    )

    api_gateway_adapter.create_method(rest_api_id, _resource_id, http_method, description)
    api_gateway_adapter.integrate_with_lambda(
        rest_api_id,
        _resource_id,
        http_method,
        f'arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/{lambda_arn}/invocations'
    )

def setup_ssm_parameters():
    ssm_adapter.put_string_parameter('pems-bucket-name', 'robertjankowski-pems')