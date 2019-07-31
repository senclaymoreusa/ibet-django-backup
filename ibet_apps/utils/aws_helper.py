import boto3
import logging
import json
from botocore.exceptions import ClientError, NoCredentialsError

logger = logging.getLogger('django')

def getThirdPartyKeys(bucket, file):
    s3client = boto3.client("s3")
    try:
        config_obj = s3client.get_object(Bucket=bucket, Key=file)
        config = json.loads(config_obj['Body'].read())
    except ClientError as e:
        logger.error(e)
        return None
    except NoCredentialsError as e:
        logger.error(e)
        return None
    return config


def getAWSClient(service_name, third_party_keys):
    service = boto3.resource(service_name)
    try:
        client = boto3.client(
            service_name,
            aws_access_key_id = third_party_keys["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key = third_party_keys["AWS_SECRET_ACCESS_KEY"],
        )
    except ClientError as e:
        logger.error(e)
        return None
    except NoCredentialsError as e:
        logger.error(e)
        return None

    return client 

def getSQSQueue(third_party_keys, queue_name):
    sqs = boto3.resource('sqs')
    try:
        queue = sqs.get_queue_by_name(QueueName=queue_name)
    except NonExistentQueue as e:
        logger.error("Queue Not Exist. {}".format(e))
        return None

    return queue
