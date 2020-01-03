from django.views import View
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from utils.constants import AWS_S3_ADMIN_BUCKET
from utils.redisClient import RedisClient
from utils.redisHelper import RedisHelper
import games.ftp.ftp_client as ftpClient
import boto3
import os
import xmltodict
import json
import logging

logger = logging.getLogger('django')

class GetEaBetHistory(View):

    def get(self, request, *args, **kwargs):
        ftp_connection = ftpClient.ftpConnect()
        fileList = []
        ftp_connection.ftp_session.retrlines('RETR gameinfolist.txt', fileList.append)
        try:
            r = RedisClient().connect()
            redis = RedisHelper()
        except:
            logger.error("There is something wrong with redis connection.")
            return HttpResponse({'status': 'There is something wrong with redis connection.'}, status=status.HTTP_400_BAD_REQUEST)

        last_file = redis.get_ea_last_file()
        processed = True
        if last_file is None:
            processed = False

        for f in fileList:
            localFileName = f.split('/')[-1]

            if last_file == localFileName:
                processed = False

            if last_file == localFileName or processed:
                continue

            logger.info('writing file to local: ' + localFileName)
            localFile = open(localFileName, 'wb')
            ftp_connection.ftp_session.retrbinary('RETR ' + f, localFile.write)
            localFile.close()

            s3client = boto3.client("s3")
            s3client.upload_file(localFileName, AWS_S3_ADMIN_BUCKET, 'EA-game-history/{}'.format(localFileName))
            logger.info('Uploading to S3 to bucket ' + AWS_S3_ADMIN_BUCKET + ' with file name ' + localFileName)

            with open(localFileName, 'r') as f:
                doc = xmltodict.parse(f.read())
                data = json.dumps(doc)
                # print(data)
                logger.info('store EA bet history to database')
                
            os.remove(localFileName)


        last_file = fileList[-1]
        redis.set_ea_last_file(last_file)
        logger.info('finished writting last file to s3')

        logger.info('finished processing the ea bet history')
        return HttpResponse({"code": 1, "message": "finished download ea bet history"}, content_type="application/json")