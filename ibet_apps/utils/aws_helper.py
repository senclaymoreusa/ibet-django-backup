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

def getPTCertContent(bucket, file):
    s3client = boto3.client("s3")
    try:
        fileobj = s3client.get_object(Bucket=bucket, Key=file)
        filedata = fileobj['Body'].read()
        # contents = filedata.decode('utf-8')
       
    except ClientError as e:
        logger.error(e)
        return None
    except NoCredentialsError as e:
        logger.error(e)
        return None
    return filedata
    


# Method that writes filestr to S3 to bucket_name with file_name
def writeToS3(filestr, bucket_name, file_name):

    s3client = boto3.client("s3")
    try:
        logger.info('Writing to S3 to bucket ' + bucket_name + ' with file name ' + file_name)
        s3client.put_object(Body=filestr, Bucket=bucket_name, Key=file_name)
        logger.info('Successfully wrote to S3...')

    except ClientError as e:
        logger.error(e)
    except NoCredentialsError as e:
        logger.error(e)


def getAWSClient(service_name, third_party_keys, region):
    try:
        client = boto3.client(
            service_name,
            region_name=region,
            aws_access_key_id=third_party_keys["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=third_party_keys["AWS_SECRET_ACCESS_KEY"],
        )
    except ClientError as e:
        logger.error(e)
        return None
    except NoCredentialsError as e:
        logger.error(e)
        return None

    return client 

def getSQSQueue(queue_name):
    sqs = boto3.resource('sqs', region_name = "eu-west-2")
    try:
        queue = sqs.get_queue_by_name(QueueName=queue_name)
    except ClientError as e:
        logger.error(e)
        return None
    except NoCredentialsError as e:
        logger.error(e)
        return None

    return queue
