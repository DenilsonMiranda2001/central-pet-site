from pathlib import Path
from urllib.parse import urlparse

from decouple import config, Csv
from django.core.exceptions import ImproperlyConfigured
import dj_database_url
import sentry_sdk

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = config('DEBUG', default=True, cast=bool)

SECRET_KEY = config('SECRET_KEY', default='')
if not SECRET_KEY and not DEBUG:
    raise ImproperlyConfigured('Defina SECRET_KEY no ambiente de produção.')
if not SECRET_KEY:
    SECRET_KEY = 'django-insecure-local-development-central-pet'

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='http://localhost:8000,http://127.0.0.1:8000',
    cast=Csv()
)
ENVIRONMENT = config('ENVIRONMENT', default='development')
RELEASE = config('RELEASE', default='local')
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=not DEBUG, cast=bool)
USE_X_FORWARDED_HOST = config('USE_X_FORWARDED_HOST', default=not DEBUG, cast=bool)
TRUST_PROXY_SSL_HEADER = config('TRUST_PROXY_SSL_HEADER', default=not DEBUG, cast=bool)
if TRUST_PROXY_SSL_HEADER:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'core',
    'products',
    'services',
    'panel',
]

LOGIN_URL = '/painel/login/'
LOGIN_REDIRECT_URL = '/painel/'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'central_pet.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.store_config',
            ],
        },
    },
]

WSGI_APPLICATION = 'central_pet.wsgi.application'

DATABASE_URL = config('DATABASE_URL', default='')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=not DEBUG,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Media persistente via Cloudflare R2.
# Em desenvolvimento, R2 pode ficar desativado e o Django usa MEDIA_ROOT local.
# Em produção, habilite R2_ENABLED=true para que uploads feitos pelo admin sobrevivam aos deploys.
R2_ENABLED = config('R2_ENABLED', default=False, cast=bool)
if R2_ENABLED:
    R2_ACCOUNT_ID = config('R2_ACCOUNT_ID')
    R2_ACCESS_KEY_ID = config('R2_ACCESS_KEY_ID')
    R2_SECRET_ACCESS_KEY = config('R2_SECRET_ACCESS_KEY')
    R2_BUCKET_NAME = config('R2_BUCKET_NAME')
    R2_ENDPOINT_URL = config(
        'R2_ENDPOINT_URL',
        default=f'https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com'
    ).rstrip('/')
    R2_PUBLIC_BASE_URL = config('R2_PUBLIC_BASE_URL').strip().rstrip('/')

    # django-storages espera somente o host em custom_domain, sem https://.
    parsed_r2_public_url = urlparse(
        R2_PUBLIC_BASE_URL
        if '://' in R2_PUBLIC_BASE_URL
        else f'https://{R2_PUBLIC_BASE_URL}'
    )
    R2_PUBLIC_DOMAIN = parsed_r2_public_url.netloc or parsed_r2_public_url.path
    if not R2_PUBLIC_DOMAIN:
        raise ImproperlyConfigured('R2_PUBLIC_BASE_URL precisa apontar para o domínio público do bucket R2.')

    MEDIA_URL = f'https://{R2_PUBLIC_DOMAIN}/'

    STORAGES = {
        'default': {
            'BACKEND': 'storages.backends.s3.S3Storage',
            'OPTIONS': {
                'bucket_name': R2_BUCKET_NAME,
                'endpoint_url': R2_ENDPOINT_URL,
                'access_key': R2_ACCESS_KEY_ID,
                'secret_key': R2_SECRET_ACCESS_KEY,
                'region_name': 'auto',
                'signature_version': 's3v4',
                'default_acl': None,
                'file_overwrite': False,
                'querystring_auth': False,
                'custom_domain': R2_PUBLIC_DOMAIN,
                'url_protocol': 'https:',
                'object_parameters': {
                    'CacheControl': 'public, max-age=86400',
                },
            },
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
        },
    }
else:
    STORAGES = {
        'default': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
        },
    }

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SENTRY_DSN = config('SENTRY_DSN', default='')
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=ENVIRONMENT,
        release=RELEASE,
        traces_sample_rate=config('SENTRY_TRACES_SAMPLE_RATE', default=0.05, cast=float),
        send_default_pii=False,
    )

# Admin personalizado
ADMIN_SITE_HEADER = "In Dog - We trust Pet Boutique — Painel Administrativo"
ADMIN_SITE_TITLE = "In Dog - We trust Pet Boutique Admin"
ADMIN_INDEX_TITLE = "Gerenciamento da Loja"

# Segurança em produção
if not DEBUG:
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=31536000, cast=int)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = config('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True, cast=bool)
    SECURE_HSTS_PRELOAD = config('SECURE_HSTS_PRELOAD', default=False, cast=bool)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = False
