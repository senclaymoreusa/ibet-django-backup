from django.http import HttpResponse
from games.models import GameBet
from users.models import UserAction
from accounting.models import Transaction
import redis
from utils.aws_helper import removeFromS3
from utils.aws_helper import writeToS3

import logging
from utils.redisHelper import RedisHelper
from datetime import datetime
import datetime
import pytz
from dateutil.parser import parse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

logger = logging.getLogger('django')
redis = RedisHelper()


# Method that copies Game Bet history to S3
# This is the first stage of the pipeline - the reason behind it is that, it's much more efficient
# to batch copy from S3 to Redshift than to insert records directly to Redshift
# I already setup a "Data Pipeline" in AWS to run the second stage (copying from S3 to Redshift)
# REF: https://console.aws.amazon.com/datapipeline/home?region=ap-northeast-1#ExecutionDetailsPlace:pipelineId=df-01600683VJZR9UCYHR8X&show=latest
@api_view(['POST'])
@permission_classes((AllowAny,))
def gamebet_copy(request):
    REDIS_KEY_LATEST_TIMESTAMP_GAMEBET = 'latest_timestamp:game_bet'
    max_datetime = datetime.datetime(1900, 1, 1).replace(tzinfo=pytz.UTC)

    ts_from_redis = redis.get_latest_timestamp(REDIS_KEY_LATEST_TIMESTAMP_GAMEBET)
    if ts_from_redis is None:
        latest_datetime = max_datetime
    else:
        latest_datetime = parse(ts_from_redis.decode())

    logger.info('The timestamp of the latest copy for GameBet was: ' + str(latest_datetime))
    results = GameBet.objects.filter(bet_time__gt=latest_datetime)

    filestr = ''
    count = 0

    for result in results:
        try:

            if result.bet_time > max_datetime:
                max_datetime = result.bet_time
            filestr = filestr \
                      + ('' if (result.provider is None or result.provider.provider_name is None) else
                         result.provider.provider_name) + ',' \
                      + ('' if (result.category is None or result.category.name is None) else
                         result.category.name) + ',' \
                      + ('' if (result.game is None or result.game.name is None) else
                         result.game.name) + ',' \
                      + ('' if (result.game is None or result.game.game_url is None) else
                         result.game.game_url) + ',' \
                      + ('' if (result.user is None or result.user.username is None) else
                         result.user.username) + ',' \
                      + ('' if (result.user is None or result.user.email is None) else
                         result.user.email) + ',' \
                      + ('' if result.amount_wagered is None else str(result.amount_wagered)) + ',' \
                      + ('' if result.amount_won is None else str(result.amount_won)) + ',' \
                      + ('' if result.outcome is None else result.get_outcome_display()) + ',' \
                      + ('' if result.odds is None else str(result.odds)) + ',' \
                      + ('' if result.bet_type is None else result.get_bet_type_display()) + ',' \
                      + ('' if result.line is None else result.line) + ',' \
                      + ('' if result.transaction_id is None else result.transaction_id) + ',' \
                      + ('' if result.currency is None else str(result.get_currency_display())) + ',' \
                      + ('' if result.market is None else str(result.get_market_display())) + ',' \
                      + ('' if result.ref_no is None else result.ref_no) + ',' \
                      + ('' if result.bet_time is None else str(result.bet_time)) + ',' \
                      + ('' if result.resolved_time is None else str(result.resolved_time)) + ',' \
                      + ('' if result.other_data is None else str(result.other_data)) + '\n'
            count = count + 1
        except Exception as e:
            error_message = "FATAL__ERROR piping GameBet entry into S3: exception = " + str(e)
            logger.error(error_message)
            return HttpResponse(error_message)

    logger.info(str(count) + ' new GameBet records have been retrieved in total. ')
    if count <= 0:
        return HttpResponse("count <= 0")

    removeFromS3('redshift-middle', 'game_bet/gamebet.csv')
    writeToS3(filestr, 'redshift-middle', 'game_bet/gamebet.csv')

    # Write the timestamp of the latest record processed to Redis
    redis.set_latest_timestamp(REDIS_KEY_LATEST_TIMESTAMP_GAMEBET, str(max_datetime))
    return HttpResponse(str(count) + ' new GameBet records have been retrieved in total. ')


# Method that copies Transaction history to S3
# Similar to gamebet_copy
# I already setup a "Data Pipeline" in AWS to run the second stage (copying from S3 to Redshift)
@api_view(['POST'])
@permission_classes((AllowAny,))
def transaction_copy(request):
    REDIS_KEY_LATEST_TIMESTAMP_TRANSACTION = 'latest_timestamp:transaction'
    max_datetime = datetime.datetime(1900, 1, 1).replace(tzinfo=pytz.UTC)

    ts_from_redis = redis.get_latest_timestamp(REDIS_KEY_LATEST_TIMESTAMP_TRANSACTION)
    if ts_from_redis is None:
        latest_datetime = max_datetime
    else:
        latest_datetime = parse(ts_from_redis.decode())

    logger.info('The timestamp of the latest copy for Transaction was: ' + str(latest_datetime))
    results = Transaction.objects.filter(request_time__gt=latest_datetime)

    filestr = ''
    count = 0

    for result in results:
        try:
            if result.request_time > max_datetime:
                max_datetime = result.request_time
            filestr = filestr \
                      + ('' if result.transaction_id is None else result.transaction_id) + ',' \
                      + ('' if (result.user_id is None or result.user_id.username is None) else
                         result.user_id.username) + ',' \
                      + ('' if (result.user_id is None or result.user_id.email is None) else
                         result.user_id.email) + ',' \
                      + ('' if result.order_id is None else result.order_id) + ',' \
                      + ('' if result.amount is None else str(result.amount)) + ',' \
                      + ('' if result.currency is None else str(result.get_currency_display())) + ',' \
                      + ('' if result.language is None else result.get_language_display()) + ',' \
                      + ('' if result.depositorTier is None else str(result.depositorTier)) + ',' \
                      + ('' if result.method is None else result.method) + ',' \
                      + ('' if result.channel is None else result.get_channel_display()) + ',' \
                      + ('' if result.last_updated is None else str(result.last_updated)) + ',' \
                      + ('' if result.request_time is None else str(result.request_time)) + ',' \
                      + ('' if result.arrive_time is None else str(result.arrive_time)) + ',' \
                      + ('' if result.status is None else result.get_status_display()) + ',' \
                      + ('' if result.transaction_type is None else result.get_transaction_type_display()) + ',' \
                      + ('' if result.remark is None else result.remark) + ',' \
                      + ('' if result.transfer_from is None else result.transfer_from) + ',' \
                      + ('' if result.transfer_to is None else result.transfer_to) + ',' \
                      + ('' if result.product is None else result.get_product_display()) + ',' \
                      + ('' if result.review_status is None else result.get_review_status_display()) + ',' \
                      + ('' if result.bank_info is None else result.bank_info) + ',' \
                      + ('' if result.transaction_image is None else result.transaction_image) + ',' \
                      + ('' if result.month is None else str(result.month)) + ',' \
                      + ('' if result.qrcode is None else result.qrcode) + ',' \
                      + ('' if (result.commission_id is None or result.commission_id.pk is None) else
                         str(result.commission_id.pk)) + ',' \
                      + ('' if result.other_data is None else str(result.other_data)) + ',' \
                      + ('' if (result.release_by is None or result.release_by.username is None) else
                         result.release_by.username) + '\n'
            count = count + 1
        except Exception as e:
            error_message = "FATAL__ERROR piping Transaction entry into S3: " + "current Transaction record = " + \
                            result.transaction_id + str(e)
            logger.error(error_message)
            return HttpResponse(error_message)

    logger.info(str(count) + ' new Transaction records have been retrieved in total. ')
    if count <= 0:
        return HttpResponse("No new transaction records available.")

    removeFromS3('redshift-middle', 'transaction/transaction.csv')
    writeToS3(filestr, 'redshift-middle', 'transaction/transaction.csv')

    # Write the timestamp of the latest record processed to Redis
    redis.set_latest_timestamp(REDIS_KEY_LATEST_TIMESTAMP_TRANSACTION, str(max_datetime))
    return HttpResponse(str(count) + ' new Transaction records have been retrieved in total. ')

# Method that copies UserAction history to S3
# Similar to gamebet_copy
# I already setup a "Data Pipeline" in AWS to run the second stage (copying from S3 to Redshift)
@api_view(['POST'])
@permission_classes((AllowAny,))
def user_action_copy(request):
    REDIS_KEY_LATEST_TIMESTAMP_USERACTION = 'latest_timestamp:user_action'
    max_datetime = datetime.datetime(1900, 1, 1).replace(tzinfo=pytz.UTC)

    ts_from_redis = redis.get_latest_timestamp(REDIS_KEY_LATEST_TIMESTAMP_USERACTION)
    if ts_from_redis is None:
        latest_datetime = max_datetime
    else:
        latest_datetime = parse(ts_from_redis.decode())

    logger.info('The timestamp of the latest copy for UserAction was: ' + str(latest_datetime))
    results = UserAction.objects.filter(created_time__gt=latest_datetime)

    filestr = ''
    count = 0

    for result in results:
        try:
            if result.created_time > max_datetime:
                max_datetime = result.created_time
            filestr = filestr \
                      + ('' if (result.user is None or result.user.username is None) else result.user.username) + ',' \
                      + ('' if (result.user is None or result.user.email is None) else result.user.email) + ',' \
                      + ('' if result.ip_addr is None else result.ip_addr) + ',' \
                      + ('' if result.event_type is None else result.get_event_type_display()) + ',' \
                      + ('' if result.device is None else str(result.device)) + ',' \
                      + ('' if result.browser is None else str(result.browser)) + ',' \
                      + ('' if result.refer_url is None else str(result.refer_url)) + ',' \
                      + ('' if result.page_id is None else str(result.page_id)) + ',' \
                      + ('' if result.created_time is None else str(result.created_time)) + '\n'
            count = count + 1
        except Exception as e:
            error_message = "FATAL__ERROR piping UserAction entry into S3: " + "current UserAction record = " + \
                            result.user.username + ", " + str(result.created_time) + str(e)
            logger.error(error_message)
            return HttpResponse(error_message)

    logger.info(str(count) + ' new UserAction records have been retrieved in total. ')
    if count <= 0:
        return HttpResponse("count <= 0")

    removeFromS3('redshift-middle', 'user_action/useraction.csv')
    writeToS3(filestr, 'redshift-middle', 'user_action/useraction.csv')

    # Write the timestamp of the latest record processed to Redis
    redis.set_latest_timestamp(REDIS_KEY_LATEST_TIMESTAMP_USERACTION, str(max_datetime))
    return HttpResponse(str(count) + ' new UserAction records have been retrieved in total. ')
