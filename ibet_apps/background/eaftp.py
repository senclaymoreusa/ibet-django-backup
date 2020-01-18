from django.views import View
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.utils import timezone

from games.models import GameBet, GameProvider, Category
from users.models import CustomUser
from utils.constants import *
from utils.redisClient import RedisClient
from utils.redisHelper import RedisHelper
import games.ftp.ftp_client as ftpClient

import pytz
import boto3
import os
import xmltodict
import json
import logging
import random
import datetime


logger = logging.getLogger('django')

class GetEaBetHistory(View):

    def get(self, request, *args, **kwargs):
        logger.info("connecting ea ftp")
        try:
            ftp_connection = ftpClient.ftpConnect()
        except Exception as e:
            logger.critical("(FATAL_ERROR) There is something wrong with ftp connection.", e)
            return HttpResponse({'status': 'There is something wrong with ftp connection.' + str(e)}, status=status.HTTP_400_BAD_REQUEST)

        file_list = []
        ftp_connection.ftp_session.retrlines('RETR gameinfolist.txt', file_list.append)
        try:
            r = RedisClient().connect()
            redis = RedisHelper()
            logger.info("connecting redis")
        except Exception as e:
            logger.critical("(FATAL_ERROR) There is something wrong with redis connection.", e)
            return HttpResponse({'status': 'There is something wrong with redis connection.'}, status=status.HTTP_400_BAD_REQUEST)

        last_file = redis.get_ea_last_file()
        last_file = last_file.decode("utf-8")
        processed = True
        if last_file is None:
            processed = False

        for f in file_list:

            local_file_name = f.split('/')[-1]
            if last_file == local_file_name:
                processed = False
            if last_file == local_file_name or processed:
                continue

            logger.info('writing file to local: ' + local_file_name)
            localFile = open(local_file_name, 'wb')
            ftp_connection.ftp_session.retrbinary('RETR ' + f, localFile.write)
            localFile.close()

            s3client = boto3.client("s3")
            try:
                s3client.upload_file(local_file_name, AWS_BET_S3_BUCKET, 'EA-game-history/{}'.format(local_file_name))
            except Exception as e:
                logger.warning("Uploading to S3 error", e)
            
            logger.info('Uploading to S3 to bucket ' + AWS_BET_S3_BUCKET + ' with file name ' + local_file_name)

            with open(local_file_name, 'r') as f:
                data = xmltodict.parse(f.read())
                # print(data)
                if 'gameinfo' in data and data['gameinfo'] and 'game' in data['gameinfo']:
                    all_game_types = data['gameinfo']
                    #multiple type of games playing in this time range
                    if isinstance(all_game_types['game'], list):
                        for each_game_type in all_game_types['game']:
                            # print(each_game_type)
                            game_code = each_game_type['@code']
                            bet_detail = each_game_type['deal']
                            gameHistoryToDatabase(bet_detail, game_code)
                    # only one type of game playing in this time range
                    else:
                        game_code = all_game_types['game']['@code']
                        bet_detail = all_game_types['game']['deal']
                        gameHistoryToDatabase(bet_detail, game_code)
                    logger.info('store EA bet history to database')
                else:
                    logger.info('There is no bet history between this time range')

                
            os.remove(local_file_name)


        last_file = file_list[-1]
        last_file_name = last_file.split('/')[-1]
        redis.set_ea_last_file(last_file_name)
        logger.info('finished writting last file {} to s3'.format(last_file))


        # test with one file will delete before merge
        
        # last_file = '123'
        # localFileName = "gameinfo202001040034 (1).xml"
        # with open(localFileName, 'r') as f:
        #     data = xmltodict.parse(f.read())
        #     # data = json.dumps(doc)
        #     # all_game_types = data['gameinfo']
        #     # print(all_game_types)
        #     # print(data)
        #     if 'gameinfo' in data:
        #         all_game_types = data['gameinfo']
        #         #multiple type of games playing in this time range
        #         if 'game' in all_game_types and isinstance(all_game_types['game'], list):
        #             for each_game_type in all_game_types['game']:
        #                 # print(each_game_type)
        #                 game_code = each_game_type['@code']
        #                 bet_detail = each_game_type['deal']
        #                 gameHistoryToDatabase(bet_detail, game_code)
        #         # only one type of game playing in this time range
        #         else:
        #             game_code = all_game_types['game']['@code']
        #             bet_detail = all_game_types['game']['deal']
        #             gameHistoryToDatabase(bet_detail, game_code)
                    
        logger.info('finished processing the ea bet history and end file is {}'.format(last_file))
        response = {
            "success": True,
            "message": 'finished processing the ea bet history and end file is {}'.format(last_file)
        }
        return HttpResponse(json.dumps(response), content_type="application/json")


def gameHistoryToDatabase(bet_detail, game_code):

    try: 
        provider = GameProvider.objects.get(provider_name=EA_PROVIDER)
        category = Category.objects.get(name='Live Casino')
    except Exception as e:
        logger.critical("(FATAL__ERROR) There is missing EA provider or category", e)

    for i in bet_detail:
        game_code_id = i['@code']
        game_end_date = i['@enddate']
        game_id = i['@id']
        game_start_date = i['@startdate']
        game_status = i['@status']
        bet_amount = i['betinfo']['clientbet']['@bet_amount']
        payout_amount = i['betinfo']['clientbet']['@payout_amount']
        username = i['betinfo']['clientbet']['@login']
        valid_turnover = i['betinfo']['clientbet']['@valid_turnover']

        # print(game_code_id, game_id, game_end_date, game_start_date, game_status, bet_amount, payout_amount, username, valid_turnover)

        # provider use Etc/GMT+8 timezone
        local = pytz.timezone ("Etc/GMT+8")
        game_start_date = datetime.datetime.strptime(game_start_date, "%Y-%m-%d %H:%M:%S")
        game_end_date = datetime.datetime.strptime(game_end_date, "%Y-%m-%d %H:%M:%S")
        local_start_date = local.localize(game_start_date, is_dst=None)
        local_end_date = local.localize(game_end_date, is_dst=None)
        utc_start_date = local_start_date.astimezone(pytz.utc)
        utc_end_date = local_end_date.astimezone(pytz.utc)

        user = CustomUser.objects.get(username=username)
        ibet_trans_id = user.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))
        if int(bet_amount) > int(payout_amount):
            outcome = 1
        elif int(bet_amount) == int(payout_amount):
            outcome = 2
        else:
            outcome = 0
        GameBet.objects.create(
            provider=provider,
            category=category,
            #game = None,
            #game_name = None,
            user=user,
            user_name=user.username,
            amount_wagered = float(int(bet_amount)/100),
            amount_won = float(int(payout_amount)/100),
            outcome = outcome,
            #odds = None,
            #bet_type = None,
            #line = None,
            transaction_id=ibet_trans_id,
            currency=user.currency,
            market=ibetVN, # do we need to store the market for game bet?
            ref_no=game_code_id,
            bet_time=utc_start_date,   #bet_time field should change
            resolved_time=utc_end_date,
            other_data={
                "start_time": str(game_start_date), 
                "end_time": str(game_end_date),
                "game_status": game_status,
                "valid_turnover": valid_turnover,
                "game_type": game_code,
                "deal_unique_id": game_id,
                "game_code_id": game_code_id
                }
        )


        logger.info("Successfully store the bet history to which code ID from EA is {}".format(game_code_id))