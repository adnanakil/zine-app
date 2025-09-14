# Firebase Setup Guide for Zine App

## Your Firebase Project Details
- **Project ID**: archgest-20638
- **Project Number**: 1039573653180
- **API Key**: AIzaSyBSYJd9hGVT8YoUmgJXoLQMhILSQe6t4QE

## Steps to Complete Setup

### 1. Enable Authentication in Firebase Console

1. Go to [Firebase Console](https://console.firebase.google.com/project/archgest-20638/authentication)
2. Click on "Get started" if not already enabled
3. Go to "Sign-in method" tab
4. Enable the following providers:
   - **Email/Password**: Click, toggle "Enable", and Save
   - **Google**: Click, toggle "Enable", add a support email, and Save

### 2. Get Your Web App ID

1. Go to [Project Settings](https://console.firebase.google.com/project/archgest-20638/settings/general)
2. Scroll to "Your apps" section
3. If no web app exists:
   - Click "Add app" → Choose Web (</> icon)
   - Register app with nickname "Zine App"
   - Copy the `appId` from the config shown
4. Update the `FIREBASE_APP_ID` in your `.env` file

### 3. Download Service Account Key (for backend)

1. Go to [Service Accounts](https://console.firebase.google.com/project/archgest-20638/settings/serviceaccounts/adminsdk)
2. Click "Generate new private key"
3. Save the downloaded JSON file as `serviceAccountKey.json` in the `zine-app` directory
4. Update `.env` file:
   ```
   FIREBASE_SERVICE_ACCOUNT_PATH=serviceAccountKey.json
   ```

### 4. Configure Authorized Domains (Important!)

1. Go to [Authentication Settings](https://console.firebase.google.com/project/archgest-20638/authentication/settings)
2. Under "Authorized domains", add:
   - `localhost` (for local development)
   - Your Vercel domain when deployed (e.g., `your-app.vercel.app`)

### 5. Set up Firebase Security Rules (if using Firestore later)

For now, the app uses SQLite, but if you want to use Firestore later:

1. Go to [Firestore Database](https://console.firebase.google.com/project/archgest-20638/firestore)
2. Create database if not exists
3. Set appropriate security rules

## Running the App Locally

1. Install dependencies:
   ```bash
   cd zine-app
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Initialize the database:
   ```bash
   python
   >>> from app import create_app, db
   >>> app = create_app()
   >>> with app.app_context():
   ...     db.create_all()
   >>> exit()
   ```

3. Run the application:
   ```bash
   python app.py
   ```

4. Visit `http://localhost:5000`

## Testing Authentication

1. **Sign up with Email**:
   - Go to `/auth/register`
   - Enter username, email, and password
   - The app will create a Firebase account and local user record

2. **Sign in with Google**:
   - Click "Sign in with Google" button
   - Authorize with your Google account
   - Choose a username on first login

## Deployment to Vercel

1. Install Vercel CLI:
   ```bash
   npm i -g vercel
   ```

2. For Vercel deployment, you need to add Firebase Admin credentials as environment variables:
   - Open your `serviceAccountKey.json`
   - Add these values to Vercel environment variables:
     ```
     FIREBASE_PROJECT_ID=archgest-20638
     FIREBASE_PRIVATE_KEY_ID=(from JSON)
     FIREBASE_PRIVATE_KEY=(from JSON, keep the \n characters)
     FIREBASE_CLIENT_EMAIL=(from JSON)
     FIREBASE_CLIENT_ID=(from JSON)
     FIREBASE_CLIENT_CERT_URL=(from JSON)
     ```

3. Deploy:
   ```bash
   vercel --prod
   ```

## Troubleshooting

### "Firebase not configured" warning
- This appears when Firebase credentials are not set up
- The app will still work in development mode with mock authentication

### "Invalid token" errors
- Ensure your service account key is properly configured
- Check that the Firebase project ID matches in all configurations

### Google Sign-in not working
- Make sure Google provider is enabled in Firebase Console
- Check that your domain is in the authorized domains list
- Ensure popup blockers are disabled

## Security Notes

1. **Never commit** `serviceAccountKey.json` or `.env` to version control
2. Keep your Firebase API keys secure (though they're meant to be public for web apps)
3. Always use environment variables for sensitive data in production
4. Set up proper Firebase Security Rules when using Firestore/Storage

## Next Steps

1. Configure email templates in Firebase for password reset
2. Set up Firebase Storage for image uploads (optional)
3. Enable additional authentication providers if needed
4. Configure Firebase Analytics for usage tracking