# RGC Nyahururu CMS — Deployment Guide
# Last updated: May 2026

---

## QUICK ANSWER: DO I REMOVE THE API KEYS?

**NO. Do not remove or delete anything from your code.**

Here is exactly what happens with your secrets:

| File | Goes to GitHub? | What you do |
|------|----------------|-------------|
| `msys/.env` | ❌ NO — blocked by `.gitignore` | Leave it as-is. It stays on your laptop only. |
| `render.yaml` | ✅ YES — it has NO secrets (safe) | Nothing to change. |
| `msys/settings.py` | ✅ YES — it has NO real secrets (safe) | Nothing to change. |
| `rgc-mobile/constants/Api.ts` | ✅ YES — has no secrets | Only update social links (see Step 3 below). |

**On Render**, you type the values from your `.env` file into their dashboard manually.
Render stores them securely — they are never visible in your code.

---

## WHAT YOU MUST MANUALLY EDIT BEFORE DEPLOYING

Only **two files** need changes. Everything else is already correct.

### Edit 1 — `msys/.env` (update the M-Pesa callback URL)

Open `msys/.env` and change this one line:

```
BEFORE:  MPESA_CALLBACK_URL=https://yourdomain.com/mpesa/callback/
AFTER:   MPESA_CALLBACK_URL=https://rgc-nyahururu-cms.onrender.com/mpesa/callback/
```

Everything else in `.env` stays the same. Do not delete anything.

### Edit 2 — `rgc-mobile/constants/Api.ts` (update your church social links)

Open the file and fill in your actual social media page URLs:

```typescript
export const SOCIAL = {
  facebook:  'https://www.facebook.com/YOUR_ACTUAL_PAGE',  // ← change this
  instagram: 'https://www.instagram.com/YOUR_ACTUAL_PAGE', // ← change this
  youtube:   'https://www.youtube.com/@YOUR_CHANNEL',       // ← change this
  linkedin:  'https://www.linkedin.com/company/YOUR_PAGE',  // ← change this (or delete)
  twitter:   'https://twitter.com/YOUR_PAGE',               // ← change this (or leave as-is)
};
```

If you don't have a page for one of them, leave it as-is — the app won't show a broken link.

**The BASE_URL is already set correctly:**
```typescript
export const BASE_URL = 'https://rgc-nyahururu-cms.onrender.com';
```
Do not change this unless you use a custom domain.

---

## PART 1 — DEPLOY THE WEBSITE TO RENDER

### Step 1 — Push your code to GitHub

Open Command Prompt and run:
```
cd C:\Users\NGM\Documents\Francis\emobilis-fnl-prjct-
git add -A
git commit -m "Production deployment"
git push origin master
```

> **Note:** The `msys/.env` file will NOT be pushed because it is in `.gitignore`.
> GitHub will never see your passwords or API keys.

---

### Step 2 — Create the service on Render

1. Go to **https://render.com** → Log in (or create a free account)
2. Click **New** → **Blueprint**
3. Click **Connect a repository** → Connect GitHub → select **`emobilis-fnl-prjct-`**
4. Render reads `render.yaml` automatically
5. Click **Apply** — Render creates:
   - A web service named `rgc-nyahururu-cms`
   - A free PostgreSQL database named `rgc-db`

> Render will run the build automatically. The first build takes 3–5 minutes.

---

### Step 3 — Add your secret environment variables

In Render → your `rgc-nyahururu-cms` service → click **Environment** tab.

Click **Add Environment Variable** and add each one below.
Copy the exact values from your `msys/.env` file.

| Key | Where to get the value | Example value from your .env |
|-----|------------------------|-------------------------------|
| `EMAIL_HOST_USER` | Your Gmail address | e.g. `yourchurch@gmail.com` |
| `EMAIL_HOST_PASSWORD` | Gmail App Password (16 chars from myaccount.google.com/apppasswords) | `xxxx xxxx xxxx xxxx` |
| `MPESA_CONSUMER_KEY` | Your Daraja sandbox app | Value in your `.env` |
| `MPESA_CONSUMER_SECRET` | Your Daraja sandbox app | Value in your `.env` |
| `MPESA_TILL_NUMBER` | Your real till (or `538394` for sandbox) | `538394` |
| `MPESA_PASSKEY` | Daraja sandbox passkey | Value in your `.env` |
| `MPESA_CALLBACK_URL` | Your Render URL | `https://rgc-nyahururu-cms.onrender.com/mpesa/callback/` |
| `AT_USERNAME` | Africa's Talking | `sandbox` (for testing) |
| `AT_API_KEY` | Africa's Talking dashboard | Value in your `.env` |
| `TWILIO_ACCOUNT_SID` | Twilio console | Value in your `.env` |
| `TWILIO_AUTH_TOKEN` | Twilio console | Value in your `.env` |
| `TWILIO_VERIFY_SERVICE_SID` | Twilio console | Value in your `.env` |
| `WHATSAPP_ACCESS_TOKEN` | Meta Business → WhatsApp | Value in your `.env` (if set up) |
| `WHATSAPP_PHONE_NUMBER_ID` | Meta Business → WhatsApp | Value in your `.env` (if set up) |

> **Which ones are required right now?**
> - ✅ Required immediately: `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`
> - ✅ Required for M-Pesa: `MPESA_CONSUMER_KEY`, `MPESA_CONSUMER_SECRET`, `MPESA_CALLBACK_URL`
> - ⏳ Can skip for now: `TWILIO_*`, `WHATSAPP_*`, `AT_*` (app still works without them)

Click **Save Changes** — the service restarts automatically.

---

### Step 4 — Initialize the database

In Render → `rgc-nyahururu-cms` → **Shell** tab, run these commands:

```bash
# Create your admin account (you will be asked for username/email/password)
python manage.py createsuperuser

# Load all 41 hymns (English, Swahili, Kikuyu)
python manage.py load_hymns

# Seed the RGC Nyahururu HQ church record
python manage.py shell -c "
from myapp.models import BranchChurch
BranchChurch.objects.get_or_create(
    name='RGC Nyahururu HQ',
    defaults={
        'region': 'nyahururu',
        'location': 'Nyahururu Town, Laikipia County',
        'status': 'active',
        'latitude': -0.0296,
        'longitude': 36.3590,
        'notes': 'Central Rift Regional Headquarters',
    }
)
print('HQ church created.')
"
```

---

### Step 5 — Verify everything works

Visit these URLs in your browser:

| Page | URL to visit | What to check |
|------|-------------|---------------|
| Home | `https://rgc-nyahururu-cms.onrender.com` | Site loads with church name |
| Login | `https://rgc-nyahururu-cms.onrender.com/login` | Can log in as admin |
| Admin portal | `https://rgc-nyahururu-cms.onrender.com/adminn/` | Dashboard shows |
| Django admin | `https://rgc-nyahururu-cms.onrender.com/admin/` | Full database admin |
| Members | `https://rgc-nyahururu-cms.onrender.com/adminn/members/` | Member list loads |
| Regional map | `https://rgc-nyahururu-cms.onrender.com/regional/` | Map shows churches |
| Hymns | `https://rgc-nyahururu-cms.onrender.com/hymns/` | 41 hymns listed |
| Bible | `https://rgc-nyahururu-cms.onrender.com/bible/` | Translation dropdown works |
| Sermon notes | `https://rgc-nyahururu-cms.onrender.com/sermon-notes/` | Restricted page loads |
| Videos | `https://rgc-nyahururu-cms.onrender.com/video` | Video page loads |
| Contribute | `https://rgc-nyahururu-cms.onrender.com/contribute` | M-Pesa form shows |
| API | `https://rgc-nyahururu-cms.onrender.com/api/` | Returns JSON |

> **Important:** The free Render tier sleeps after 15 minutes of no traffic.
> The first request after sleeping takes ~30 seconds. This is normal.
> Upgrade to Starter ($7/month) to keep it always-on.

---

## PART 2 — BUILD THE MOBILE APP (APK)

### Step 1 — Make sure the URL points to Render

Open `rgc-mobile/constants/Api.ts` and confirm:
```typescript
export const BASE_URL = 'https://rgc-nyahururu-cms.onrender.com';
```
This is already set correctly. Do not change it.

### Step 2 — Create a free Expo account

1. Go to **https://expo.dev** → Sign Up (free)
2. Verify your email

### Step 3 — Login and build

Open Command Prompt:
```
cd C:\Users\NGM\Documents\Francis\emobilis-fnl-prjct-\rgc-mobile
npm install
eas login
```
Enter your expo.dev email and password.

```
eas build:configure
```
Select **Android** → press Enter for defaults.

```
eas build --platform android --profile preview
```
When asked **"Generate a new Android Keystore?"** → press **Enter** (Yes).

Wait **10–15 minutes**. When done you get a URL like:
```
https://expo.dev/artifacts/eas/XXXXXXXXXX.apk
```

### Step 4 — Share the APK

Download the `.apk` file (about 80–120 MB) and send it to users via:
- **WhatsApp** — send as a document/file (not as media)
- **Google Drive** — upload, share the link
- **Email** — attach and send

**Install instructions to send with the APK:**
> 1. Download the file (ends in `.apk`)
> 2. Tap it in your Downloads folder
> 3. If asked "Allow from this source" → Settings → turn on → go back
> 4. Tap Install → Open
> 5. Register with your name, email, and phone number

---

## PART 3 — SWITCH FROM SANDBOX TO REAL MONEY (M-Pesa Live)

When you are ready to accept real church contributions:

### Get a real Safaricom Till Number
1. Go to any **Safaricom shop** with your church registration documents
2. Register a **Buy Goods (Merchant)** till number
3. You receive a **Till Number** (e.g., 654321)

### Go Live on Daraja Portal
1. Go to **https://developer.safaricom.co.ke**
2. Log in → **My Apps** → your app → **Go Live**
3. Fill in the application (needs business PIN or registration)
4. You receive live **Consumer Key**, **Consumer Secret**, and **Passkey**

### Update Render environment variables
In Render → Environment tab, update:

| Key | Change to |
|-----|-----------|
| `MPESA_ENVIRONMENT` | `production` |
| `MPESA_TILL_NUMBER` | Your real till number |
| `MPESA_CONSUMER_KEY` | Live consumer key from Daraja |
| `MPESA_CONSUMER_SECRET` | Live consumer secret from Daraja |
| `MPESA_PASSKEY` | Live passkey from Daraja |

Click Save Changes. Done — the app automatically uses real M-Pesa.

---

## PART 4 — CUSTOM DOMAIN (Optional)

If you buy a domain like `rgcnyahururu.org`:

1. In Render → `rgc-nyahururu-cms` → **Settings** → **Custom Domains** → Add your domain
2. Render gives you a **CNAME record** (e.g., `rgc-nyahururu-cms.onrender.com`)
3. Go to your domain registrar → DNS settings → Add that CNAME
4. HTTPS certificate is automatic (takes up to 24 hours)

Update Render environment variables:
```
ALLOWED_HOSTS=rgcnyahururu.org,www.rgcnyahururu.org
MPESA_CALLBACK_URL=https://rgcnyahururu.org/mpesa/callback/
```

Update `rgc-mobile/constants/Api.ts`:
```typescript
export const BASE_URL = 'https://rgcnyahururu.org';
```
Then rebuild the APK (`eas build --platform android --profile preview`).

---

## TROUBLESHOOTING

### "Application error" or blank page on Render
→ Render → your service → **Logs** tab → read the error message
→ Most common cause: missing environment variable
→ Fix: add the missing variable in Environment tab → Save → redeploy

### "Network Error" in the mobile app
→ Check `Api.ts` has the correct Render URL
→ Wait 30 seconds if Render was sleeping (first request)
→ Test the URL in a browser: `https://rgc-nyahururu-cms.onrender.com/api/categories/`
→ Should return JSON (not an error page)

### "Cannot send email" / email not arriving
→ Check `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` are set in Render Environment
→ Gmail App Password must be 16 characters with spaces (e.g., `ifph nfgy onjh rpuh`)
→ Go to **myaccount.google.com/apppasswords** to generate a new one if needed

### M-Pesa "Auth Failed" or "Invalid Transaction"
→ Sandbox only works with `MPESA_ENVIRONMENT=sandbox` and shortcode `174379`
→ Check `MPESA_CONSUMER_KEY` and `MPESA_CONSUMER_SECRET` are correct in Render
→ For sandbox, get credentials at **developer.safaricom.co.ke**

### EAS build fails
→ Run `npx expo-doctor` in the `rgc-mobile` folder
→ Check **expo.dev** → your project → Builds tab for full error logs
→ Try: `npm install` then rebuild

### Hymns not loading in app
→ In Render Shell: `python manage.py load_hymns`
→ The command skips hymns that already exist (safe to run multiple times)

### New sermon note not visible to members
→ This is correct behavior — pastors create notes privately
→ Admin must go to `/sermon-notes/` → open the note → click **"Release to Members"**
→ Only then will regular members be able to see it

---

## ADMIN CREDENTIALS (Change after first login)

```
Default superuser: whatever you set in Step 4 (createsuperuser)
Django Admin:      /admin/
RGC Admin Portal:  /adminn/
```

**Change your password immediately** after first login:
`/adminn/` → top right → your name → Profile → Change Password

---

## KEY URLS REFERENCE

| Page | URL |
|------|-----|
| Main website | `/` |
| Login | `/login` |
| Admin portal | `/adminn/` |
| Django admin (full DB) | `/admin/` |
| Members management | `/adminn/members/` |
| Add member | `/adminn/members/add/` |
| Manage roles | `/adminn/manage-users/` |
| Sermon notes | `/sermon-notes/` |
| Hymns | `/hymns/` |
| Bible | `/bible/` |
| Gallery | `/gallery` |
| Videos | `/video` |
| Regional churches | `/regional/` |
| Clergy payments 🔒 | `/adminn/clergy-payments/` |
| Notification settings | `/notifications/preferences/` |
| Contribute (M-Pesa) | `/contribute` |
| REST API | `/api/` |

---

*Redeemed Gospel Church Nyahururu — "Where everybody is somebody"*
