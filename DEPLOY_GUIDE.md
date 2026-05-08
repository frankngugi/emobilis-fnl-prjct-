# RGC Nyahururu CMS — Deployment Guide
# Updated: May 2026 | Status: Ready to deploy

---

## BEFORE YOU START — READ THIS ONCE

**Your `msys/.env` file stays on your laptop only.**
It is blocked from GitHub by `.gitignore`. You never touch it for deployment —
instead you copy each value from it into Render's Environment tab (Step 5 below).

**Your code on GitHub has NO secrets.** The `.env` was removed from all git history.

---

## PART 1 — DEPLOY THE WEBSITE (Render.com)

### Step 1 — Push your code to GitHub

Open **Command Prompt** and run:

```
cd C:\Users\NGM\Documents\Francis\emobilis-fnl-prjct-
git add -A
git commit -m "Deploy to production"
git push origin master
```

That's it. GitHub will have your latest code with no secrets.

---

### Step 2 — Create the service on Render

1. Go to **https://render.com** → Sign in (or create a free account with your Gmail)
2. Click **New +** → **Blueprint**
3. Click **Connect a repository** → connect your GitHub → select **`emobilis-fnl-prjct-`**
4. Render reads `render.yaml` automatically and shows you what it will create:
   - A web service called `rgc-nyahururu-cms`
   - A free PostgreSQL database called `rgc-db`
5. Click **Apply**

Render starts building. The first build takes **3–5 minutes**.
You can watch progress in the **Logs** tab.

---

### Step 3 — Wait for the build to finish

The build runs these commands automatically (from `render.yaml`):
```
pip install -r requirements.txt
python manage.py collectstatic
python manage.py migrate
python manage.py load_hymns
```

When you see **"Your service is live"** or the status turns green, continue to Step 4.

---

### Step 4 — Add your secret credentials to Render

Go to Render → click your `rgc-nyahururu-cms` service → click the **Environment** tab.

Click **Add Environment Variable** for each row below.
Open your `msys/.env` file on your laptop to copy the values.

#### Required — add these now:

| Key to type in Render | Where to find the value |
|----------------------|------------------------|
| `SECRET_KEY` | Generate any 50-character random string — e.g. go to **djecrety.ir** and copy one |
| `EMAIL_HOST_USER` | Copy from your `.env` → `EMAIL_HOST_USER` |
| `EMAIL_HOST_PASSWORD` | Copy from your `.env` → `EMAIL_HOST_PASSWORD` (the new rotated one) |
| `MPESA_CONSUMER_KEY` | Copy from your `.env` → `MPESA_CONSUMER_KEY` |
| `MPESA_CONSUMER_SECRET` | Copy from your `.env` → `MPESA_CONSUMER_SECRET` |
| `MPESA_PASSKEY` | Copy from your `.env` → `MPESA_PASSKEY` |
| `MPESA_CALLBACK_URL` | `https://rgc-nyahururu-cms.onrender.com/mpesa/callback/` |
| `AT_USERNAME` | `sandbox` |
| `AT_API_KEY` | Copy from your `.env` → `AT_API_KEY` |

#### Optional — add if you have them, skip if not:

| Key | Value |
|-----|-------|
| `TWILIO_ACCOUNT_SID` | Copy from your `.env` |
| `TWILIO_AUTH_TOKEN` | Copy from your `.env` |
| `TWILIO_VERIFY_SERVICE_SID` | Copy from your `.env` |
| `WHATSAPP_ACCESS_TOKEN` | Copy from your `.env` (leave blank if not set up) |
| `WHATSAPP_PHONE_NUMBER_ID` | Copy from your `.env` (leave blank if not set up) |

After adding all variables, click **Save Changes**.
Render restarts the service automatically — wait about 1 minute.

---

### Step 5 — Set up the database

Go to Render → your `rgc-nyahururu-cms` service → click the **Shell** tab.

Run each command below one at a time:

```bash
python manage.py createsuperuser
```
You will be asked to type:
- **Username:** choose anything (e.g. `admin`)
- **Email:** your email address
- **Password:** choose a strong password — write it down

```bash
python manage.py load_hymns
```
This loads all 41 hymns (English, Swahili, Kikuyu). Should say "41 added".

```bash
python manage.py shell -c "
from myapp.models import BranchChurch
obj, created = BranchChurch.objects.get_or_create(
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
print('Created:', created)
"
```
This seeds the RGC Nyahururu HQ on the regional map.

---

### Step 6 — Test the live site

Open these URLs in your browser one by one. Each should load correctly:

| What to check | URL |
|--------------|-----|
| Home page | `https://rgc-nyahururu-cms.onrender.com` |
| Login page | `https://rgc-nyahururu-cms.onrender.com/login` |
| Admin portal | `https://rgc-nyahururu-cms.onrender.com/adminn/` |
| Django admin | `https://rgc-nyahururu-cms.onrender.com/admin/` |
| Members list | `https://rgc-nyahururu-cms.onrender.com/adminn/members/` |
| Hymns | `https://rgc-nyahururu-cms.onrender.com/hymns/` |
| Bible | `https://rgc-nyahururu-cms.onrender.com/bible/` |
| Sermon notes | `https://rgc-nyahururu-cms.onrender.com/sermon-notes/` |
| Regional map | `https://rgc-nyahururu-cms.onrender.com/regional/` |
| Videos | `https://rgc-nyahururu-cms.onrender.com/video` |
| Give / M-Pesa | `https://rgc-nyahururu-cms.onrender.com/contribute` |
| REST API | `https://rgc-nyahururu-cms.onrender.com/api/` |

> **First request is slow.** The free Render plan sleeps after 15 minutes of no traffic.
> The first page load after sleeping takes ~30 seconds. After that it is fast.
> To keep it always-on, upgrade to Render Starter ($7/month).

---

## PART 2 — BUILD THE ANDROID APP (APK)

### Step 1 — Create a free Expo account

1. Go to **https://expo.dev** → click **Sign Up**
2. Use your email → verify it

### Step 2 — Open Command Prompt and build

```
cd C:\Users\NGM\Documents\Francis\emobilis-fnl-prjct-\rgc-mobile
npm install
eas login
```
Type your expo.dev email and password when asked.

```
eas build:configure
```
Select **Android** → press Enter for all other questions.

```
eas build --platform android --profile preview
```
When asked **"Generate a new Android Keystore?"** → press **Enter** (Yes, generate one).

Wait **10–15 minutes**. When done you get a link like:
```
https://expo.dev/artifacts/eas/XXXXXXXXXXXXXXXX.apk
```

### Step 3 — Download and share

Click the link → download the `.apk` file (~80–120 MB).

Send it to people via:
- **WhatsApp** — attach as a document (not a photo)
- **Google Drive** — upload and share the link
- **Email** — attach and send

**Instructions to include when sending the APK:**
> 1. Download the file (it ends with `.apk`)
> 2. Tap it in your Downloads folder or notifications
> 3. If your phone says "Allow installs from this source" → tap Settings → turn it on → go back
> 4. Tap **Install** → tap **Open**
> 5. Register with your name, email, and phone number

### Step 4 — Future app updates

When you change the app code, just rebuild:
```
eas build --platform android --profile preview
```
Share the new link. Users uninstall the old version and install the new one.

---

## PART 3 — SWITCH TO REAL M-PESA (when ready to collect real money)

Currently the site uses **Safaricom sandbox** — no real money moves.

When the church is ready to collect real contributions:

### Get a real Safaricom Till Number
1. Go to any **Safaricom shop** with your church registration documents (or CRB report)
2. Ask to register a **Buy Goods (Merchant)** till number
3. You receive a **Till Number** (6 digits, e.g. `654321`)

### Apply to go live on Daraja
1. Go to **https://developer.safaricom.co.ke** → log in
2. **My Apps** → your app → **Go Live**
3. Fill in the form (requires your business/church PIN)
4. Safaricom reviews and approves (takes a few days)
5. You receive a live **Consumer Key**, **Consumer Secret**, and **Passkey**

### Update Render environment variables
In Render → Environment tab, change these 5 values:

| Key | New value |
|-----|-----------|
| `MPESA_ENVIRONMENT` | `production` |
| `MPESA_TILL_NUMBER` | Your real till number |
| `MPESA_CONSUMER_KEY` | Your live consumer key |
| `MPESA_CONSUMER_SECRET` | Your live consumer secret |
| `MPESA_PASSKEY` | Your live passkey |

Click **Save Changes**. Done — the site now accepts real M-Pesa payments.

---

## PART 4 — CUSTOM DOMAIN (optional)

If you buy a domain like `rgcnyahururu.org` or `rgcnyahururu.co.ke`:

1. Render → your service → **Settings** → **Custom Domains** → Add your domain
2. Render gives you a **CNAME record** to add to your domain's DNS
3. Add it at your domain registrar's DNS settings
4. HTTPS is automatic (Render handles it, takes up to 24 hours)

After connecting the domain, update these in Render → Environment:
```
ALLOWED_HOSTS = rgcnyahururu.org,www.rgcnyahururu.org
MPESA_CALLBACK_URL = https://rgcnyahururu.org/mpesa/callback/
```

Also update `rgc-mobile/constants/Api.ts`:
```typescript
export const BASE_URL = 'https://rgcnyahururu.org';
```
Then rebuild the APK.

---

## TROUBLESHOOTING

### Site shows an error page / "Application error"
→ Render → your service → **Logs** tab → read the red error lines
→ Most common cause: a missing environment variable
→ Fix: add the missing key in Environment tab → Save → wait for restart

### First page load is very slow (30+ seconds)
→ Normal on the free plan — Render is waking up from sleep
→ After the first load it will be fast

### Mobile app says "Network Error" or "Cannot connect"
→ The Render service might be sleeping — open the website first, wait 30 sec, try app again
→ Check that `BASE_URL` in `Api.ts` is `https://rgc-nyahururu-cms.onrender.com`
→ In your browser go to `https://rgc-nyahururu-cms.onrender.com/api/categories/` — should return JSON

### Email not sending / OTP not arriving
→ Check `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` are set in Render Environment
→ The password must be the Gmail **App Password** (16 chars), not your normal Gmail password
→ To get a new one: **myaccount.google.com/apppasswords**

### M-Pesa "Auth Failed" or "Bad Request"
→ Check `MPESA_CONSUMER_KEY` and `MPESA_CONSUMER_SECRET` are set correctly in Render
→ Sandbox mode only works with the Safaricom sandbox keys from developer.safaricom.co.ke
→ Make sure `MPESA_ENVIRONMENT` is `sandbox` in render.yaml (it already is)

### Hymns not showing
→ In Render Shell run: `python manage.py load_hymns`
→ Safe to run multiple times — skips ones already loaded

### "church_detail.html not found" or similar template error
→ Pull latest code: `git push origin master` then Render will redeploy automatically

### EAS build fails
→ In Command Prompt, run `npx expo-doctor` inside the `rgc-mobile` folder
→ Common fix: `npm install` then rebuild
→ Check build logs at **expo.dev** → your project → Builds tab

---

## ALL ADMIN URLS AT A GLANCE

| Section | URL |
|---------|-----|
| Home | `/` |
| Login | `/login` |
| **Admin dashboard** | `/adminn/` |
| Add / manage members | `/adminn/members/` |
| Add a member | `/adminn/members/add/` |
| Manage user roles | `/adminn/manage-users/` |
| Post announcement | `/announcements/add/` |
| Add event | `/adminn/addevents` |
| Upload image | `/adminn/uploadimages` |
| Add video / link | `/adminn/uploadvideos` |
| Create group | `/create-group/` |
| **Sermon notes** | `/sermon-notes/` |
| Add sermon note | `/sermon-notes/add/` |
| **Hymns** | `/hymns/` |
| Add hymn | `/hymns/add/` |
| **Bible** | `/bible/` |
| Regional churches | `/regional/` |
| Manage branches (Django) | `/admin/myapp/branchchurch/` |
| Clergy payments 🔒 | `/adminn/clergy-payments/` |
| Notification settings | `/notifications/preferences/` |
| Contribute (M-Pesa) | `/contribute` |
| Django admin (full DB) | `/admin/` |
| REST API | `/api/` |

---

## WHAT RENDER ALREADY DOES FOR YOU AUTOMATICALLY

These are configured in `render.yaml` and happen without any action from you:

- ✅ Installs all Python packages (`pip install -r requirements.txt`)
- ✅ Collects static files (`python manage.py collectstatic`)
- ✅ Runs all database migrations (`python manage.py migrate`)
- ✅ Loads hymns (`python manage.py load_hymns`)
- ✅ Starts the web server with Gunicorn
- ✅ Creates and connects the PostgreSQL database
- ✅ Sets `DEBUG=false` for production
- ✅ Generates a secure `SECRET_KEY` (you still add your own in Step 4)
- ✅ Free SSL/HTTPS certificate

---

*Redeemed Gospel Church Nyahururu — "Where everybody is somebody"*
