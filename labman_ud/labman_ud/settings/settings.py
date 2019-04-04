# -*- coding: utf-8 -*-

import os

from unipath import Path

PROJECT_DIR = Path(__file__).ancestor(3)


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', '')


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = eval(os.environ.get('DEBUG', 'False'))

ALLOWED_HOSTS = eval(os.environ.get('ALLOWED_HOSTS', '[]'))

ADMINS = (
    eval(os.environ.get('ADMINS', '()'))
)


# Uploaded file permissions (allow to third parties download documents from web)
FILE_UPLOAD_PERMISSIONS = 0o644

# Application definition

INSTALLED_APPS = (
    # django admin templates
    'bootstrap_admin',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # Re-usable applications
    'debug_toolbar',
    'django_extensions',
    'logentry_admin',
    'redactor',
    'django_ajax',

    # Custom applications with data models
    'entities.events',
    'entities.funding_programs',
    'entities.news',
    'entities.organizations',
    'entities.persons',
    'entities.projects',
    'entities.publications',
    'entities.utils',
    'entities.datasets',

    'extractors.zotero',
    'labman_setup',
    'maintenance_tasks',
    'management',
    'template_tags',

    # Custom applications for data consulting only
    'charts',

    # Extension packages
    'django_cleanup',
    'pagination_bootstrap',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',

    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'pagination_bootstrap.middleware.PaginationMiddleware',
)

ROOT_URLCONF = 'labman_ud.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            PROJECT_DIR.child('templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'labman_ud.context_processors.global_vars',
            ],
        },
    },
]

BOOTSTRAP_ADMIN_SIDEBAR_MENU = False

WSGI_APPLICATION = 'labman_ud.wsgi.application'


# Database

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DATABASE_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.environ.get('DATABASE_NAME', 'labman'),
        'USER': os.environ.get('DATABASE_USER', 'labman'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD', 'labman'),
        'HOST': os.environ.get('DATABASE_HOST', 'localhost'),
        'PORT': os.environ.get('DATABASE_PORT', '5432'),
    }
}


# Internationalization

LANGUAGE_CODE = 'en-EN'

TIME_ZONE = 'Europe/Madrid'

USE_I18N = False

USE_L10N = False

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    PROJECT_DIR.child('static'),
)

MEDIA_URL = '/media/'

MEDIA_ROOT = '/src/labman_ud/labman_ud/media'

STATIC_ROOT = PROJECT_DIR.child('collected_static')


# Pagination: https://pypi.python.org/pypi/django-bootstrap-pagination/

PAGINATION_DEFAULT_PAGINATION = 10

PAGINATION_DEFAULT_WINDOW = 3

PAGINATION_INVALID_PAGE_RAISES_404 = True

# Name similarity

DEFAULT_THRESHOLD_RATIO = 60

# Email settings
EMAIL_HOST = os.environ.get('EMAIL_HOST', '')
EMAIL_PORT = os.environ.get('EMAIL_PORT', 25)
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = eval(os.environ.get('EMAIL_USE_TLS', 'False'))
EMAIL_USE_SSL = eval(os.environ.get('EMAIL_USE_SSL', 'False'))
EMAIL_TIMEOUT = os.environ.get('EMAIL_TIMEOUT', None)


DEFAULT_EMAIL_SENDER = os.environ.get('DEFAULT_EMAIL_SENDER', '')
NEWS_UPDATES_RECEIVERS = eval(os.environ.get('NEWS_UPDATES_RECEIVERS', ''))

# RDF settings

ENABLE_RDF_PUBLISHING = eval(os.environ.get('ENABLE_RDF_PUBLISHING', 'False'))

# Logging settings

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': """
[%(asctime)s] %(levelname)s
[%(name)s:%(lineno)s]
    %(message)s
            """,
            'datefmt': '%Y/%m/%d %H:%M:%S',
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        'compact': {
            'format': '[%(asctime)s] [%(levelname)s]\t%(message)s',
            'datefmt': '%Y/%m/%d %H:%M:%S'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'compact',
        },
        'mail_admins': {
            'level': 'WARNING',
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'maintenance_tasks': {
            'handlers': ['console', 'mail_admins'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'extractors.zotero': {
            'handlers': ['console', 'mail_admins'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
