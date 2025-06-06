"""
Django settings for navyojan project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import sys
from pathlib import Path
import os
from datetime import timedelta
import firebase_admin
from firebase_admin import credentials
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

sys.path.extend(
    [
        str(BASE_DIR.parent / "ai"),
        str(BASE_DIR.parent / "logs"),
        str(BASE_DIR.parent / "tasks"),
        str(BASE_DIR.parent / "scripts"),
    ]
)

load_dotenv(os.path.join(BASE_DIR, ".env"))

from logs import logger

# URL for serving media files (locally stored PDFs)
MEDIA_URL = "/media/"

# Local directory where files will be stored
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


FIREBASE_CREDENTIALS = credentials.Certificate(
    {
        "type": os.environ["FIREBASE_TYPE"],
        "project_id": os.environ["FIREBASE_PROJECT_ID"],
        "private_key_id": os.environ["FIREBASE_PRIVATE_KEY_ID"],
        "private_key": os.environ["FIREBASE_PRIVATE_KEY"].replace("\\n", "\n"),
        "client_email": os.environ["FIREBASE_CLIENT_EMAIL"],
        "client_id": os.environ["FIREBASE_CLIENT_ID"],
        "auth_uri": os.environ["FIREBASE_AUTH_URI"],
        "token_uri": os.environ["FIREBASE_TOKEN_URI"],
        "auth_provider_x509_cert_url": os.environ[
            "FIREBASE_AUTH_PROVIDER_X509_CERT_URL"
        ],
        "client_x509_cert_url": os.environ["FIREBASE_CLIENT_X509_CERT_URL"],
    }
)

firebase_admin.initialize_app(FIREBASE_CREDENTIALS)

# Email configuration
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"  # For Gmail SMTP
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ["EMAIL_HOST_USER"]  # Your email address
EMAIL_HOST_PASSWORD = os.environ[
    "EMAIL_HOST_PASSWORD"
]  # Your email password or App Password


FERNET_KEY = os.environ["FERNET_KEY"]

CELERY_BROKER_URL = os.environ["RABBITMQ"]
CELERY_RESULT_BACKEND = (
    "db+postgresql://{user}:{password}@{host}:{port}/{database}".format(
        user=os.environ["POSTGRES_USERNAME"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        database=os.environ["POSTGRES_DATABASE"],
    )
)

CELERY_TASK_ROUTES = {
    "tasks.send_email.send_email_task": {"queue": "default-queue"},
    "tasks.send_email.send_text_task": {"queue": "default-queue"},
    "backend.celery.debug_task": {"queue": "default-queue"},
    # Add more tasks as needed
}


CELERY_TASK_SERIALIZER = "pickle"
CELERY_RESULT_SERIALIZER = "pickle"
CELERY_ACCEPT_CONTENT = ["pickle"]
CELERY_TASK_IGNORE_RESULT = False
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_DEFAULT_QUEUE = "default-queue"

MSG_AUTH = os.environ["MSG_AUTH"]


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-x$im$wy@jq*%&rjoccud*3%m9w)qo6vug+a@50v@y7##598q@+"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


# Application definition

INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "userapp",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",
    "corsheaders",
    "drf_yasg",
    "celery",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# CORS settings


# Important: When using CORS_ALLOW_CREDENTIALS, specify the exact origin


# Additional required headers
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    "http://34.66.194.53",  # Production frontend
    "http://localhost:3000",  # Next.js default
    "http://localhost:3001",  # Alternative Next.js port
    "http://localhost:5173",  # Vite default
    "http://localhost:8000",  # Django development server
    "http://localhost:8080",  # Alternative backend port
    "http://127.0.0.1:3000",  # localhost alternative
    "http://127.0.0.1:3001",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8080",
]

# Optional: If you need regex patterns for dynamic subdomains or ports
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^http://localhost:\d+$",
    r"^http://127\.0\.0\.1:\d+$",
]

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

CORS_ALLOW_HEADERS = ["*"]
ALLOWED_HOSTS = ["*"]

# Add these specific response headers
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

ROOT_URLCONF = "navyojan.urls"


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

WSGI_APPLICATION = "navyojan.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases


# TO CONNECT TO THE DATABASE: RUN THE FOLLOWING COMMANDS IN THE TERMINAL
# psql -U postgres

logger.info(f'starting postgres db...... {os.environ["POSTGRES_DATABASE"]}')

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["POSTGRES_DATABASE"],
        "USER": os.environ["POSTGRES_USERNAME"],
        "PASSWORD": os.environ["POSTGRES_PASSWORD"],
        "HOST": os.environ["POSTGRES_HOST"],
        "PORT": os.environ["POSTGRES_PORT"],
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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


AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "userapp.authentication.custom_authentication.EmailModelBackend",
]

REFRESH_TOKEN_COOKIE_PATH = "/refresh-token"
REFRESH_TOKEN_COOKIE_MAX_AGE = timedelta(days=30)

SIMPLE_JWT = {
    "AUTH_HEADER_TYPES": ("Bearer",),
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),  # Access token lifetime
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),  # Refresh token lifetime
    "ROTATE_REFRESH_TOKENS": True,  # Issue a new refresh token with each refresh
    "BLACKLIST_AFTER_ROTATION": True,  # Blacklist the old refresh token after it is rotated
}

RAZOR_KEY_ID = os.environ["RAZOR_KEY_ID"]
RAZOR_KEY_SECRET = os.environ["RAZOR_KEY_SECRET"]


# REST_FRAMEWORK = {
#     # 'DEFAULT_FILTER_BACKENDS': [
#     #     'django_filters.rest_framework.DjangoFilterBackend'
#     # ],
#     # 'DEFAULT_AUTHENTICATION_CLASSES': [
#     #     'userapp.google_authentication.FirebaseAuthentication',
#     #     'rest_framework_simplejwt.authentication.JWTAuthentication',
#     #     'rest_framework.authentication.BasicAuthentication',
#     # ],
#     # 'DEFAULT_PERMISSION_CLASSES': [
#     #     'rest_framework.permissions.IsAuthenticated',
#     # ],
# }


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# CORS settings with credentials

