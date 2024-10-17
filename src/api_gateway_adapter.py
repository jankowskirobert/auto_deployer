import json
import logging
import time

import boto3
from botocore.config import Config

logger = logging.getLogger("main")


class ApiGatewayAdapter:

    def __init__(self):
        self.api_gateway_client = boto3.client("apigateway", config=Config(retries=dict(max_attempts=10)))

    def create_rest_api(self, api_name: str) -> tuple[str, str] | None:
        try:
            response = self.api_gateway_client.create_rest_api(
                name=api_name,
                endpointConfiguration={'types': ['REGIONAL']}
            )
            api_id = response['id']
            root_resource_id = response['rootResourceId']
            logger.info("REST API has been created successfully [rest_api_name=%s, rest_api_id=%s]", api_name, api_id)
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

    def create_method_validator(self, rest_api_id: str, validator_name: str) -> str:
        return self.api_gateway_client.create_request_validator(
            restApiId=rest_api_id,
            name=validator_name,
            validateRequestBody=True
        )['id']

    def create_method(self, rest_api_id: str, resource_id: str, http_method: str, operation_mode: str, request_model:str, request_validator_id: str | None = None):
        try:
            if request_validator_id:
                self.api_gateway_client.put_method(
                    restApiId=rest_api_id,
                    resourceId=resource_id,
                    httpMethod=http_method,
                    authorizationType='NONE',
                    operationName=operation_mode,
                    requestParameters={},
                    requestModels={'application/json': request_model},
                    requestValidatorId=request_validator_id
                )
            else:
                method_response = self.api_gateway_client.put_method(
                    restApiId=rest_api_id,
                    resourceId=resource_id,
                    httpMethod=http_method,
                    authorizationType='NONE',
                    operationName=operation_mode,
                    requestParameters={},
                    requestModels={'application/json': request_model}
                )
            self.api_gateway_client.put_method_response(
                restApiId=rest_api_id,
                resourceId=resource_id,
                httpMethod=http_method,
                statusCode='200',
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
                timeoutInMillis=6000,
                passthroughBehavior='WHEN_NO_TEMPLATES'
            )
            logger.info("Integration with lambda successfully created")
            self.api_gateway_client.put_integration_response(
                restApiId=rest_api_id,
                resourceId=resource_id,
                httpMethod=http_method,
                statusCode='200'
            )
        except Exception as exp:
            logger.error("Could not create integration with lambda for Method in API")
            logger.error(exp)

    def create_deployment_and_stage(self, rest_api_id: str, stage_name: str):
        try:

            self.api_gateway_client.create_deployment(
                restApiId=rest_api_id,
                stageName=stage_name
            )
            logger.info("API has been staged and deployed")
        except Exception as exp:
            logger.error("Could not stage and deploy API")
            logger.error(exp)

    def delete_all_rest_apis(self):
        """
        !Caution!
        Super long execution
        """
        try:
            response = self.api_gateway_client.get_rest_apis()
            for item in response['items']:
                rest_api_id = item['id']
                self.api_gateway_client.delete_rest_api(
                    restApiId=rest_api_id
                )
                logger.info('Successfully removed api [rest_api_id=%s]', rest_api_id)
        except Exception as exp:
            logger.error('Cannot delete rest APIs')
            logger.error(exp)

    def create_method_request_model(self, rest_api_id: str, model_name: str, model: dict):
        try:
            self.api_gateway_client.create_model(
                restApiId=rest_api_id,
                name=model_name,
                description='My custom model',
                schema=json.dumps(model),
                contentType='application/json'
            )
            logger.info('API model created')
        except Exception as exp:
            logger.error('Could not create API model')
            logger.error(exp)


if __name__ == '__main__':
    api_adapter = ApiGatewayAdapter()
    api_adapter.delete_all_rest_apis()
