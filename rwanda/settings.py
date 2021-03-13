"""
Django settings for rwanda project.

Generated by 'django-admin startproject' using Django 3.0.8.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from datetime import timedelta

from django.utils.translation import gettext_lazy as _

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'h=i^c29+u$^669mk^ba*6rmq*yw+qe$y#()fg5k9@4&(6v1td9'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

CORS_ORIGIN_WHITELIST = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:4000',
    'http://127.0.0.1:4000',
    'https://mdtaf.com',
    'https://www.mdtaf.com',
    'https://admin.mdtaf.com',
    'https://www.admin.mdtaf.com',
]

CORS_ALLOW_CREDENTIALS = True

# Application definition

INSTALLED_APPS = [
    'rwanda.users',
    'rwanda.services',
    'rwanda.administration',
    'rwanda.account',
    'rwanda.accounting',
    'rwanda.purchases',
    'rwanda.payments',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'graphene_django',
    'graphql_jwt.refresh_token.apps.RefreshTokenConfig',
    'corsheaders',
    'channels',
    'django_celery_results',
    'django_celery_beat'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'rwanda.middlewares.JSONWebTokenMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'rwanda.backends.JSONWebTokenBackend',
    'django.contrib.auth.backends.ModelBackend',
]

ROOT_URLCONF = 'rwanda.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'rwanda.context_processors.base_url',
                'rwanda.context_processors.today',
            ],
        },
    },
]

WSGI_APPLICATION = 'rwanda.wsgi.application'
ASGI_APPLICATION = 'rwanda.routing.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('redis', 6379)],
        },
    },
}

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'postgres',
        'PORT': 5432,

    }
}

AUTH_USER_MODEL = 'users.User'

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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

GRAPHENE = {
    'MIDDLEWARE': [
        'graphql_jwt.middleware.JSONWebTokenMiddleware',
    ],
}

GRAPHQL_JWT = {
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_LONG_RUNNING_REFRESH_TOKEN': True,
    'JWT_EXPIRATION_DELTA': timedelta(hours=2),
    'JWT_REFRESH_EXPIRATION_DELTA': timedelta(days=5),
}

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'fr'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LANGUAGES = [
    ('fr', _('French')),
    ('en', _('English')),
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, "locales"),
]

BASE_URL = 'http://localhost:8000'
FRONTEND_ACCOUNT_BASE_URL = 'http://localhost:3000'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
# STATIC_ROOT = 'static'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

MEDIA_URL = '/media/'
MEDIA_ROOT = 'media'

if not os.path.exists(os.path.join(BASE_DIR, "logs")):
    os.makedirs(os.path.join(BASE_DIR, "logs"))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'rwanda': {
            'formatter': 'verbose',
            'filename': os.path.join(BASE_DIR, "logs", "rwanda.log"),
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'midnight',
            'interval': 1,
        },
        'rwanda.payments': {
            'formatter': 'verbose',
            'filename': os.path.join(BASE_DIR, "logs", "payments.log"),
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'midnight',
            'interval': 1,
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['rwanda'],
            'level': 'WARNING',
            'propagate': True,
        },
        'rwanda.payments': {
            'handlers': ['rwanda.payments'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

CINETPAY_SIGNATURE_URL = "https://api.cinetpay.com/v1/?method=getSignatureByPost"
CINETPAY_PAYMENT_URL = "https://secure.cinetpay.com"
CINETPAY_CHECK_STATUS_URL = "https://api.cinetpay.com/v1/?method=checkPayStatus"
CINETPAY_AUTH_URL = "https://client.cinetpay.com/v1/auth/login"
CINETPAY_CHECK_BALANCE_URL = "https://client.cinetpay.com/v1/transfer/check/balance"
CINETPAY_TRANSFER_MONEY_URL = "https://client.cinetpay.com/v1/transfer/money/send/contact"
CINETPAY_ADD_CONTACT_URL = "https://client.cinetpay.com/v1/transfer/contact"
CINETPAY_API_KEY = "3281856345e6c13a1a91b61.98428115"
CINETPAY_SITE_ID = 414425
CINETPAY_CURRENCY = "CFA"

# EMAIL CONFIGS
DEFAULT_FROM_EMAIL = "mdtaf@mdtaf.com"
EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_HOST_USER = "apikey"
EMAIL_HOST_PASSWORD = "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"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'django-cache'
CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
