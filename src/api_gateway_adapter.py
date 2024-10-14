import logging

import boto3

from src.sys_utils import setup_basic_logger

logger = logging.getLogger("main")


class ApiGatewayAdapter:

    def __init__(self):
        self.api_gateway_client = boto3.client('apigateway')
        self.api_gateway_client = boto3.client('apigateway')

    def create_rest_api(self, api_name: str) -> str | None:
        try:
            response = self.api_gateway_client.create_rest_api(
                name=api_name,
                endpointConfiguration={'types': ['REGIONAL']}
            )
            api_id = response['id']
            logger.info("REST API has been created successfully [api_name=%s, api_id=%s]", api_name, api_id)
            return api_id
        except Exception as exp:
            logger.error("Could not create APIGateway REST API")
            return

    def create_resource(self, rest_api_id: str, parent_id: str, path_part: str):
        response = self.api_gateway_client.create_resource(
            restApiId=rest_api_id,
            parentId=parent_id,
            pathPart=path_part
        )

    def create_method(self, rest_api_id: str, resource_id: str, http_method: str, operation_mode: str):
        response = self.api_gateway_client.put_method(
            restApiId=rest_api_id,
            resourceId=resource_id,
            httpMethod=http_method,
            authorizationType='NONE',
            operationName=operation_mode,
            requestParameters={
                'string': True | False
            },
            requestModels={
                'string': 'string'
            }
        )

    def integrate_with_lambda(self, lambda_arn: str):

        response = client.put_integration(
            restApiId='string',
            resourceId='string',
            httpMethod='string',
            type= 'AWS_PROXY',
            integrationHttpMethod='string',
            uri='string',
            connectionType='INTERNET' | 'VPC_LINK',
            connectionId='string',
            credentials='string',
            requestParameters={
                'string': 'string'
            },
            requestTemplates={
                'string': 'string'
            },
            passthroughBehavior='string',
            cacheNamespace='string',
            cacheKeyParameters=[
                'string',
            ],
            contentHandling='CONVERT_TO_BINARY' | 'CONVERT_TO_TEXT',
            timeoutInMillis=123,
            tlsConfig={
                'insecureSkipVerification': True | False
            }
        )

if __name__ == '__main__':
    setup_basic_logger()
    api_gateway_adapter = ApiGatewayAdapter()
    _id = api_gateway_adapter.create_rest_api("ForLambda")
