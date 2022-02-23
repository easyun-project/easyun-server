"""
  @module:  Easyun Deployment - Lambda
  @desc:    Deploy lambda function to AWS Cloud
  @auth:    aleck
"""
import boto3


Deploy_Region = 'us-east-1'


def lambda_creator(name):
    client_lambda = boto3.client('lambda', region_name= Deploy_Region)
    response = client_lambda.create_function(
        Code={
            'ZipFile': func_file()
        },
        Description='Dashboard inventory lambda function.',
        FunctionName='easyun-inventory-database',
        Handler='lambda_function.lambda_handler',
        Publish=True,
        Role='arn:aws:iam::565521294060:role/easyun-inventory-role',
        Runtime='python3.9',    
    )
    return response

def func_file(zip_name):
    with open(zip_name, 'rb') as file_data:
        bytes_content = file_data.read()
    return bytes_content
