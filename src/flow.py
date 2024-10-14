import logging

from src.file_utils import create_lambdas_file_zip
from src.s3_adapter import S3Adapter
from src.sys_utils import setup_basic_logger

logger = logging.getLogger("main")


def upload_lambdas_to_s3_bucket():
    adapter = S3Adapter()
    lambda_functions_bucket_name = 'robertjankowski-test-test-3'
    lambdas_zip_path = 'my-zip.zip'
    lambdas_file_s3_object_key = 'test-key'
    s3_region = 'eu-west-1'

    is_bucket_exists = adapter.check_if_bucket_exists(lambda_functions_bucket_name)
    if is_bucket_exists:
        adapter.upload_file_to_s3(lambdas_zip_path, lambda_functions_bucket_name, lambdas_file_s3_object_key)
        logger.info('Bucket found and file uploaded')
    else:
        logger.warning('No bucket found, creating new')
        adapter.create_s3_bucket(lambda_functions_bucket_name, s3_region)
        adapter.upload_file_to_s3(lambdas_zip_path, lambda_functions_bucket_name, lambdas_file_s3_object_key)


if __name__ == '__main__':
    setup_basic_logger()
    if (create_lambdas_file_zip('./lambda_functions', 'my-zip', 'zip')):
        upload_lambdas_to_s3_bucket()
