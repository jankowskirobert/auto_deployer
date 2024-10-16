import logging

import boto3

logger = logging.getLogger("main")


class SystemManagerAdapter:

    def __init__(self):
        self.ssm_client = boto3.client('ssm')

    def put_string_parameter(self, parameter_name: str, parameter_value: str):
        try:
            self.ssm_client.put_parameter(
                Name=parameter_name,
                Value=parameter_value,
                Type='String',
                Overwrite=True,
                Tier='Standard',
                DataType='text'
            )
            logger.info('Successfully uploaded parameters to SSM Parameter Store')

        except Exception as exp:
            logger.error('Could not put parameters into SSM Parameter Store')
            logger.error(exp)
