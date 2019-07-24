import boto3
import logging

logger = logging.getLogger('django')

def getThirdPartyKeys(bucket, file):
    s3client = boto3.client("s3")
    try:
        config_obj = s3client.get_object(Bucket=bucket, Key=file)
        config = json.loads(config_obj['Body'].read())
    except ClientError as e:
        logger_aws.error(e)
        return None
    except NoCredentialsError as e:
        logger_aws.error(e)
        return None
    
    return config

'''
def getAWSClient(service_name, third_party_keys):
    # AWS Client
    service = boto3.resource(service_name)
    client = boto3.client(
        service_name,
        aws_access_key_id = third_party_keys["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key = third_party_keys["AWS_SECRET_ACCESS_KEY"],
    )

    return client
'''