"""
Django settings for games project.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""
import os

import dj_database_url

from .config import config as devops_config
import mimetypes
from google.oauth2 import service_account

mimetypes.add_type("image/svg+xml", ".svg", True)
mimetypes.add_type("image/svg+xml", ".svgz", True)


# версия шаблона
TEMPLATE_VERSION = "1.4.3"

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname( os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = devops_config['secret_key'].text

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = devops_config.get('debug', False)

ALLOWED_HOSTS = ['*']

AUTH_USER_MODEL = 'games.User'

REST_AUTH_SERIALIZERS = {
    "USER_DETAILS_SERIALIZER": "games.api.serializers.CustomUserDetailsSerializer",
}

REST_AUTH_REGISTER_SERIALIZERS = {
    "REGISTER_SERIALIZER": "games.api.serializers.CustomRegisterSerializer"
}

ACCOUNT_ADAPTER = 'games.api.adapters.CustomUserAccountAdapter'


# Application definition
INSTALLED_APPS = [

    # 'fluent_dashboard',
    # 'admin_tools',
    # 'admin_tools.dashboard',

    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework.authtoken',
    'rest_auth',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'rest_auth.registration',

    'games',
    'admin_reorder',

    'rest_framework_swagger',

]

# DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
# GS_BUCKET_NAME = 'kit4kid'
# GS_CREDENTIALS = service_account.Credentials.from_service_account_file("/conf/credentials.json")

DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated', )
}


AWS_ACCESS_KEY_ID = 'AKIAVOOOS3SAIZMICZV6'
AWS_SECRET_ACCESS_KEY = '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'
EMAIL_BACKEND = 'django_ses.SESBackend'

AWS_SES_REGION_NAME = 'eu-west-1'
AWS_SES_REGION_ENDPOINT = 'email.eu-west-1.amazonaws.com'

ADMIN_REORDER = (

    {
        'app': 'games', 'label': 'Пользователи',
        'models': (
            'games.User',
            'games.Child',
            'games.Statistic'
        )
    },


    {
        'app': 'games', 'label': 'Массивы изображений игр № 1, 2, 3 (сопоставления, различения, категории)',
        'models': (
            'games.Game_1_obj',
        )
    },

    {
        'app': 'games', 'label': 'Группы изображений игры № 4 (Последовательности)',
        'models': (
            'games.Game_2_Obj_Level_1',
            'games.Game_2_Obj_Level_2',
            'games.Game_2_Obj_Level_3',
        )
    },

    {
        'app': 'games', 'label': 'Массив изображений игры № 5 (Игра №5 - глаголы)',
        'models': (
            'games.Game_3_Obj',
        )
    },


    {
        'app': 'games', 'label': 'Параметры массива №1',
        'models': (
            'games.Form',
            'games.Category',
            'games.Color',
            'games.FunctionalQuestion',
            'games.CompoundQuestion',
            'games.DefinitionQuestion',
            'games.Material',
            'games.SubCategory',
            'games.Quantity',
        )
    },


    {
        'app': 'games', 'label': 'Файлы',
        'models': (
            'games.Audio',
        )
    },

    {
        'app': 'games', 'label': 'Игры',
        'models': (
            'games.Rule',
        )
    },
)

SITE_ID = 1

ACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'username'
ACCOUNT_LOGOUT_ON_GET = True


MEDIA_URL = '/media/'
MEDIA_ROOT = devops_config['media_root'].text

CONTENT_TYPES = ['image', 'audio']
MAX_UPLOAD_SIZE = 10485760


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'request_logging.middleware.LoggingMiddleware',
    'admin_reorder.middleware.ModelAdminReorder',

]

ROOT_URLCONF = 'games.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            # 'loaders': [
            #     'django.template.loaders.filesystem.Loader',
            #     'django.template.loaders.app_directories.Loader',
            #     'admin_tools.template_loaders.Loader',
            # ],
        },
    },
]


WSGI_APPLICATION = 'games.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases
DATABASES = {
    'default': dj_database_url.parse(devops_config['connections']['pgsql']['uri'].text)
}

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 4,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'games.validators.ComplexPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/
LANGUAGE_CODE = 'ru-ru'
# LANGUAGE_CODE = 'en-en'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = devops_config['static_root'].text

if DEBUG:
    INSTALLED_APPS += [
        'debug_toolbar',
        'django_extensions',
    ]

    MIDDLEWARE += [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ]
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'django.db.backends': {
                'handlers': ['console'],
                'level': 'DEBUG',
            },
            'django.request': {
                'handlers': ['console'],
                'level': 'DEBUG',  # change debug level as appropiate
                'propagate': False,
            },
            'factory': {  # чтобы factory-boy не мусорил в вывод
                'handlers': ['console'],
                'level': 'INFO',
            },
            '': {
                'handlers': ['console'],
                'level': 'DEBUG',
            }
        },
    }
else:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default_format': {
                'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(request_id)s %(message)s"
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'default_format',
            },
            'file': {
                'class': 'logging.handlers.WatchedFileHandler',
                'formatter': 'default_format',
                'filename': '/var/log/games/games.log',
            },
        },
        'loggers': {
            'django.request': {
                'handlers': ['console', 'file'],
                'level': 'INFO',  # change debug level as appropiate
                'propagate': False,
            },
            'celery.task': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
            },
            '': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
            }
        },
    }

# Celery
CELERY_BROKER_URL = devops_config['connections']['celery']['uri'].text
CELERY_WORKER_HIJACK_ROOT_LOGGER = False


# def implicit():
#     from google.cloud import storage
#
#     # If you don't specify credentials when constructing the client, the
#     # client library will look for credentials in the environment.
#     storage_client = storage.Client(credentials=GS_CREDENTIALS)
#
#     # Make an authenticated API request
#     buckets = list(storage_client.list_buckets())
#     print(buckets)
#
# implicit()