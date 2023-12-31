"""
Django settings for mobypick_proj project.

Generated by 'django-admin startproject' using Django 4.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import boto3
from botocore.exceptions import ClientError
import json

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-3h)6gcyc($%ld$n%64-v(8w0vkvt63e-7#%bmvz4rf0j$4^-@l'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['mobypick.us-east-1.elasticbeanstalk.com', '127.0.0.1', 'localhost']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mobypick_app',
    'sslserver'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mobypick_proj.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mobypick_proj.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

#DATABASES = {
 #   'default': {
  #      'ENGINE': 'django.db.backends.sqlite3',
   #     'NAME': BASE_DIR / 'db.sqlite3',
   # }
#}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = 'static'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


BASE_URL = "https%3A%2F%2Fmobypick.us-east-1.elasticbeanstalk.com"
# BASE_URL = "https%3A%2F%2Flocalhost%3A8000"
REDIRECT_URL = "https%3A%2F%2Fmobypick.us-east-1.elasticbeanstalk.com%2Floading"
# REDIRECT_URL="https%3A%2F%2Flocalhost%3A8000%2Floading"
REQUEST_REDIRECT_URL="https://mobypick.us-east-1.elasticbeanstalk.com/loading"
# REQUEST_REDIRECT_URL="https://localhost:8000/loading"



secret_name = "serviceKeys"
region_name = "us-east-1"

# Create a Secrets Manager client
session = boto3.session.Session()
client = session.client(
service_name='secretsmanager',
region_name=region_name
)

try:
    get_secret_value_response = client.get_secret_value(SecretId=secret_name)
except ClientError as e:
    # For a list of exceptions thrown, see
    # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    raise e

secrets = json.loads(str(get_secret_value_response['SecretString']))

AWS_ACCESS_KEY = secrets['AWS_ACCESS_KEY']
AWS_SECRET_KEY = secrets['AWS_SECRET_KEY']
DYNAMO_USER_TABLE = 'UserInfo'

PERSONALIZE_EVENT_TRACKER = '53074283-8c08-43a9-a11e-56c9cc89b134'


RDS_USER = "admin"
RDS_PWD = secrets['RDS_PWD']
RDS_HOST = "mobypickbookreco.ctoo3wejf5nw.us-east-1.rds.amazonaws.com"
RDS_DB = "mobypickbookrec"

secret_name="cognitoSecret"

try:
    get_secret_value_response = client.get_secret_value(SecretId=secret_name)
except ClientError as e:
    # For a list of exceptions thrown, see
    # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    raise e


secrets = json.loads(str(get_secret_value_response['SecretString']))

COGNITO_CLIENT_ID='2e7kvbaanloridi3m4sn7qjmh1'
COGNITO_CLIENT_SECRET=secrets['COGNITO_CLIENT_SECRET']
COGNITO_REGION='us-east-1'
COGNITO_DOMAIN='https://mobypick.auth.us-east-1.amazoncognito.com'
