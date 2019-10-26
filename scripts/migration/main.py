######################################################################################
# This script is NOT part of any django projects and will be run alone by itself.    #
# The whole and only purpose is to migrate all the relevant data from the SQL Server #
# Database (in Taipei) to our Database.                                              #
# Hopefully, we shall need to run it for only ONCE.                                  #
######################################################################################

import pyodbc

import os
import boto3
import json
import logging
import datetime
import sys
import psycopg2


from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv
from django.utils.translation import ugettext_lazy as _





"""
# There's really no point for logging, so I will use print everywhere.
print ('Starting the Migration...')

# We do not need to deploy this script anywhere and for now the access is restricted to only our office,
# so there should be no problem to hard code all the credentials.
server = '169.254.223.130'
database = 'MainDB'
username = 'migration'
password = 'Clay1688'

try:
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
    cursor = cnxn.cursor()
except Exception as e:
    print ("Error connecting to SQL Server DB, Exiting...", e)
    exit(-1)

print ('Successfully connected to the DB:', server, database)
"""

print ('connecting to our postgres DB...')

logger = logging.getLogger('django')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print("[" + str(datetime.datetime.now()) + "] Trying to load environment variables...")
print (BASE_DIR)
if os.path.exists("/tmp/ibetenv/.env") or os.path.exists(BASE_DIR+"/.env"):
    print("[" + str(datetime.datetime.now()) + "] .env file found!")
else:
    print("[" + str(datetime.datetime.now()) + "] No .env file was found")


load_dotenv()
if "ENV" in os.environ:
    print("[" + str(datetime.datetime.now()) + "] Environment is: " + os.getenv("ENV"))
else:
    print("[" + str(datetime.datetime.now()) + "] Environment not specified!")


def getKeys(bucket, file):
    s3 = boto3.client('s3')
    try:
        keys = s3.get_object(Bucket=bucket, Key=file)
        config = json.loads(keys['Body'].read())
    except ClientError as e:
        logger.error(e)
        return None
    except NoCredentialsError as e:
        logger.error(e)
        return None

    return config


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '7i^ke1w79@h(!g0)e18c8(^j=c8ewfx8=*9n4652o%0f3i^g_-'

print("[" + str(datetime.datetime.now()) + "] Using db of dev")
AWS_S3_ADMIN_BUCKET = "ibet-admin-apdev"
db_data = getKeys(AWS_S3_ADMIN_BUCKET, 'config/ibetadmin_db.json')


print (db_data['RDS_DB_NAME'])


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': db_data['RDS_DB_NAME'],
        'USER': db_data['RDS_USERNAME'],
        'PASSWORD': db_data['RDS_PASSWORD'],
        'HOST': db_data['RDS_HOSTNAME'],
        'PORT': db_data['RDS_PORT'],
    }
}

connection = psycopg2.connect(  user = db_data['RDS_USERNAME'],
                                password = db_data['RDS_PASSWORD'],
                                host = db_data['RDS_HOSTNAME'],
                                port = db_data['RDS_PORT'],
                                database = db_data['RDS_DB_NAME'])

cursor = connection.cursor()


print ('connection successful')








































