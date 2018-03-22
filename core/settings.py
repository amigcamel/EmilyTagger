import os
import logging

import coloredlogs

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


coloredlogs.ColoredStreamHandler.default_severity_to_style['INFO'] = {
    'underline': True}
coloredlogs.ColoredStreamHandler.default_severity_to_style['WARNING'] = {
    'inverse': True}
coloredlogs.install(level=logging.DEBUG)

SECRET_KEY = 'agth-neb+eg#m&21wukpdjti5d%ou&sb=oxi(mndn)f=2$3q!*'

DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['140.112.147.131']

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

INSTALLED_APPS_LOCAL = (
    'annotator',
    'utility',
    'analysis',
    'account',
)

INSTALLED_APPS += INSTALLED_APPS_LOCAL

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'core.urls'

WSGI_APPLICATION = 'core.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Taipei'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static_lopeanno/'
STATICFILES_DIRS = (
    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'),
)

TEMPLATE_DIRS = tuple([os.path.join(BASE_DIR, app, 'templates')
                       for app in INSTALLED_APPS_LOCAL])
TEMPLATE_DIRS += (os.path.join(BASE_DIR, 'templates'), )

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.contrib.auth.context_processors.auth',
)


LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'propagate': False,
            'level': 'ERROR',
        }
    },
}

RLITE_DB_PATH = os.path.join(BASE_DIR, 'dbs')
USER_DB_PATH = os.path.join(BASE_DIR, 'user_dbs', '%s.db')

TAG_PATH = os.path.join(BASE_DIR, 'annotator', 'ref.json')
