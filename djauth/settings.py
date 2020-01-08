"""
Django settings for djauth project.

Generated by 'django-admin startproject' using Django 2.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import boto3
import json
import logging
import datetime
import sys

from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger('django')
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print("[" + str(datetime.datetime.now()) + "] Trying to load environment variables...")
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

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

CORS_ORIGIN_WHITELIST = [
    'localhost:3000'
]
CORS_ALLOW_CREDENTIALS = True

ALLOWED_HOSTS = ['*']       # Added this for Andorid to access back-end

CORS_ORIGIN_ALLOW_ALL = True

SESSION_COOKIE_SAMESITE = None
CSRF_COOKIE_SAMESITE = None


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
sys.path.insert(0,os.path.join(BASE_DIR, 'extra_app'))
sys.path.insert(0,os.path.join(BASE_DIR, 'ibet_apps'))

# Application definition

INSTALLED_APPS = [
    'test_without_migrations',
    'django.contrib.admin',
    'xadmin',
    'crispy_forms',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'users.apps.UsersConfig', # new
    'operation.apps.OperationConfig',
    'bonus.apps.BonusConfig',
    'games',
    'accounting.apps.AccountingConfig',
    'system.apps.SystemConfig',
    'rest_framework',              
    'corsheaders',                 
    'rest_auth',                   
    'rest_framework.authtoken',    
    'django.contrib.sites',        
    'allauth',                     
    'allauth.account',             
    'rest_auth.registration',      
    'allauth.socialaccount',       
    'django_rest_passwordreset',
    'django_nose',
    'reversion',
    'ckeditor',                    # ckeditor
    'ckeditor_uploader',           # ckeditor
    'django_user_agents',
]

CKEDITOR_UPLOAD_PATH = "uploads/"  # ckeditor

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        'width': 300,
    },
}

SITE_ID = 1                        

ACCOUNT_EMAIL_REQUIRED = False                
ACCOUNT_AUTHENTICATION_METHOD = 'username'    
ACCOUNT_EMAIL_VERIFICATION = 'none'           

AUTH_USER_MODEL = 'users.CustomUser' # Override the default user model and reference custom user model instead.

DOMAIN = 'http://localhost:8000/'
HOST_URL = 'http://localhost:3000/'
SENDGRID_API_KEY = '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'

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',      
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',  
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',
]

ROOT_URLCONF = 'djauth.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')], # new
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
            ],
        },
    },
]

WSGI_APPLICATION = 'djauth.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
# To accommodate bucket names across all regions, need to remove hard-coded value
# 
# ENV: 
#     USA: dev / prod
#     EU:  eudev / euprod
#

TESTING = sys.argv[1:2] == ['test']

if os.getenv("ENV") == "local":
    print("[" + str(datetime.datetime.now()) + "] Using local db")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'ibetlocal',
            'USER': '',
            'PASSWORD': '',
            'HOST': '',
            'PORT': 5432,
        }
    }


    print("[" + str(datetime.datetime.now()) + "] Using local Redis...")
    REDIS = {
        "HOST": 'localhost',
        "PORT": 6379
    }

elif "ENV" in os.environ:
    print("[" + str(datetime.datetime.now()) + "] Using db of " + os.environ["ENV"])
    AWS_S3_ADMIN_BUCKET = "ibet-admin-" + os.environ["ENV"]
    db_data = getKeys(AWS_S3_ADMIN_BUCKET, 'config/ibetadmin_db.json')
    
    print("DB HOST: " + db_data['RDS_HOSTNAME'])
    # print(db_data)
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

    print("[" + str(datetime.datetime.now()) + "] Using staging Redis...")
    REDIS = {
        # "HOST": 'staging-redis-cluster.hivulc.clustercfg.apne1.cache.amazonaws.com',
        "HOST": 'letou-staging-redis.hivulc.ng.0001.apne1.cache.amazonaws.com',
        "PORT": 6379
    }
    # print("letou-staging-redis.hivulc.ng.0001.apne1.cache.amazonaws.com")


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Rest Framework default settings (Stephen)
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_AUTHENTICATION_CLASSES': [
       'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]

}


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'
# LANGUAGE_CODE = 'zh-hans'


LANGUAGES = (
    ('en', _('English')),
    ('zh-hans', _('Chinese')),
    ('fr', _('Franch')),
)

# TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

DATETIME_FORMAT = '%d-%m-%Y-%H-%M-%S'

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_HTTPONLY = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

# STATIC_URL = '/static/'

# djauth/settings.py
# LOGIN_REDIRECT_URL = '/'
# LOGOUT_REDIRECT_URL = '/admin'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/
# The absolute path to the directory where collectstatic will collect static files for deployment.
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# The URL to use when referring to static files (where they will be served from)
STATIC_URL = '/static/'

# Simplified static file serving.
# https://warehouse.python.org/project/whitenoise/
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


log_filename = "logs/debug.log"
os.makedirs(os.path.dirname(log_filename), exist_ok=True)  


# Logging setup added by Stephen
if os.getenv("ENV") == "local":
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
                'datefmt': "%d/%b/%Y %H:%M:%S"
            },
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
        }, 
        'handlers': {
            'file':
                {
                    'level': 'DEBUG',
                    'class': 'logging.handlers.TimedRotatingFileHandler',
                    'filename': 'logs/debug.log',
                    'when': 'midnight', # Log file rollover at midnight
                    'interval': 1,  # Interval as 1 day
                    'backupCount': 10,  # how many backup file to keep, 10 days
                    'formatter': 'verbose',
                },
            'error':
                {
                    'level': 'ERROR',
                    'class': 'logging.handlers.TimedRotatingFileHandler',
                    'filename': 'logs/error.log',
                    'when': 'midnight',  # Log file rollover at midnight
                    'interval': 1,  # Interval as 1 day
                    'backupCount': 10,  # how many backup file to keep, 10 days
                    'formatter': 'verbose',
                }
        },
        'loggers': {
            'django': {
                'handlers': ['file', 'error'],
                # 'level': 'DEBUG',
                'propagate': True,
            },
        },
    }
else:
    print("AWS Logging to django-logger.log")
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': "[%(asctime)s] [%(levelname)s] [%(pathname)s:%(lineno)s] %(message)s",
                'datefmt': "%d/%b/%Y %H:%M:%S"
            },
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
        }, 
        'handlers': {
            'file': {
                'level': 'ERROR',
                'class': 'logging.FileHandler',
                'filename': '/opt/python/log/django-logger.log',
                'formatter': 'verbose',
            }
        },
        'loggers': {
            'django': {
                'handlers': ['file'],
                'level': 'ERROR',
                'propagate': True,
            },
        }
    }


TIME_ZONE = 'America/Los_Angeles'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'apps/users/media')


# Test Part
# Use nose to run all tests
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

# Tell nose to measure coverage on the 'foo' and 'bar' apps
NOSE_ARGS = [
    '--with-coverage',
    '--cover-package=users,accounting,games,operation',
    '--verbosity=1'
]

TEST_WITHOUT_MIGRATIONS_COMMAND = 'django_nose.management.commands.test.Command'

STATIC_DIRS = 'static'
STATICFILES_DIRS = [
    STATIC_DIRS,
]

AWS_S3_ADMIN_BUCKET = 'ibet-admin-dev'
PATH_TO_KEYS = 'config/thirdPartyKeys.json'


