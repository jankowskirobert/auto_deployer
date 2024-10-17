import logging

from src.api_gateway_adapter import ApiGatewayAdapter
from src.file_utils import create_lambdas_file_zip
from src.lambda_adapter import LambdaAdapter
from src.s3_adapter import S3Adapter
from src.ssm_adapter import SystemManagerAdapter
from src.sts_adapter import STSAdapter
from src.sys_utils import load_config
from src.utils.constants import EC2_CREATE_POST_REQUEST_MODEL, EC2_START_POST_REQUEST_MODEL, EC2_DELETE_DELETE_REQUEST_MODEL, EC2_STOP_POST_REQUEST_MODEL

logger = logging.getLogger("main")

lambda_adapter = LambdaAdapter()
s3_adapter = S3Adapter()
api_gateway_adapter = ApiGatewayAdapter()
ssm_adapter = SystemManagerAdapter()
sts_adapter = STSAdapter()
config = load_config()


def upload_lambdas_to_s3_bucket(lambda_functions_bucket_name: str,
                                lambdas_zip_path: str,
                                lambdas_file_s3_object_key: str,
                                s3_region: str):
    is_bucket_exists = s3_adapter.check_if_bucket_exists(lambda_functions_bucket_name)
    if is_bucket_exists:
        s3_adapter.upload_file_to_s3(lambdas_zip_path, lambda_functions_bucket_name, lambdas_file_s3_object_key)
        logger.info('Bucket found and file uploaded')
    else:
        logger.warning('No bucket found, creating new')
        s3_adapter.create_s3_bucket(lambda_functions_bucket_name, s3_region)
        s3_adapter.upload_file_to_s3(lambdas_zip_path, lambda_functions_bucket_name, lambdas_file_s3_object_key)


def execute_flow(region: str, invocation_name: str, lambdas_bucket_name: str, pems_bucket_name: str, root_api_path: str):
    caller_account_id = sts_adapter.get_account_id()
    # clean old functions
    lambda_adapter.delete_function('startEC2Instance')
    lambda_adapter.delete_function('stopEC2Instance')
    lambda_adapter.delete_function('createEC2Instance')
    lambda_adapter.delete_function('deleteEC2Instance')
    # clean old s3 objects
    s3_adapter.delete_s3_objects_from_bucket(
        lambdas_bucket_name,
        ['start_ec2', 'stop_ec2', 'create_ec2', 'delete_ec2']
    )
    # publish parameters
    setup_ssm_parameters(pems_bucket_name)
    # reupload
    zip_and_push_function(zipped_file='start_ec2',
                          handler='start_ec2_instance_lambda.lambda_handler',
                          function_name='startEC2Instance',
                          account_id=caller_account_id,
                          role_name='lambda-execution-manual',
                          lambdas_bucket_name=lambdas_bucket_name,
                          region=region)
    zip_and_push_function(zipped_file='stop_ec2',
                          handler='stop_ec2_instance_lambda.lambda_handler',
                          function_name='stopEC2Instance',
                          account_id=caller_account_id,
                          role_name='lambda-execution-manual',
                          lambdas_bucket_name=lambdas_bucket_name,
                          region=region)
    zip_and_push_function(zipped_file='create_ec2',
                          handler='create_ec2_instance_lambda.lambda_handler',
                          function_name='createEC2Instance',
                          account_id=caller_account_id,
                          role_name='lambda-execution-manual',
                          lambdas_bucket_name=lambdas_bucket_name,
                          region=region)
    zip_and_push_function(zipped_file='delete_ec2',
                          handler='delete_ec2_instance_lambda.lambda_handler',
                          function_name='deleteEC2Instance',
                          account_id=caller_account_id,
                          role_name='lambda-execution-manual',
                          lambdas_bucket_name=lambdas_bucket_name,
                          region=region)

    _rest_api_id, root_resource_id = api_gateway_adapter.create_rest_api(invocation_name + '-API-for-lambda')
    api_gateway_adapter.create_method_request_model(_rest_api_id, 'EC2Create', EC2_CREATE_POST_REQUEST_MODEL)
    api_gateway_adapter.create_method_request_model(_rest_api_id, 'EC2Start', EC2_START_POST_REQUEST_MODEL)
    api_gateway_adapter.create_method_request_model(_rest_api_id, 'EC2Stop', EC2_STOP_POST_REQUEST_MODEL)
    api_gateway_adapter.create_method_request_model(_rest_api_id, 'EC2Delete', EC2_DELETE_DELETE_REQUEST_MODEL)
    validator_id = api_gateway_adapter.create_method_validator(_rest_api_id, 'EC2CreateValidator')

    create_api_method_for_lambda(_rest_api_id,
                                 root_resource_id,
                                 'POST',
                                 'startEC2Instance',
                                 'start-ec2',
                                 'EC2Start',
                                 'Start EC2 Instance',
                                 region,
                                 caller_account_id,
                                 validator_id)
    lambda_adapter.grant_permission('startEC2Instance',
                                    'start-ec2-instance-permission-for-api',
                                    region,
                                    caller_account_id,
                                    _rest_api_id,
                                    'POST',
                                    'start-ec2')

    create_api_method_for_lambda(_rest_api_id,
                                 root_resource_id,
                                 'POST',
                                 'stopEC2Instance',
                                 'stop-ec2',
                                 'EC2Stop',
                                 'Stop EC2 Instance',
                                 region,
                                 caller_account_id,
                                 validator_id)
    lambda_adapter.grant_permission('stopEC2Instance',
                                    'stop-ec2-instance-permission-for-api',
                                    region,
                                    caller_account_id,
                                    _rest_api_id,
                                    'POST',
                                    'stop-ec2')

    create_api_method_for_lambda(_rest_api_id,
                                 root_resource_id,
                                 'POST',
                                 'createEC2Instance',
                                 'create-ec2',
                                 'EC2Create',
                                 'Create EC2 Instance',
                                 region,
                                 caller_account_id,
                                 validator_id)
    lambda_adapter.grant_permission('createEC2Instance',
                                    'create-ec2-instance-permission-for-api',
                                    region,
                                    caller_account_id,
                                    _rest_api_id,
                                    'POST',
                                    'create-ec2')

    create_api_method_for_lambda(_rest_api_id,
                                 root_resource_id,
                                 'DELETE',
                                 'deleteEC2Instance',
                                 'delete-ec2',
                                 'EC2Delete',
                                 'Delete EC2 Instance',
                                 region,
                                 caller_account_id,
                                 validator_id)
    lambda_adapter.grant_permission('deleteEC2Instance',
                                    'delete-ec2-instance-permission-for-api',
                                    region,
                                    caller_account_id,
                                    _rest_api_id,
                                    'DELETE',
                                    'delete-ec2')

    api_gateway_adapter.create_deployment_and_stage(_rest_api_id, root_api_path)


def zip_and_push_function(zipped_file,
                          handler,
                          function_name,
                          account_id,
                          role_name,
                          lambdas_bucket_name,
                          region
                          ):
    if (create_lambdas_file_zip('lambdas/' + zipped_file, zipped_file, 'zip')):
        upload_lambdas_to_s3_bucket(
            lambda_functions_bucket_name=lambdas_bucket_name,
            lambdas_zip_path='./' + zipped_file + '.zip',
            lambdas_file_s3_object_key=zipped_file,
            s3_region=region
        )
        lambda_adapter.create_lambda_function(
            function_name,
            f'arn:aws:iam::{account_id}:role/{role_name}',
            handler,
            lambdas_bucket_name,
            zipped_file
        )


def create_api_method_for_lambda(rest_api_id: str,
                                 root_resource_id: str,
                                 http_method: str,
                                 lambda_name: str,
                                 url_path: str,
                                 request_model: str,
                                 description: str,
                                 region: str,
                                 account_id: str,
                                 validator_id: str | None = None):
    lambda_arn = f'arn:aws:lambda:{region}:{account_id}:function:{lambda_name}'

    _resource_id = api_gateway_adapter.create_resource(
        rest_api_id,
        root_resource_id,
        url_path
    )

    api_gateway_adapter.create_method(rest_api_id, _resource_id, http_method, description, request_model, validator_id)
    api_gateway_adapter.integrate_with_lambda(
        rest_api_id,
        _resource_id,
        http_method,
        f'arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/{lambda_arn}/invocations'
    )


def setup_ssm_parameters(pems_bucket_name: str):
    ssm_adapter.put_string_parameter('pems-bucket-name', pems_bucket_name)
