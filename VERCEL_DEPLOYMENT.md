# Vercel Deployment Instructions

## Critical Issue Fixed
The intermittent 404 errors (where zines work twice then fail on third refresh) were caused by Vercel running multiple serverless instances with separate in-memory databases. This has been fixed by properly configuring Firebase/Firestore.

## Required Environment Variables

You need to set **ONE** environment variable in Vercel:

### FIREBASE_SERVICE_ACCOUNT_BASE64

Copy the entire value from `.env.production` (line 6) - it's the long base64 string that starts with `eyJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCI...`

**IMPORTANT:**
- Copy the ENTIRE value (it's about 3144 characters long)
- Make sure there are NO spaces or newlines at the beginning or end
- The value should be one continuous string

### Setting the Environment Variable in Vercel:

1. Go to your Vercel project dashboard
2. Click on "Settings" tab
3. Click on "Environment Variables" in the left sidebar
4. Add the following variable:
   - **Key:** `FIREBASE_SERVICE_ACCOUNT_BASE64`
   - **Value:** [Paste the entire base64 string from .env.production]
   - **Environment:** Production, Preview, Development (select all)
5. Click "Save"

### Other Required Variables (Already Set)

These should already be in your Vercel environment:
- FIREBASE_API_KEY
- FIREBASE_AUTH_DOMAIN
- FIREBASE_PROJECT_ID
- FIREBASE_STORAGE_BUCKET
- FIREBASE_MESSAGING_SENDER_ID
- FIREBASE_APP_ID
- FIREBASE_MEASUREMENT_ID
- SECRET_KEY

## Testing the Deployment

After setting the environment variable:

1. Trigger a new deployment (push any change or click "Redeploy" in Vercel)

2. Check the Function Logs in Vercel to see initialization messages:
   - You should see: "✅ Firebase initialized with base64 encoded service account JSON"
   - You should see: "✅ Firestore is available and working"

3. Test the app:
   - Visit https://archgest.com/debug/firebase to see detailed initialization info
   - Create a new zine and verify it persists across refreshes
   - The /dev/test zine should always be available

## What Was Fixed

1. **Improved Firebase initialization** with better error handling and logging
2. **Base64 encoding** of the entire service account JSON for simpler configuration
3. **Detailed logging** to track initialization issues on Vercel
4. **Firestore connection testing** to ensure it's working before using it

## If Issues Persist

1. Check the Vercel Function Logs for error messages
2. Visit https://archgest.com/debug/firebase for detailed diagnostics
3. Ensure the FIREBASE_SERVICE_ACCOUNT_BASE64 value is exactly as in .env.production
4. Verify Firestore is enabled in Google Cloud Console for project archgest-20638

The app will now use Firestore for persistent storage, eliminating the intermittent 404 errors!