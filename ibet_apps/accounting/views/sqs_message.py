import boto3
import asyncio
import logging

from botocore.exceptions import ClientError
from utils.constants import *
from utils.aws_helper import getThirdPartyKeys, getAWSClient, getSQSQueueUrl
from users.models import CustomUser

third_party_keys = getThirdPartyKeys("ibet-admin-dev", "config/sqs_access.json")
client = getAWSClient('sqs', third_party_keys)
queue = getSQSQueueUrl(third_party_keys)
logger = logging.getLogger('django')

# example for deposit with Astropay
    
async def send_message_sqs(**tranDict):
    # Get Transaction Type 
    transaction_type = dict(TRANSACTION_TYPE_CHOICES).get(tranDict['transaction_type'])
    
     # Set up logging
    # logging.basicConfig(level=logging.DEBUG,
    #                     format='%(levelname)s: %(asctime)s: %(message)s')

    # Send message to SQS queue
    try:
        msg = client.send_message(
            QueueUrl=queue.url,
            DelaySeconds=10,
            MessageAttributes={
                'User_id': {
                    'DataType': 'Number',
                    'StringValue': str(tranDict['user_id'].pk),
                },
                'Transaction_type': {
                    'DataType': 'String',
                    'StringValue': transaction_type,
                },
                'Amount': {
                    'DataType': 'String',
                    'StringValue': tranDict['amount'],
                },
                'User_balance': {
                    'DataType': 'Number',
                    'StringValue': str(tranDict['user_id'].main_wallet),
                },
            },
            MessageBody=(
                'Deposit Transaction(Astropay)'
            )
        )
    except ClientError as e:
        logger.error("Client Error. {}".format(e))
        return None
    return msg



