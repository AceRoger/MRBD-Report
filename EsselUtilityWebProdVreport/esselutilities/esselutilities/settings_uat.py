"""
Django settings for esselutilities project.

Generated by 'django-admin startproject' using Django 1.8.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '87)-hj+uhop(n+=$migr6bbhq-v)20gnapq93y^_0yiuk!b&gj'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# GET_ROUTEMASTER_URL = "http://soatest.utility.esselgroup.com:8002/soa-infra/services/FieldMobility/getRouteMaster/getRouteMasterMediator_ep?WSDL"
# GET_ROUTEDETAILS_URL = "http://soatest.utility.esselgroup.com:8002/soa-infra/services/FieldMobility/getRouteDetails/getRouteDetails_ep?WSDL"
# UPLOADB30_URL = "http://soatest.utility.esselgroup.com:8002/soa-infra/services/FieldMobility/uploadMeterReading/uploadMeterReadingMediator_ep?WSDL"

# GET_ROUTEMASTER_URL = "http://soatest.utility.esselgroup.com:8002/soa-infra/services/FieldMobility/getRouteMaster!7.0*soa_4aab5b25-748a-49c4-b618-97281f4305f3/getRouteMasterMediator_ep?WSDL"
# GET_ROUTEDETAILS_URL = "http://soatest.utility.esselgroup.com:8002/soa-infra/services/FieldMobility/getRouteDetails!7.0*soa_79b0efd6-37fd-429a-8615-dfa5676f88c2/getRouteDetails_ep?WSDL"
# UPLOADB30_URL = "http://soatest.utility.esselgroup.com:8002/soa-infra/services/FieldMobility/uploadMeterReading!7.0*soa_e4f607aa-bb89-49a4-b1c5-9ae98e7fbe4d/uploadMeterReadingMediator_ep?WSDL"


GET_ROUTEMASTER_URL = "http://soatest.utility.esselgroup.com:8002/soa-infra/services/FieldMobility/getRouteMaster!7.0*soa_a66659f9-f20b-4bec-9a86-5c30b98ddb3a/getRouteMaster_ep?WSDL"
GET_ROUTEDETAILS_URL = "http://soatest.utility.esselgroup.com:8002/soa-infra/services/FieldMobility/getRouteDetails!7.0*soa_89b54a74-24d0-4f3d-a496-432ddda4ee9a/getRouteDetails_ep?WSDL"
UPLOADB30_URL = "http://soatest.utility.esselgroup.com:8002/soa-infra/services/FieldMobility/uploadMeterReading!7.0*soa_e4f607aa-bb89-49a4-b1c5-9ae98e7fbe4d/uploadMeterReadingMediator_ep?WSDL"



# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djcelery',
    'djkombu',
    'rest_framework',
    'rest_framework.authtoken',
    'push_notifications',
    'django_extensions',
    'adminapp',
    'consumerapp',
    'scheduleapp',
    'authenticateapp',
    'validationapp',
    'dispatch',
    'meterreaderapp',
    'uploadapp',
    'mrbdapp'
)



import djcelery
djcelery.setup_loader()
BROKER_URL="django://"

CELERY_IMPORTS = ('consumerapp.views.task','dispatch.tasks','uploadapp.views.task')
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
CELERY_ENABLE_UTC=True


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'esselutilities.mymiddleware.AutoLogout',
)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esselutilities.settings')

ROOT_URLCONF = 'esselutilities.urls'
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'
AUTO_LOGOUT_DELAY = 5
SESSION_EXPIRE_AT_BROWSER_CLOSE= True


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates')],
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

WSGI_APPLICATION = 'esselutilities.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'esselutilities_db',
#         'USER':'root',
#         'PASSWORD':'root',
#         'HOST':'localhost',
#         'PORT':'3306',
#     }
# }
#



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mrbd',
        'USER':'india',
        'PASSWORD':'2016',
        'HOST':'10.1.5.28',
        'PORT':'3306',
    }
}




# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'mrbd',
#         'USER':'bynry',
#         'PASSWORD':'2016',
#         'HOST':'10.1.1.224',
#         'PORT':'3306',
#     }
# }


# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'file': {
#             'level': 'DEBUG',
#             'class': 'logging.FileHandler',
#             'filename': BASE_DIR + '/debug.log',
#         },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['file'],
#             'level': 'DEBUG',
#             'propagate': True,
#         },
#     },
# }




# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = ('assets', BASE_DIR +'/static/',)

# Absolute path to the directory that holds media.
MEDIA_ROOT = os.path.join(BASE_DIR, "sitemedia")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://example.com/media/"
MEDIA_URL = '/sitemedia/'

#Job Cards per page count
JOB_CARDS_PER_PAGE = 100