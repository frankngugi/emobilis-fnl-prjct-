# RGC Nyahururu CMS — Complete Deployment Guide
# Website (Render) + Mobile App (EAS APK)

---

## PART 1 — DEPLOY THE WEBSITE TO RENDER

### Step 1 — Push latest code to GitHub
Open Command Prompt:
```
cd C:\Users\NGM\Documents\Francis\emobilis-fnl-prjct-
git add -A
git commit -m "Deploy to production"
git push origin master
```

### Step 2 — Deploy on Render
1. Go to **https://render.com** → Log in
2. Click **New** → **Blueprint**
3. Connect GitHub → select **`emobilis-fnl-prjct-`**
4. Render auto-reads `render.yaml` → creates web app + PostgreSQL
5. Click **Apply**

### Step 3 — Set environment variables
In Render → your web service → **Environment** tab → add:

| Key | Value |
|-----|-------|
| `EMAIL_HOST_USER` | `frneltp@gmail.com` |
| `EMAIL_HOST_PASSWORD` | `ifph nfgy onjh rpuh` |
| `MPESA_CONSUMER_KEY` | *(from msys/.env)* |
| `MPESA_CONSUMER_SECRET` | *(from msys/.env)* |
| `MPESA_TILL_NUMBER` | `538394` |
| `AT_USERNAME` | `sandbox` |
| `AT_API_KEY` | *(from msys/.env)* |
| `TWILIO_ACCOUNT_SID` | *(from msys/.env)* |
| `TWILIO_AUTH_TOKEN` | *(from msys/.env)* |
| `TWILIO_VERIFY_SERVICE_SID` | *(from msys/.env)* |
| `WHATSAPP_ACCESS_TOKEN` | *(from Meta — optional)* |
| `WHATSAPP_PHONE_NUMBER_ID` | *(from Meta — optional)* |

Click **Save Changes** → service restarts with new vars.

### Step 4 — Initialize the database
In Render → your service → **Shell** tab:
```bash
python manage.py createsuperuser
python manage.py load_hymns
```
Create a superuser with a strong password.

### Step 5 — Verify deployment
1. Visit `https://rgc-nyahururu-cms.onrender.com`
2. Log in at `/login` with your superuser credentials
3. Visit `/admin/` for Django admin
4. Visit `/regional/` to see the regional churches map
5. Visit `/bible/` to test Bible navigation + projector
6. Test `/contribute` for M-Pesa (sandbox mode)

> **Note:** Render free tier sleeps after 15 min inactivity.
> First request after sleep takes ~30 seconds.
> Upgrade to Starter ($7/month) to keep it always-on.

---

## PART 2 — BUILD AND DEPLOY THE MOBILE APP (APK)

### Step 1 — Update API URL to point to Render
Edit `rgc-mobile/constants/Api.ts`:
```typescript
export const BASE_URL = 'https://rgc-nyahururu-cms.onrender.com';
```

### Step 2 — Create Expo account
1. Go to **https://expo.dev** → Sign Up (free)
2. Use any email → verify it

### Step 3 — Login to EAS
Open Command Prompt:
```
cd C:\Users\NGM\Documents\Francis\emobilis-fnl-prjct-\rgc-mobile
eas login
```
Enter your expo.dev email and password.

### Step 4 — Configure EAS project
```
eas build:configure
```
Select **Android** when prompted. Press Enter for all defaults.

### Step 5 — Build the APK
```
eas build --platform android --profile preview
```
When asked "Generate a new Android Keystore?" → press **Enter** (Yes).

Wait 10–15 minutes. The terminal shows progress.
When done, you get a URL like:
```
https://expo.dev/artifacts/eas/XXXXXXXXXX.apk
```

### Step 6 — Download and share the APK
1. Click the download URL → save the `.apk` file (typically ~80-120 MB)
2. Send to your test user via:
   - **WhatsApp** — send as a document/file attachment
   - **Email** — attach and send
   - **Google Drive** — upload, share link
   - **USB** — copy directly to their phone

### Step 7 — Instructions for end user (send this with the APK)

> **"How to install RGC Nyahururu app:"**
> 1. Download the file I sent you (it ends in `.apk`)
> 2. Tap the downloaded file in your notifications or in the Downloads folder
> 3. If phone asks "Allow from this source" → tap **Settings** → turn on → go back
> 4. Tap **Install** → tap **Open**
> 5. Register with your name, email, and phone number
> 6. You're in! No need for any other app.

### Step 8 — Future updates
When you make changes to the app, just run:
```
eas build --platform android --profile preview
```
New APK link is generated. Share it — user uninstalls old and installs new.

---

## PART 3 — GOING FULLY LIVE (Production M-Pesa)

When ready to accept real money:

### Get a real Safaricom M-Pesa Till
1. Go to a Safaricom shop or M-Pesa agent with church documents
2. Register a **Buy Goods (Merchant)** till number
3. You'll receive a **Till Number** (e.g. 123456)

### Apply on Daraja Portal
1. Go to **https://developer.safaricom.co.ke**
2. Log in → go to **My Apps** → your app → **Go Live**
3. Fill in the application form (business registration required)
4. Get approved production Consumer Key + Consumer Secret

### Update environment variables on Render
```
MPESA_ENVIRONMENT=production
MPESA_TILL_NUMBER=your_real_till_number
MPESA_CONSUMER_KEY=live_consumer_key
MPESA_CONSUMER_SECRET=live_consumer_secret
MPESA_CALLBACK_URL=https://rgc-nyahururu-cms.onrender.com/mpesa/callback/
```

### Update the app API URL
In `Api.ts` it already points to Render, so the app automatically uses production M-Pesa once the server is updated.

---

## PART 4 — OPTIONAL: Custom Domain

### Get a free domain
- **Freenom** (.tk, .ml) — free but unreliable
- **Cloudflare** (.com from ~$10/year) — recommended

### Connect to Render
1. In Render → your service → **Settings** → **Custom Domains**
2. Add your domain (e.g. `rgcnyahururu.org`)
3. Render gives you CNAME records
4. Add those CNAME records in your domain registrar's DNS settings
5. HTTPS is automatic (Let's Encrypt)

Update on Render environment:
```
ALLOWED_HOSTS=rgcnyahururu.org,www.rgcnyahururu.org
MPESA_CALLBACK_URL=https://rgcnyahururu.org/mpesa/callback/
```

---

## QUICK REFERENCE

### Render Dashboard
```
https://dashboard.render.com
→ Your service: rgc-nyahururu-cms
→ Logs: to debug issues
→ Shell: to run management commands
→ Environment: to update secrets
```

### Expo Dashboard  
```
https://expo.dev
→ Your project: rgc-nyahururu
→ Builds: download past APKs
→ Usage: track remaining free build minutes
```

### Key URLs (after deployment)
| Page | URL |
|------|-----|
| Website | `https://rgc-nyahururu-cms.onrender.com` |
| Admin | `https://rgc-nyahururu-cms.onrender.com/admin/` |
| RGC Admin Portal | `https://rgc-nyahururu-cms.onrender.com/adminn/` |
| API (for mobile) | `https://rgc-nyahururu-cms.onrender.com/api/` |
| Regional Churches | `https://rgc-nyahururu-cms.onrender.com/regional/` |
| Clergy Payments 🔒 | `https://rgc-nyahururu-cms.onrender.com/adminn/clergy-payments/` |

### Default credentials (CHANGE IMMEDIATELY AFTER DEPLOY)
```
Username: admin
Password: RGCAdmin2024!
```

---

## TROUBLESHOOTING

### Website shows 500 error
→ Check Render Logs tab for the actual error
→ Common cause: missing environment variable
→ Run `python manage.py check` in Shell

### Mobile app says "Network Error"
→ Check BASE_URL in Api.ts points to Render URL
→ Wait 30 sec if Render was sleeping (first request)
→ Check `/api/categories/` returns JSON in browser

### M-Pesa "Auth Failed"
→ Verify MPESA_CONSUMER_KEY and MPESA_CONSUMER_SECRET are set in Render
→ For sandbox: use sandbox credentials from developer.safaricom.co.ke
→ For production: use live credentials

### Build fails on EAS
→ Run `npx expo-doctor` in rgc-mobile folder
→ Check expo.dev dashboard for build logs
→ Common fix: `npm install` then try again

---

*Redeemed Gospel Church Nyahururu — "Where everybody is somebody"*
