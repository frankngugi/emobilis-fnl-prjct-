from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env safely (handles values with '=' in them)
_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(_env_path):
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith('#') and '=' in _line:
                _key, _, _val = _line.partition('=')
                _val = _val.strip('<>').strip()
                os.environ.setdefault(_key.strip(), _val)

SECRET_KEY = '4+aqjgn#-v8@m*jb$*u^+2ikf=)04zq3zi(mjgm-o5j6gnylkd'

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# Production security settings (auto-enabled when DEBUG=False)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    'myapp',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': True,
}

AUTH_USER_MODEL = 'myapp.CustomUser'
LOGIN_URL = '/login'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',   # serves static files in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ORIGIN_ALLOW_ALL = True

ROOT_URLCONF = 'msys.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'msys.wsgi.application'

# Database: SQLite locally, PostgreSQL on Railway/Render via DATABASE_URL env var
_database_url = os.environ.get('DATABASE_URL', '')
if _database_url:
    try:
        import dj_database_url
        DATABASES = {'default': dj_database_url.config(default=_database_url, conn_max_age=600)}
    except ImportError:
        pass  # dj-database-url not installed; fall through to SQLite
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Uncomment below and comment SQLite above to use MySQL in production:
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'rgc_cms',
#         'USER': 'rgc',
#         'PASSWORD': 'your_password_here',
#         'HOST': 'localhost',
#         'PORT': '3306',
#         'OPTIONS': {'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"},
#     }
# }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'    # collectstatic output for production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Twilio — for phone OTP verification
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
TWILIO_VERIFY_SERVICE_SID = os.environ.get('TWILIO_VERIFY_SERVICE_SID', '')

# Email — use console backend in dev; switch to SMTP for production
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@redeemedgospelchurch.org'

# For production SMTP (Gmail example):
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your@gmail.com'
# EMAIL_HOST_PASSWORD = 'your_app_password'

# M-Pesa Daraja API (replace with real credentials from Safaricom Developer Portal)
MPESA_ENVIRONMENT = 'sandbox'   # Change to 'production' for live
MPESA_CONSUMER_KEY = os.environ.get('MPESA_CONSUMER_KEY', 'your_consumer_key')
MPESA_CONSUMER_SECRET = os.environ.get('MPESA_CONSUMER_SECRET', 'your_consumer_secret')
MPESA_SHORTCODE = os.environ.get('MPESA_SHORTCODE', '174379')
MPESA_PASSKEY = os.environ.get('MPESA_PASSKEY', 'your_passkey')
MPESA_CALLBACK_URL = os.environ.get('MPESA_CALLBACK_URL', 'https://yourdomain.com/mpesa/callback/')

# Church info
CHURCH_NAME = 'Redeemed Gospel Church Nyahururu'
CHURCH_SHORT_NAME = 'RGC Nyahururu'
CHURCH_LOCATION = 'Nyahururu, Laikipia County, Kenya'
CHURCH_PHONE = '+254 712 760 740'
CHURCH_EMAIL = 'info@redeemedgospelchurch.org'

# Django 6.0 + Python 3.14 are natively compatible — no patches needed.
