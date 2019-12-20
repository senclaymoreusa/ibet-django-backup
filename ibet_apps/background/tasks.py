#from background_task import background

from games.models import GameBet
from accounting.models import Transaction
from users.models import UserAction
from django.utils import timezone
from utils.aws_helper import writeToS3
import logging
from utils.redisHelper import RedisHelper
from datetime import datetime, date, time
import datetime
import pytz
from dateutil.parser import parse

logger = logging.getLogger('django')
redis = RedisHelper()

# Method that copies Game Bet history to S3
# This is the first stage of the pipeline - the reason behind it is that, it's much more efficient
# to batch copy from S3 to Redshift than to insert records directly to Redshift
# I already setup a "Data Pipeline" in AWS to run the second stage (copying from S3 to Redshift)
# REF: https://console.aws.amazon.com/datapipeline/home?region=ap-northeast-1#ExecutionDetailsPlace:pipelineId=df-01600683VJZR9UCYHR8X&show=latest
# @background(schedule=5000) # TODO: this is commented because it's still yet to decide whether we want to use background_task
def gamebet_copy():

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
        if result.bet_time > max_datetime:
            max_datetime = result.bet_time
        filestr = filestr \
                  + result.provider.provider_name + ',' \
                  + result.category.name + ',' \
                  + result.game.name + ',' \
                  + result.game.game_url + ',' \
                  + result.user.username + ',' \
                  + result.user.email + ',' \
                  + str(result.amount_wagered) + ','\
                  + str(result.amount_won) + ',' \
                  + result.get_outcome_display() + ',' \
                  + str(result.odds) + ',' \
                  + result.get_bet_type_display() + ',' \
                  + result.line + ',' \
                  + result.transaction_id + ',' \
                  + str(result.get_currency_display()) + ',' \
                  + str(result.get_market_display()) + ',' \
                  + result.ref_no + ',' \
                  + str(result.bet_time) + ',' \
                  + str(result.resolved_time) + ',' \
                  + str(result.other_data) + ',' + '\n'
        count = count + 1

    logger.info(str(count) + 'new GameBet records have been retrieved in total. ')
    if count <= 0:
        return

    # TODO: The bucket name and file name are still to be decided
    writeToS3(filestr, 'redshift-middle', 'input/gamebet.csv')

    # Write the timestamp of the latest record processed to Redis
    redis.set_latest_timestamp(REDIS_KEY_LATEST_TIMESTAMP_GAMEBET, str(max_datetime))


# Method that copies Transaction history to S3
# Similar to gamebet_copy
# I already setup a "Data Pipeline" in AWS to run the second stage (copying from S3 to Redshift)
def transaction_copy():

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
        if result.request_time > max_datetime:
            max_datetime = result.request_time
        filestr = filestr \
                  + result.transaction_id + ',' \
                  + result.user_id.username + ',' \
                  + result.user_id.email + ',' \
                  + result.order_id + ','\
                  + str(result.amount) + ',' \
                  + str(result.get_currency_display()) + ',' \
                  + result.get_language_display() + ',' \
                  + str(result.depositorTier) + ',' \
                  + result.method + ',' \
                  + result.get_channel_display() + ',' \
                  + str(result.last_updated) + ',' \
                  + str(result.request_time) + ',' \
                  + str(result.arrive_time) + ',' \
                  + result.get_status_display() + ',' \
                  + result.get_transaction_type() + ',' \
                  + result.remark + ',' \
                  + result.transfer_from + ',' \
                  + result.transfer_to + ',' \
                  + result.get_product_display() + ',' \
                  + result.get_review_status_display() + ',' \
                  + result.user_bank_account.account_name + ',' \
                  + result.user_bank_account.account_number + ',' \
                  + result.user_bank_account.bank.name + ',' \
                  + result.transaction_image + ',' \
                  + str(result.month) + ',' \
                  + result.qrcode + ',' \
                  + result.commission_id.pk + ',' \
                  + str(result.other_data) + ',' \
                  + result.release_by.username + ',' + '\n'
        count = count + 1

    logger.info(str(count) + 'new Transaction records have been retrieved in total. ')
    if count <= 0:
        return

    # TODO: The bucket name and file name are still to be decided
    writeToS3(filestr, 'redshift-middle', 'input/transaction.csv')

    # Write the timestamp of the latest record processed to Redis
    redis.set_latest_timestamp(REDIS_KEY_LATEST_TIMESTAMP_TRANSACTION, str(max_datetime))


# Method that copies UserAction history to S3
# Similar to gamebet_copy
# I already setup a "Data Pipeline" in AWS to run the second stage (copying from S3 to Redshift)
def user_action_copy():

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
        if result.created_time > max_datetime:
            max_datetime = result.created_time
        filestr = filestr \
                  + (result.user.username) + ',' \
                  + (result.user.email) + ',' \
                  + (result.ip_addr) + ',' \
                  + (result.get_event_type_display()) + ',' \
                  + str(result.device) + ',' \
                  + str(result.browser) + ',' \
                  + str(result.refer_url) + ',' \
                  + str(result.page_id) + ',' \
                  + str(result.created_time) + '\n'
        count = count + 1

    logger.info(str(count) + ' new UserAction records have been retrieved in total. ')
    if count <= 0:
        return

    # TODO: The bucket name and file name are still to be decided
    writeToS3(filestr, 'redshift-middle', 'input/useraction.csv')

    # Write the timestamp of the latest record processed to Redis
    redis.set_latest_timestamp(REDIS_KEY_LATEST_TIMESTAMP_USERACTION, str(max_datetime))
