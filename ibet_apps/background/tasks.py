#from background_task import background

from games.models import GameBet
from accounting.models import Transaction
from users.models import UserAction
from django.utils import timezone
from utils.aws_helper import writeToS3
import logging

logger = logging.getLogger('django')

# Method that copies Game Bet history to S3
# This is the first stage of the pipeline - the reason behind it is that, it's much more efficient
# to batch copy from S3 to Redshift than to insert records directly to Redshift
# I already setup a "Data Pipeline" in AWS to run the second stage (copying from S3 to Redshift)
# REF: https://console.aws.amazon.com/datapipeline/home?region=ap-northeast-1#ExecutionDetailsPlace:pipelineId=df-01600683VJZR9UCYHR8X&show=latest
# @background(schedule=5000) # TODO: this is commented because it's still yet to decide whether we want to use background_task
def gamebet_copy():

    # TODO: This needs to be updated so that only the newer records will be retrieved from GameBet
    results = GameBet.objects.filter(bet_time__lt=timezone.now())

    filestr = ''
    count = 0
    for result in results:
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
    # TODO: The bucket name and file name are still to be decided
    writeToS3(filestr, 'redshift-middle', 'input/gamebet.csv')
