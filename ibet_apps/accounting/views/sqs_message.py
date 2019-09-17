import boto3
import asyncio
import logging
import json

from botocore.exceptions import ClientError
from utils.constants import *
from utils.aws_helper import getThirdPartyKeys, getAWSClient, getSQSQueue
from users.models import CustomUser

from django.conf import settings
from pytz import timezone
import decimal
 # Set up logging
logger = logging.getLogger("django")

# example for deposit with Astropay
async def send_message_sqs(**tranDict):
    third_party_keys = getThirdPartyKeys("ibet-admin-eudev", "config/sqs_access.json")
    client = getAWSClient("sqs", third_party_keys, AWS_SQS_REGION)
    bonus_queue = getSQSQueue(BONUS_QUEUE_NAME)

    # Get Transaction Type
    transaction_type = dict(TRANSACTION_TYPE_CHOICES).get(tranDict["transaction_type"])
    currency_type = dict(CURRENCY_CHOICES).get(tranDict["currency"])
    arrive_time = tranDict["arrive_time"].astimezone(timezone(settings.TIME_ZONE))

    # Send message to SQS queue
    # userid - user id(pk)
    # transtype - transaction type : deposit, withdrawal, bet placed
    # amount  - Transaction Amount
    # mainwallet - User main wallet
    # bonuswallet - User Bonus wallet
    # transtime - the transaction arrive time
    # currency - the currency type
    # product - game types choice Sports, Games, Live Casino

    msg = json.dumps(
        {
            "userid": tranDict["user_id"].pk, 
            "bonuswallet": decimal.Decimal(tranDict["user_id"].bonus_wallet),
            "product": str(tranDict["product"]), 
            "amount": decimal.Decimal(tranDict["amount"]),
            "mainwallet": decimal.Decimal(tranDict["user_id"].main_wallet),
            "transtype": str(transaction_type), 
            "transtime": str(arrive_time),
            "currency": str(currency_type)
        },default=decimal_default
    )
    
    try:
        msg = client.send_message(
            QueueUrl=bonus_queue.url,
            MessageBody=(msg)
        )
        logger.info("Sent message: %s" % msg['MessageId'])
    except Exception as e:
        logger.error("Sent message error: %s" % e)


def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    logger.error("TypeError")