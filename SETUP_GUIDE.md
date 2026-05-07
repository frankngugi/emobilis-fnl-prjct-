# RGC Church Management System – Complete Setup & Deployment Guide

**Redeemed Gospel Church Nyahururu**  
Stack: Django 6.0.5 · Python 3.14 · SQLite (dev) / PostgreSQL (prod)

---

## TABLE OF CONTENTS
1. [Run Locally (Development)](#1-run-locally)
2. [Phone OTP via Twilio (FREE trial)](#2-phone-otp-twilio)
3. [Email Notifications (FREE – Gmail SMTP)](#3-email-gmail-smtp)
4. [SMS Notifications – Africa's Talking (FREE sandbox)](#4-sms-africas-talking)
5. [M-Pesa Payments (Daraja API – FREE)](#5-mpesa-daraja-api)
6. [Deploy to Production (FREE – Railway)](#6-deploy-railway)
7. [Alternative Free Hosts](#7-alternative-hosts)
8. [Production Checklist](#8-production-checklist)
9. [Default Admin Credentials](#9-admin-credentials)

---

## 1. Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Apply database migrations
python manage.py migrate

# Load default hymns
python manage.py load_hymns

# Create admin user (if first time)
python manage.py createsuperuser

# Start the server
python manage.py runserver
```

Open: http://127.0.0.1:8000  
Admin panel: http://127.0.0.1:8000/admin/  
Default admin: username=`admin` password=`RGCAdmin2024!`

---

## 2. Phone OTP – Twilio (FREE Trial)

**What you already have:** Twilio credentials are already in `msys/.env`.  
**Free tier:** $15.50 trial credit, ~150 SMS messages.

### Steps:
1. Log in to https://www.twilio.com/console
2. Go to **Verify** → **Services** → **Create Service**
   - Name: "RGC Church"
   - Copy the **Service SID** (starts with `VA...`)
3. Note your **Account SID** and **Auth Token** from the dashboard
4. Update `msys/.env`:
   ```
   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   TWILIO_AUTH_TOKEN=your_auth_token_here
   TWILIO_VERIFY_SERVICE_SID=VAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
5. Install Twilio:
   ```bash
   pip install twilio
   ```
6. To test: Register on the site → go to `/send-phone-otp/` → enter your number

### Upgrade to paid:
- Twilio pay-as-you-go: ~$0.0065/SMS to Kenya (very cheap)
- No monthly fees, only pay what you use

---

## 3. Email Notifications – Gmail SMTP (FREE)

**Cost:** FREE (up to 500 emails/day via Gmail)

### Steps:
1. Go to your Gmail → **Settings** → **Security** → **2-Step Verification** (enable it)
2. Then go to **App Passwords**: https://myaccount.google.com/apppasswords
3. Select **Mail** + **Windows Computer** → Generate → Copy the 16-character password
4. Open `msys/settings.py` and update the email section:
   ```python
   EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
   EMAIL_HOST = 'smtp.gmail.com'
   EMAIL_PORT = 587
   EMAIL_USE_TLS = True
   EMAIL_HOST_USER = 'your.gmail@gmail.com'
   EMAIL_HOST_PASSWORD = 'your16charapppassword'
   DEFAULT_FROM_EMAIL = 'Redeemed Gospel Church <your.gmail@gmail.com>'
   ```
5. Test it:
   ```bash
   python manage.py shell
   >>> from django.core.mail import send_mail
   >>> send_mail('Test', 'Hello from RGC!', 'your@gmail.com', ['recipient@email.com'])
   ```

### Alternative FREE email services (higher limits):
| Service | Free Emails/Day | Sign Up |
|---------|----------------|---------|
| **Brevo (Sendinblue)** | 300/day | https://www.brevo.com |
| **Mailgun** | 100/day | https://www.mailgun.com |
| **Resend** | 100/day | https://resend.com |

For Brevo, use SMTP settings from their dashboard (same format as Gmail above).

---

## 4. SMS Notifications – Africa's Talking (FREE Sandbox)

**Better for Kenya than Twilio** – local support, works with Safaricom/Airtel/Telkom.  
**Free sandbox:** Unlimited test SMS (no real delivery).  
**Paid:** ~KES 1.20 per SMS to Safaricom.

### Steps:
1. Sign up: https://africastalking.com
2. Create an app in the dashboard
3. Get your **Username** and **API Key**
4. Install:
   ```bash
   pip install africastalking
   ```
5. Add to `msys/.env`:
   ```
   AT_USERNAME=sandbox    # Use 'sandbox' for testing, your real username for production
   AT_API_KEY=your_api_key_here
   ```
6. Add to `msys/settings.py`:
   ```python
   AT_USERNAME = os.environ.get('AT_USERNAME', 'sandbox')
   AT_API_KEY = os.environ.get('AT_API_KEY', '')
   AT_SENDER_ID = 'RGC'  # Your branded sender ID (requires approval from AT)
   ```
7. To send SMS in views.py, add this helper function:
   ```python
   def send_sms_notification(phone, message):
       """Send SMS via Africa's Talking."""
       try:
           import africastalking
           africastalking.initialize(settings.AT_USERNAME, settings.AT_API_KEY)
           sms = africastalking.SMS
           response = sms.send(message, [phone], sender_id=settings.AT_SENDER_ID)
           return response
       except Exception as e:
           print(f"SMS failed: {e}")
           return None
   ```

### When to use:
- New member registration confirmation
- Event reminders 24h before
- Payment confirmation
- Role approval notifications

---

## 5. M-Pesa (Daraja API) – FREE

**Cost:** FREE to integrate; Safaricom charges the customer standard M-Pesa rates.

### Steps:
1. **Register as a developer:**  
   Go to https://developer.safaricom.co.ke → Sign Up → Create an App

2. **Get sandbox credentials** (for testing):
   - Consumer Key
   - Consumer Secret
   - Test Shortcode: `174379` (Safaricom provides this)
   - Test Passkey: `bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919`
   - Test phone: `254708374149` (Safaricom sandbox test number)

3. **Add to `msys/.env`:**
   ```
   MPESA_CONSUMER_KEY=your_consumer_key
   MPESA_CONSUMER_SECRET=your_consumer_secret
   MPESA_SHORTCODE=174379
   MPESA_PASSKEY=bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919
   MPESA_CALLBACK_URL=https://yourdomain.com/mpesa/callback/
   ```

4. **Test payment flow:**
   - Go to http://127.0.0.1:8000/contribute
   - Enter the test phone: `0708374149`
   - Enter any amount (minimum KES 10)
   - You'll receive an STK Push on the test simulator

5. **Go live (production):**
   - Apply for a Paybill/Till number from Safaricom
   - Submit your app for review on the Daraja portal
   - Update `MPESA_ENVIRONMENT = 'production'` in settings.py
   - Update credentials with production values

### Callback URL requirement:
M-Pesa requires a **public HTTPS URL** to send payment confirmations.  
For local testing, use **ngrok**:
```bash
pip install pyngrok
ngrok http 8000
# Copy the https URL and add /mpesa/callback/ to it
```

---

## 6. Deploy to Production – Railway (FREE $5/month credit)

**Railway** is the easiest free hosting for Django apps.

### Steps:

#### 6.1 Prepare the project

Install production packages:
```bash
pip install gunicorn whitenoise psycopg2-binary
pip freeze > requirements.txt
```

Create `Procfile` in the project root:
```
web: gunicorn msys.wsgi:application --bind 0.0.0.0:$PORT
```

Create `runtime.txt`:
```
python-3.14.4
```

#### 6.2 Production settings

In `msys/settings.py`, set these for production:
```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.railway.app', 'yourdomain.com']

# WhiteNoise for static files
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ← add after SecurityMiddleware
    ...
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# PostgreSQL (Railway provides this)
DATABASES = {
    'default': dj_database_url.config(default=os.environ.get('DATABASE_URL'))
}
```

Install `dj-database-url`:
```bash
pip install dj-database-url
```

Collect static files:
```bash
python manage.py collectstatic --noinput
```

#### 6.3 Deploy to Railway

1. Install Railway CLI: https://docs.railway.app/develop/cli
2. Push to GitHub first (or use Railway's direct deploy)
3. Commands:
   ```bash
   railway login
   railway init
   railway up
   ```
4. Add environment variables in Railway dashboard:
   - `SECRET_KEY` (generate a new one)
   - `DEBUG=False`
   - `ALLOWED_HOSTS=yourdomain.railway.app`
   - `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_VERIFY_SERVICE_SID`
   - `MPESA_CONSUMER_KEY`, `MPESA_CONSUMER_SECRET`, etc.
   - `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`

5. Run migrations on Railway:
   ```bash
   railway run python manage.py migrate
   railway run python manage.py createsuperuser
   railway run python manage.py load_hymns
   ```

---

## 7. Alternative Free Hosts

| Platform | Free Tier | Notes |
|----------|-----------|-------|
| **Railway** | $5/month credit | Easiest, PostgreSQL included |
| **Render** | 512MB RAM | Sleeps after 15 min inactive |
| **PythonAnywhere** | 1 web app | Good for Django, limited bandwidth |
| **Fly.io** | 3 shared VMs | More complex setup |
| **Koyeb** | 2 services | Fast cold starts |

### Render deployment (alternative):
```bash
# Create render.yaml in project root:
services:
  - type: web
    name: rgc-cms
    env: python
    buildCommand: pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
    startCommand: gunicorn msys.wsgi:application
    envVars:
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: false
```

---

## 8. Production Checklist

Before going live, complete these steps:

### Security
- [ ] Change `SECRET_KEY` to a new random value (never use the dev key)
- [ ] Set `DEBUG = False`
- [ ] Set `ALLOWED_HOSTS` to your actual domain
- [ ] Enable HTTPS (Railway/Render do this automatically)
- [ ] Set `SECURE_SSL_REDIRECT = True`
- [ ] Set `SESSION_COOKIE_SECURE = True`
- [ ] Set `CSRF_COOKIE_SECURE = True`

### Database
- [ ] Switch from SQLite to PostgreSQL (Railway/Render provide free PostgreSQL)
- [ ] Run `python manage.py migrate` on the production database
- [ ] Create a superuser: `python manage.py createsuperuser`
- [ ] Load hymns: `python manage.py load_hymns`

### Static Files
- [ ] Run `python manage.py collectstatic`
- [ ] Install and configure WhiteNoise (already in middleware above)

### Services
- [ ] Configure Gmail SMTP (or Brevo) for email
- [ ] Activate Twilio Verify for phone OTP
- [ ] Get M-Pesa Daraja live credentials from Safaricom
- [ ] Set M-Pesa callback URL to your production domain
- [ ] Set `MPESA_ENVIRONMENT = 'production'`

### Content
- [ ] Update church contact info in `index.html` (phone, email, address)
- [ ] Upload church logo to `static/assets/img/img/`
- [ ] Create initial church groups (Admin → Create Group)
- [ ] Post your first announcement
- [ ] Add upcoming events

### Admin
- [ ] Change the default admin password (admin/RGCAdmin2024!)
- [ ] Create manager accounts for church leaders
- [ ] Set up church groups and invite members to join

---

## 9. Admin Credentials

| | Details |
|-|---------|
| **Admin URL** | http://yourdomain.com/admin/ |
| **Default username** | `admin` |
| **Default password** | `RGCAdmin2024!` |
| **RGC Admin portal** | http://yourdomain.com/adminn/ |

> **IMPORTANT:** Change the admin password immediately after first login!  
> Go to Admin Portal → Manage Users → click Edit on `admin` → set new password.

---

## Quick Command Reference

```bash
# Start development server
python manage.py runserver

# Create new admin user
python manage.py createsuperuser

# Apply database migrations
python manage.py migrate

# Load hymns data
python manage.py load_hymns

# Collect static files (production)
python manage.py collectstatic

# Open Django shell (for debugging)
python manage.py shell

# Check for configuration errors
python manage.py check --deploy

# Generate a new SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

*Redeemed Gospel Church Nyahururu – "Where everybody is somebody"*
