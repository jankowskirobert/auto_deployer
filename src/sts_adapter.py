import boto3


class STSAdapter:

    def __init__(self):
        self.sts_client = boto3.client('sts')

    def get_account_id(self):
        return self.sts_client.get_caller_identity().get('Account')
