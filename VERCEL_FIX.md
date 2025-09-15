# 🚨 URGENT: Fix Vercel Deployment

## The Problem
Your Vercel deployment is missing the correct environment variable. You have `FIREBASE_PRIVATE_KEY_BASE64` (just the private key) but you need `FIREBASE_SERVICE_ACCOUNT_BASE64` (the complete service account JSON).

## The Solution - Add ONE Environment Variable

### Step 1: Copy the Value
Open `.env.production` in this project and find line 6:
```
FIREBASE_SERVICE_ACCOUNT_BASE64=eyJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCI...
```

Copy the ENTIRE value after the `=` sign. It should:
- Start with `eyJ0eXBlIjo`
- Be exactly 3144 characters long
- Be one continuous string with NO spaces or line breaks

### Step 2: Add to Vercel

1. Go to https://vercel.com/dashboard
2. Click on your `zine-app` project
3. Go to **Settings** → **Environment Variables**
4. Click **Add New**
5. Enter:
   - **Key:** `FIREBASE_SERVICE_ACCOUNT_BASE64`
   - **Value:** [Paste the entire 3144-character string]
   - **Environment:** Select all (Production ✓, Preview ✓, Development ✓)
6. Click **Save**

### Step 3: Redeploy

After adding the variable:
1. Go to the **Deployments** tab
2. Click the three dots (...) on the latest deployment
3. Click **Redeploy**
4. Wait for deployment to complete

### Step 4: Verify It Worked

1. Visit https://archgest.com/debug/firebase
2. Look for the `summary` section at the bottom
3. You should see:
   - `"firebase_ready": true`
   - `"firestore_ready": true`
   - `"message": "✅ Firebase configuration looks good!"`

## What This Fixes

✅ Eliminates intermittent 404 errors
✅ Makes zines persist permanently
✅ Fixes the "works twice then fails" issue
✅ Enables proper Firestore database connection

## Important Notes

- You already have other Firebase variables set, which is good
- The `FIREBASE_PRIVATE_KEY_BASE64` you currently have is NOT enough
- You need the FULL service account JSON encoded as base64
- This is stored in `FIREBASE_SERVICE_ACCOUNT_BASE64`

## Still Having Issues?

Check the debug endpoint: https://archgest.com/debug/firebase

If you see `"action_required"` messages, follow those instructions.