import boto3
import asyncio
import logging

from botocore.exceptions import ClientError
from utils.constants import *
from utils.aws_helper import getThirdPartyKeys, getAWSClient, getSQSQueue
from users.models import CustomUser

from django.conf import settings
from pytz import timezone

<<<<<<< HEAD
third_party_keys = getThirdPartyKeys("ibet-admin-dev", "config/sqs_access.json")
client = getAWSClient('sqs', third_party_keys)
bonus_queue = getSQSQueue(third_party_keys, BONUS_QUEUE_NAME)
=======
>>>>>>> ca1e909eebceebc917947afad086cfa29ba2e2fa
logger = logging.getLogger('django')

# example for deposit with Astropay
    
async def send_message_sqs(**tranDict):
<<<<<<< HEAD
=======
    third_party_keys = getThirdPartyKeys("ibet-admin-dev", "config/sqs_access.json")
    client = getAWSClient('sqs', third_party_keys)
    bonus_queue = getSQSQueue(third_party_keys, BONUS_QUEUE_NAME)
    
>>>>>>> ca1e909eebceebc917947afad086cfa29ba2e2fa
    # Get Transaction Type 
    transaction_type = dict(TRANSACTION_TYPE_CHOICES).get(tranDict['transaction_type'])
    currency_type = dict(CURRENCY_CHOICES).get(tranDict['currency'])
    arrive_time = tranDict['arrive_time'].astimezone(timezone(settings.TIME_ZONE))

    # Set up logging 
    # logging.basicConfig(level=logging.DEBUG,
    #                     format='%(levelname)s: %(asctime)s: %(message)s')

    # Send message to SQS queue
    try:
        msg = client.send_message(
            QueueUrl=bonus_queue.url,
            # DelaySeconds=10,
            MessageAttributes={
                'UserId': {
                    'DataType': 'Number',
                    'StringValue': str(tranDict['user_id'].pk),
                },
                'TransactionType': {
                    'DataType': 'String',
                    'StringValue': transaction_type,
                },
                'TransactionAmount': {
                    'DataType': 'Number',
                    'StringValue': str(tranDict['amount']),
                },
                'UserBalance': {
                    'DataType': 'Number',
                    'StringValue': str(tranDict['user_id'].main_wallet),
                },
                'TransactionTime': {
                    'DataType': 'String.datetime',
                    'StringValue': str(arrive_time),
                },
                'Currency': {
                    'DataType': 'String',
                    'StringValue': currency_type,
                },
                'Product': {
                    'DataType': 'String',
                    'StringValue': tranDict['product'],
                }
            },
            MessageBody=(
                'Deposit Transaction(Astropay)'
            )
        )
    except ClientError as e:
        logger.error("Client Error. {}".format(e))
        return None
    return msg



