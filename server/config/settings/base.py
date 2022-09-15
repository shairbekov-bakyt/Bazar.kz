"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 4.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path
from celery.schedules import crontab
import os, sys

from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

PROJECT_ROOT = "/".join(os.path.dirname(__file__).split("/")[:-2])
sys.path.insert(0, os.path.join(PROJECT_ROOT, "apps"))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "user",
    "advert",
    "web_scraping",
    "chat",
    "custom_admin",
    "social_auth",

    "rest_framework",
    'rest_framework_simplejwt',
    "corsheaders",
    "drf_yasg",
    "celery",
    "django_filters",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "config.middleware.XForwardedForMiddleware",
    "config.middleware.AdvertCountMiddleware",
]

ROOT_URLCONF = "config.urls"
PREVIOUS_PASSWORD_COUNT = 2
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        # "HOST": config("DB_HOST"),
        "HOST": "localhost",
        "PORT": 5432,
        'TEST': {
            'NAME': 'test',
        },
    }
}
AUTH_USER_MODEL = "user.CustomUser"

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_BROKER_URL = "redis://" + REDIS_HOST + ":" + str(REDIS_PORT)
CELERY_RESULT_BACKEND = "redis://" + REDIS_HOST + ":" + str(REDIS_PORT)
CELERY_BROKER_TRANSPORT_OPTIONS = {"visibility_timeout": 3600}
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

CELERY_BEAT_SCHEDULE = {
      'advert_task_start_every_day': {
        'task': 'advert.tasks.task_send_advert_to_email',
        'schedule': crontab(hour=23),
        'args': '',
        'options': {
            'expires': 15.0,
        },
    },
    'add-every-morning': {
        'task': 'advert.tasks.task_save_advert_statistics',
        'schedule': crontab(minute=0, hour=0)
    },
}

'''
      'scraping_salexy_task_start_four_hour': {
        'task': 'web_scraping.tasks.task_salexy',
        'schedule': crontab(hour=4),
        'args': '',
        'options': {
            'expires': 15.0,
        },
    },
      'scraping_salexy_task_start_four_hour': {
        'task': 'web_scraping.tasks.task_doska',
        'schedule': crontab(hour=4),
        'args': '',
        'options': {
            'expires': 15.0,
        },
    },
}
'''


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = str(BASE_DIR.parent) + "/staticfiles"

MEDIA_ROOT = str(BASE_DIR.parent) + "/media"
MEDIA_URL = "/media/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_USE_TLS = True
EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
EMAIL_PORT = 587

JAZZMIN_SETTINGS = {
    "site_brand": "ZeonMall",
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'loggers': {
        '': {
            'handlers': ['error', 'info', 'debug'],
            'level': 1
        }
    },
    'handlers': {
        'std_err': {
            'class': 'logging.StreamHandler'
        },
        'info': {
            'class': 'logging.FileHandler',
            'filename': 'log/info.log',
            'level': 'INFO',
            'formatter': 'default',
        },
        'error': {
            'class': 'logging.FileHandler',
            'filename': 'log/error.log',
            'level': 'ERROR',
            'formatter': 'error',
        },
        'debug': {
            'class': 'logging.FileHandler',
            'filename': 'log/debug.log',
            'level': 'DEBUG',
            'formatter': 'default',
        },
    },
    'formatters': {
        'default': {
            'format': '%(asctime)s [%(module)s | %(levelname)s] %(message)s',
        },
        'error': {
            'format': '%(asctime)s [%(module)s | %(levelname)s] %(message)s @ %(pathname)s : %(lineno)d : %(funcName)s',
        },
    },
}




