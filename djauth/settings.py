"""
Django settings for djauth project.

Generated by 'django-admin startproject' using Django 2.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os

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

# CORS_ORIGIN_ALLOW_ALL=True     # Stephen
CORS_ORIGIN_ALLOW_ALL=True

SESSION_COOKIE_SAMESITE = None
CRSF_COOKIE_SAMESITE = None


import sys
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,os.path.join(BASE_DIR, 'extra_app'))
sys.path.insert(0,os.path.join(BASE_DIR, 'apps'))

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
    'users.apps.UsersConfig', # new
    'operation.apps.OperationConfig',
    'games.apps.GamesConfig',
    'accounting.apps.AccountingConfig',
    'rest_framework',              # Stephen
    'corsheaders',                 # Stephen
    'rest_auth',                   # Stephen
    'rest_framework.authtoken',    # Stephen
    'django.contrib.sites',        # Stephen
    'allauth',                     # Stephen
    'allauth.account',             # Stephen
    'rest_auth.registration',      # Stephen
    'allauth.socialaccount',       # Stephen
    'django_rest_passwordreset',
    'django_nose',
    'reversion',
    'table',
]

SITE_ID = 1                        # Stephen

ACCOUNT_EMAIL_REQUIRED = False                # Stephen
ACCOUNT_AUTHENTICATION_METHOD = 'username'    # Stephen
ACCOUNT_EMAIL_VERIFICATION = 'none'           # Stephen

AUTH_USER_MODEL = 'users.CustomUser' # new???

DOMAIN = 'http://localhost:8000/'
HOST_URL = 'http://localhost:3000/'
SENDGRID_API_KEY = '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'

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',      # Stephen
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',  # Stephen
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
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
if 'RDS_DB_NAME' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ['RDS_DB_NAME'],
            'USER': os.environ['RDS_USERNAME'],
            'PASSWORD': os.environ['RDS_PASSWORD'],
            'HOST': os.environ['RDS_HOSTNAME'],
            'PORT': os.environ['RDS_PORT'],
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }


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

from django.utils.translation import ugettext_lazy as _
LANGUAGES = (
    ('en', _('English')),
    ('zh-hans', _('Chinese')),
    ('fr', _('Franch')),
)

TIME_ZONE = 'UTC'

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

STATIC_URL = '/static/'

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
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    }, 
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': 'logs/debug.log',
            'when': 'midnight', # Log file rollover at midnight
            'interval': 1, # Interval as 1 day
            'backupCount': 10, # how many backup file to keep, 10 days
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
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

AWS_S3_ADMIN_BUCKET = 'ibet-admin'

