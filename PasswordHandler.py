import boto3

class PasswordHandler:

    def __init__(self, secretName):
        self.secretName = secretName

    def getPassword(self):
        ssm = boto3.client('ssm')
        parameter = ssm.get_parameter(Name=self.secretName, WithDecryption=True)
        return parameter['Parameter']['Value']
