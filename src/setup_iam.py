import boto3

apigateway = boto3.client("apigateway")

response = apigateway.create_rest_api(
    name='My Test Rest API',
    description='api testing',
    version='v1',
    binaryMediaTypes=[
        'application/json',
    ],
    minimumCompressionSize=123,
    apiKeySource='HEADER',
    endpointConfiguration={
        'types': [
            'REGIONAL',
        ]
    },
    tags={
        'mytaggo': 'balbla'
    },
    disableExecuteApiEndpoint=True
)

print("execution ", response['id'])
