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

SECRET_KEY = os.environ.get('SECRET_KEY', 'change-me-before-production-use')

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# Tell Django it's behind Render's HTTPS proxy — fixes CSRF Origin: null issue
# caused by Django issuing a 301 redirect when it doesn't know it's already on HTTPS.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Django 4.0+ requires trusted origins for HTTPS POST requests
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        'CSRF_TRUSTED_ORIGINS',
        'https://rgc-nyahururu-cms.onrender.com'
    ).split(',')
    if origin.strip()
]

# Production security settings (auto-enabled when DEBUG=False)
if not DEBUG:
    SECURE_SSL_REDIRECT = False  # Render's proxy handles HTTPS — don't double-redirect
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
    'cloudinary',
    'cloudinary_storage',
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
                'myapp.context_processors.site_settings',
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

# ── Cloudinary — Media / File Storage ────────────────────────────────────────
# Uploads (images, videos, files) are stored on Cloudinary in production.
# Locally, files fall back to MEDIA_ROOT when CLOUDINARY_CLOUD_NAME is not set.
CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME', '')
CLOUDINARY_API_KEY    = os.environ.get('CLOUDINARY_API_KEY', '')
CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET', '')

if CLOUDINARY_CLOUD_NAME:
    import cloudinary
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET,
        secure=True,
    )
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': CLOUDINARY_CLOUD_NAME,
        'API_KEY':    CLOUDINARY_API_KEY,
        'API_SECRET': CLOUDINARY_API_SECRET,
    }
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    MEDIA_URL = f'https://res.cloudinary.com/{CLOUDINARY_CLOUD_NAME}/'
else:
    # Local development — files stored in /media/
    MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── WhatsApp Business Cloud API (Meta) ───────────────────────────────────
# Sign up: business.facebook.com → WhatsApp → Get Started
# Free: 1,000 conversations/month | No cost for receiving messages
WHATSAPP_ACCESS_TOKEN = os.environ.get('WHATSAPP_ACCESS_TOKEN', '')
WHATSAPP_PHONE_NUMBER_ID = os.environ.get('WHATSAPP_PHONE_NUMBER_ID', '')
WHATSAPP_VERIFY_TOKEN = os.environ.get('WHATSAPP_VERIFY_TOKEN', 'rgc_webhook_verify')

# ── Twilio — Phone OTP ────────────────────────────────────────────────────
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
TWILIO_VERIFY_SERVICE_SID = os.environ.get('TWILIO_VERIFY_SERVICE_SID', '')

# ── Email — Gmail SMTP ────────────────────────────────────────────────────
_email_password = os.environ.get('EMAIL_HOST_PASSWORD', '')
if _email_password and _email_password != 'PASTE_YOUR_16_CHAR_APP_PASSWORD_HERE':
    # Real Gmail credentials found → use SMTP
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_TIMEOUT = 8  # fail fast — don't let SMTP hang and kill the gunicorn worker
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'frneltp@gmail.com')
    EMAIL_HOST_PASSWORD = _email_password
    DEFAULT_FROM_EMAIL = f"Redeemed Gospel Church <{EMAIL_HOST_USER}>"
else:
    # No credentials yet → print emails to terminal (safe for development)
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    EMAIL_HOST_USER = 'frneltp@gmail.com'
    DEFAULT_FROM_EMAIL = 'Redeemed Gospel Church <frneltp@gmail.com>'

# ── Brevo — Email API primary (300/day free, single-sender, no domain needed) ─
BREVO_API_KEY = os.environ.get('BREVO_API_KEY', '')
BREVO_SENDER_NAME = os.environ.get('BREVO_SENDER_NAME', 'RGC Nyahururu')
BREVO_SENDER_EMAIL = os.environ.get('BREVO_SENDER_EMAIL', 'frneltp@gmail.com')

# ── Resend — Email API fallback (requires verified domain to reach any inbox) ──
RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')
RESEND_FROM_EMAIL = os.environ.get('RESEND_FROM_EMAIL', 'RGC Nyahururu <onboarding@resend.dev>')

# ── Africa's Talking — SMS Kenya ─────────────────────────────────────────
AT_USERNAME = os.environ.get('AT_USERNAME', 'sandbox')
AT_API_KEY = os.environ.get('AT_API_KEY', '')
AT_SENDER_ID = 'RGC'   # Requires AT approval for custom sender ID; leave blank to use default

# ── M-Pesa Daraja — Buy Goods (Till Number) ───────────────────────────────
MPESA_ENVIRONMENT = os.environ.get('MPESA_ENVIRONMENT', 'sandbox')
MPESA_CONSUMER_KEY = os.environ.get('MPESA_CONSUMER_KEY', '')
MPESA_CONSUMER_SECRET = os.environ.get('MPESA_CONSUMER_SECRET', '')
MPESA_TILL_NUMBER = os.environ.get('MPESA_TILL_NUMBER', '174379')   # Sandbox till
MPESA_PASSKEY = os.environ.get('MPESA_PASSKEY', 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919')
MPESA_CALLBACK_URL = os.environ.get('MPESA_CALLBACK_URL', 'https://yourdomain.com/mpesa/callback/')

# Church info
CHURCH_NAME = 'Redeemed Gospel Church Nyahururu'
CHURCH_SHORT_NAME = 'RGC Nyahururu'
CHURCH_LOCATION = 'Nyahururu, Laikipia County, Kenya'
CHURCH_PHONE = '+254 712 760 740'
CHURCH_EMAIL = 'info@redeemedgospelchurch.org'

# Django 6.0 + Python 3.14 are natively compatible — no patches needed.
