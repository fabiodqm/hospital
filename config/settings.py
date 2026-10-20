import os
from pathlib import Path

from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

_render_environment = bool(os.getenv('RENDER') or os.getenv('RENDER_EXTERNAL_HOSTNAME'))
DEBUG = os.getenv('DEBUG', 'False' if _render_environment else 'True').lower() in {'1', 'true', 'yes', 'on'}
SECRET_KEY = os.getenv('SECRET_KEY', '')
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = 'local-development-only-insecure-key-change-me'
    else:
        raise ImproperlyConfigured('SECRET_KEY precisa estar configurada no ambiente de produção.')

ALLOWED_HOSTS = [h.strip() for h in os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',') if h.strip()]
RENDER_EXTERNAL_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME', '').strip()
if RENDER_EXTERNAL_HOSTNAME and RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
CSRF_TRUSTED_ORIGINS = [h.strip() for h in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',') if h.strip()]
if RENDER_EXTERNAL_HOSTNAME:
    _render_origin = f'https://{RENDER_EXTERNAL_HOSTNAME}'
    if _render_origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(_render_origin)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'hospital',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'hospital.middleware.SecurityHeadersMiddleware',
    'hospital.middleware.LoginRateLimitMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
if not DEBUG:
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

ROOT_URLCONF = 'config.urls'

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
                'hospital.context_processors.hospital_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

DATABASE_URL = os.getenv('DATABASE_URL', '').strip()
if DATABASE_URL:
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=not DEBUG,
        )
    }
else:
    if not DEBUG:
        raise ImproperlyConfigured('DATABASE_URL precisa apontar para o PostgreSQL de produção; SQLite não é permitido com DEBUG=False.')
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
TIME_ZONE = os.getenv('HOSPITAL_TIME_ZONE', 'America/Sao_Paulo')
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []
WHITENOISE_USE_FINDERS = os.getenv('WHITENOISE_USE_FINDERS', 'False' if not DEBUG else 'True').lower() in {'1', 'true', 'yes', 'on'}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_STORAGE = os.getenv('MEDIA_STORAGE', 'local').strip().lower()
if MEDIA_STORAGE == 'supabase':
    _s3_required = {
        'SUPABASE_S3_ENDPOINT_URL': os.getenv('SUPABASE_S3_ENDPOINT_URL', '').strip(),
        'SUPABASE_S3_REGION': os.getenv('SUPABASE_S3_REGION', '').strip(),
        'SUPABASE_S3_BUCKET': os.getenv('SUPABASE_S3_BUCKET', '').strip(),
        'SUPABASE_S3_ACCESS_KEY_ID': os.getenv('SUPABASE_S3_ACCESS_KEY_ID', '').strip(),
        'SUPABASE_S3_SECRET_ACCESS_KEY': os.getenv('SUPABASE_S3_SECRET_ACCESS_KEY', '').strip(),
    }
    _s3_missing = [name for name, value in _s3_required.items() if not value]
    if _s3_missing:
        raise ImproperlyConfigured('Armazenamento Supabase S3 incompleto. Configure: ' + ', '.join(_s3_missing))
    if not _s3_required['SUPABASE_S3_ENDPOINT_URL'].startswith('https://'):
        raise ImproperlyConfigured('SUPABASE_S3_ENDPOINT_URL deve usar HTTPS em produção.')
    STORAGES = {
        'default': {
            'BACKEND': 'storages.backends.s3.S3Storage',
            'OPTIONS': {
                'access_key': _s3_required['SUPABASE_S3_ACCESS_KEY_ID'],
                'secret_key': _s3_required['SUPABASE_S3_SECRET_ACCESS_KEY'],
                'bucket_name': _s3_required['SUPABASE_S3_BUCKET'],
                'endpoint_url': _s3_required['SUPABASE_S3_ENDPOINT_URL'],
                'region_name': _s3_required['SUPABASE_S3_REGION'],
                'addressing_style': 'path',
                'signature_version': 's3v4',
                'querystring_auth': True,
                'querystring_expire': 300,
                'file_overwrite': False,
                'default_acl': None,
            },
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
        },
    }
elif MEDIA_STORAGE == 'local':
    STORAGES = {
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
    }
else:
    raise ImproperlyConfigured('MEDIA_STORAGE deve ser local ou supabase.')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

HOSPITAL_NAME = 'Centro Médico SHINE'
HOSPITAL_PRIMARY_COLOR = os.getenv('HOSPITAL_PRIMARY_COLOR', '#22c55e')

SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY', '')


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'shine-cache',
    }
}

SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = not DEBUG
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
SECURE_REFERRER_POLICY = 'same-origin'
SECURE_BROWSER_XSS_FILTER = True
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 8 * 1024 * 1024

DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID', '')
DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET', '')
DISCORD_REDIRECT_URI = os.getenv('DISCORD_REDIRECT_URI', '')
DISCORD_GUILD_ID = os.getenv('DISCORD_GUILD_ID', '')
DISCORD_OAUTH_ENABLED = os.getenv('DISCORD_OAUTH_ENABLED', 'False').lower() in {'1', 'true', 'yes', 'on'}
