import os
from pathlib import Path
from celery.schedules import crontab

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------
# Détection environnement & GDAL
# ---------------------------------------------------
if os.name == "nt":  # Windows
    VENV_BASE = os.environ.get("VIRTUAL_ENV", os.path.join(BASE_DIR, "venv"))
    OSGEO_PATH = os.path.join(VENV_BASE, "Lib", "site-packages", "osgeo")
    os.environ["PATH"] = OSGEO_PATH + ";" + os.environ["PATH"]
    os.environ["PROJ_LIB"] = os.path.join(OSGEO_PATH, "data", "proj")
    GDAL_LIBRARY_PATH = os.path.join(OSGEO_PATH, "gdal.dll")
else:  # Linux (Docker)
    GDAL_LIBRARY_PATH = os.environ.get("GDAL_LIBRARY_PATH", "/usr/lib/x86_64-linux-gnu/libgdal.so.36")

# ---------------------------------------------------
# Chemins projet
# ---------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------
# Détection environnement & GDAL
# ---------------------------------------------------

# ---------------------------------------------------
# Sécurité
# ---------------------------------------------------
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-o0$9+icstx@*4vthy_ufg^o0&q-5p-ydqf9oh_idqvn9xd3@wd")
DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",") if os.environ.get("DJANGO_ALLOWED_HOSTS") else []

# ---------------------------------------------------
# Applications installées
# ---------------------------------------------------
INSTALLED_APPS = [
    'daphne',
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.gis',
    'django.contrib.staticfiles',
    'location_field',
    'home',
    'authentication',
    'supervisor',
    'client',
]

# ---------------------------------------------------
# Middleware
# ---------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'authentication.middlewares.SeparateSessionMiddleware',
]

# ---------------------------------------------------
# WhiteNoise
# ---------------------------------------------------
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ---------------------------------------------------
# Templates
# ---------------------------------------------------
ROOT_URLCONF = 'project.urls'

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
        },
    },
]

# ---------------------------------------------------
# WSGI / ASGI
# ---------------------------------------------------
WSGI_APPLICATION = 'project.wsgi.application'
ASGI_APPLICATION = 'project.asgi.application'

# ---------------------------------------------------
# Channels (Redis)
# ---------------------------------------------------
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(os.environ.get("REDIS_HOST", "localhost"), 6379)],
        },
    },
}

# ---------------------------------------------------
# Base de données (PostGIS)
# ---------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.environ.get('POSTGRES_DB', 'fire_detection'),
        'USER': os.environ.get('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', '170320'),
        'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),  # local=localhost, docker=db
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
    }
}

# ---------------------------------------------------
# Auth
# ---------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ---------------------------------------------------
# Internationalisation
# ---------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Tunis'
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------
# Static & Media
# ---------------------------------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/img/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'img/')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---------------------------------------------------
# Email (en dur comme demandé)
# ---------------------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'mohamedhedigharbi101@gmail.com'
EMAIL_HOST_PASSWORD = 'pacesqcanahtmpks'

# ---------------------------------------------------
# Celery
# ---------------------------------------------------
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

CELERY_BEAT_SCHEDULE = {
    'predict_fwi_every_5min': {
        'task': 'supervisor.tasks.predict_fwi_for_data',
        'schedule': crontab(minute='*/5'),
    },
}

# ---------------------------------------------
# Base directory
# ---------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------
# Détection environnement
# ---------------------------------------------
ON_WINDOWS = os.name == "nt"
IN_DOCKER = os.environ.get("IN_DOCKER", "0") == "1"

# ---------------------------------------------
# GDAL
# ---------------------------------------------
if ON_WINDOWS:
    # Windows : modifier PATH et PROJ_LIB
    VENV_BASE = os.environ.get('VIRTUAL_ENV', '')
    os.environ['PATH'] = os.path.join(VENV_BASE, 'Lib\\site-packages\\osgeo') + ';' + os.environ['PATH']
    os.environ['PROJ_LIB'] = os.path.join(VENV_BASE, 'Lib\\site-packages\\osgeo\\data\\proj')
    GDAL_LIBRARY_PATH = r'C:\Users\moham\OneDrive\Desktop\smart_forest_watcher01\Forest_Fire_Prediction\venv\Lib\site-packages\osgeo\gdal.dll'
elif IN_DOCKER:
    # Docker (Linux) : GDAL installé via apt
    GDAL_LIBRARY_PATH = "/usr/lib/libgdal.so"

# ---------------------------------------------
# Clé secrète et debug
# ---------------------------------------------
SECRET_KEY = 'django-insecure-o0$9+icstx@*4vthy_ufg^o0&q-5p-ydqf9oh_idqvn9xd3@wd'
DEBUG = True
ALLOWED_HOSTS = ['*']

# ---------------------------------------------
# Applications installées
# ---------------------------------------------
INSTALLED_APPS = [
    'daphne',
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.gis',
    'django.contrib.staticfiles',
    'location_field',
    'home',
    'authentication',
    'supervisor',
    'client',
    'camera_management',
]

# ---------------------------------------------
# Middleware
# ---------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'authentication.middlewares.SeparateSessionMiddleware',
]

# ---------------------------------------------
# WhiteNoise static files
# ---------------------------------------------
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ---------------------------------------------
# URL et templates
# ---------------------------------------------
ROOT_URLCONF = 'project.urls'

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
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'
ASGI_APPLICATION = 'project.asgi.application'

# ---------------------------------------------
# Channels
# ---------------------------------------------
# Channels (WebSockets)
# ---------------------------------------------
if IN_DOCKER:
    CHANNEL_LAYERS = {
        'default': {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": ["redis://redis:6379/0"],  # Docker DB 0
            },
        },
    }
    CELERY_BROKER_URL = 'redis://redis:6379/0'
    CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
else:
    CHANNEL_LAYERS = {
        'default': {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": ["redis://localhost:6379/1"],  # Local DB 1
            },
        },
    }
    CELERY_BROKER_URL = 'redis://localhost:6379/1'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'

# ---------------------------------------------
# Base de données PostGIS
# ---------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'fire_detection',
        'USER': 'postgres',
        'PASSWORD': '123456789',
        'HOST': 'db' if IN_DOCKER else 'localhost',  # Docker utilise service 'db'
        'PORT': '5432',
    }
}

# ---------------------------------------------
# Celery
# ---------------------------------------------
#CELERY_BROKER_URL = f'redis://{REDIS_HOST}:6379/{REDIS_DB}'
#CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:6379/{REDIS_DB}'

CELERY_BEAT_SCHEDULE = {
    'predict_fwi_every_5min': {
        'task': 'supervisor.tasks.predict_fwi_for_data',
        'schedule': crontab(minute='*/5'),
    },
}

# ---------------------------------------------
# Internationalisation
# ---------------------------------------------
USE_I18N = True
USE_L10N = True
USE_TZ = True
LANGUAGE_CODE = 'en'

LANGUAGES = [
    ('en', 'English'),
    ('fr', 'French'),
    ('ar', 'Arabic'),
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

# ---------------------------------------------
# Static et media
# ---------------------------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/img/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'img/')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
#----------------------------------------------
#Email
#----------------------------------------------
# ---------------------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_USER', 'mohamedhedigharbi101@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD', 'pacesqcanahtmpks')






