import boto3
import asyncio
import logging

from botocore.exceptions import ClientError
from utils.constants import *
from utils.aws_helper import getThirdPartyKeys, getAWSClient, getSQSQueue
from users.models import CustomUser

from django.conf import settings
from pytz import timezone

logger = logging.getLogger("django")

# example for deposit with Astropay


async def send_message_sqs(**tranDict):
    third_party_keys = getThirdPartyKeys("ibet-admin-dev", "config/sqs_access.json")
    client = getAWSClient("sqs", third_party_keys)
    bonus_queue = getSQSQueue(BONUS_QUEUE_NAME)

    # Get Transaction Type
    transaction_type = dict(TRANSACTION_TYPE_CHOICES).get(tranDict["transaction_type"])
    currency_type = dict(CURRENCY_CHOICES).get(tranDict["currency"])
    arrive_time = tranDict["arrive_time"].astimezone(timezone(settings.TIME_ZONE))

    # Set up logging
    # logging.basicConfig(level=logging.DEBUG,
    #                     format='%(levelname)s: %(asctime)s: %(message)s')

    # Send message to SQS queue
    # userid - user id(pk)
    # transtype - transaction type : deposit, withdrawal, bet placed
    # amount  - Transaction Amount
    # mainwallet - User main wallet
    # bonuswallet - User Bonus wallet
    # transtime - the transaction arrive time
    # currency - the currency type
    # product - game types choice Sports, Games, Live Casino
    try:
        msg = client.send_message(
            QueueUrl=bonus_queue.url,
            # DelaySeconds=10,
            MessageAttributes={
                "userid": {
                    "DataType": "Number",
                    "StringValue": str(tranDict["user_id"].pk),
                },
                "transtype": {"DataType": "String", "StringValue": transaction_type},
                "amount": {
                    "DataType": "Number",
                    "StringValue": str(tranDict["amount"]),
                },
                "mainwallet": {
                    "DataType": "Number",
                    "StringValue": str(tranDict["user_id"].main_wallet),
                },
                "bonuswallet": {
                    "DataType": "Number",
                    "StringValue": str(tranDict["user_id"].bonus_wallet),
                },
                "transtime": {
                    "DataType": "String.datetime",
                    "StringValue": str(arrive_time),
                },
                "currency": {"DataType": "String", "StringValue": currency_type},
                "product": {"DataType": "String", "StringValue": tranDict["product"]},
            },
            MessageBody=("Deposit Transaction(Astropay)"),
        )
    except ClientError as e:
        logger.error("Client Error. {}".format(e))
        return None
    return msg

