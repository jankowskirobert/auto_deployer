import logging

import boto3

logger = logging.getLogger("main")


class ApiGatewayAdapter:

    def __init__(self):
        self.api_gateway_client = boto3.client('apigateway')

    def create_rest_api(self, api_name: str) -> tuple[str, str] | None:
        try:
            response = self.api_gateway_client.create_rest_api(
                name=api_name,
                endpointConfiguration={'types': ['REGIONAL']}
            )
            api_id = response['id']
            root_resource_id = response['rootResourceId']
            logger.info("REST API has been created successfully [api_name=%s, api_id=%s]", api_name, api_id)
            return api_id, root_resource_id
        except Exception as exp:
            logger.error("Could not create APIGateway REST API")
            return

    def create_resource(self, rest_api_id: str, parent_id: str, path_part: str) -> str | None:
        try:
            response = self.api_gateway_client.create_resource(
                restApiId=rest_api_id,
                parentId=parent_id,
                pathPart=path_part
            )
            logger.info("Created resource for API [resource=%s]", path_part)
            return response['id']
        except Exception as exp:
            logger.error("Could not create resource for API")
            return None

    def create_method(self, rest_api_id: str, resource_id: str, http_method: str, operation_mode: str):
        try:
            self.api_gateway_client.put_method(
                restApiId=rest_api_id,
                resourceId=resource_id,
                httpMethod=http_method,
                authorizationType='NONE',
                operationName=operation_mode,
                requestParameters={},
                requestModels={}
            )
            self.api_gateway_client.put_method_response(
                restApiId=rest_api_id,
                resourceId=resource_id,
                httpMethod=http_method,
                statusCode=200,
                responseModels={
                    'application/json': 'Empty'
                }
            )
            logger.info("Method has been created [http_method=%s]", http_method)
        except Exception as exp:
            logger.error('Could not create method for API [method_name=%s, operation_name=%s]', http_method, operation_mode)
            logger.error(exp)

    def integrate_with_lambda(
        self,
        rest_api_id: str,
        resource_id: str,
        http_method: str,
        lambda_arn: str
    ):
        try:
            self.api_gateway_client.put_integration(
                restApiId=rest_api_id,
                resourceId=resource_id,
                httpMethod=http_method,
                type='AWS',
                integrationHttpMethod='POST',
                uri=lambda_arn,
                timeoutInMillis=60,
                passthroughBehavior='WHEN_NO_TEMPLATES'
            )
            logger.info("Integration with lambda successfully created")
        except Exception as exp:
            logger.error("Could not create integration with lambda for Method in API")
            logger.error(exp)
