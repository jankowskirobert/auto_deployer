import requests

stage = 'boben1'
api_id = 'ra2eu5ljhf'


def create():
    response = requests.post(f'https://{api_id}.execute-api.eu-west-1.amazonaws.com/{stage}/create-ec2', json={'instanceName': 'b41', 'instanceType': 't1.nano', 'keyPairName': 'testing3', 'imageId': 'ami-00385a401487aefa4'})
    print(response)
    print(response.text)
    return response.json()['instanceId']


def stop(instance_id):
    response = requests.post(f'https://{api_id}.execute-api.eu-west-1.amazonaws.com/{stage}/stop-ec2', json={'instanceId': instance_id})
    print(response)
    print(response.text)


def start(instance_id):
    response = requests.post(f'https://{api_id}.execute-api.eu-west-1.amazonaws.com/{stage}/start-ec2', json={'instanceId': instance_id})
    print(response)
    print(response.text)


def terminate(instance_id):
    response = requests.post(f'https://{api_id}.execute-api.eu-west-1.amazonaws.com/{stage}/delete-ec2', json={'instanceId': instance_id})
    print(response)
    print(response.text)


if __name__ == '__main__':
    instance_id = create()
    print('instance id: ' + instance_id)
    stop(instance_id)
