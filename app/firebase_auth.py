import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
from functools import wraps
from flask import request, jsonify
import os

cred = None
firebase_app = None

def init_firebase():
    global cred, firebase_app

    try:
        service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH')

        if service_account_path and os.path.exists(service_account_path):
            cred = credentials.Certificate(service_account_path)
        else:
            # Use environment variables for Vercel deployment
            private_key = os.getenv('FIREBASE_PRIVATE_KEY', '')

            # Handle different private key formats
            if private_key:
                # If the key doesn't have actual newlines, replace \n with actual newlines
                if '\\n' in private_key:
                    private_key = private_key.replace('\\n', '\n')
                # Ensure proper formatting
                if not private_key.startswith('-----BEGIN'):
                    private_key = '-----BEGIN PRIVATE KEY-----\n' + private_key
                if not private_key.endswith('-----\n'):
                    private_key = private_key + '\n-----END PRIVATE KEY-----\n'

            firebase_config = {
                "type": "service_account",
                "project_id": os.getenv('FIREBASE_PROJECT_ID'),
                "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
                "private_key": private_key,
                "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
                "client_id": os.getenv('FIREBASE_CLIENT_ID'),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": os.getenv('FIREBASE_CLIENT_CERT_URL')
            }

            # Only try to initialize if we have the required fields
            if (firebase_config.get('project_id') and
                firebase_config.get('private_key') and
                firebase_config.get('client_email')):
                cred = credentials.Certificate(firebase_config)
            else:
                # Development mode without Firebase Admin SDK
                print("\n" + "="*60)
                print("Firebase Admin SDK not configured (this is OK for development)")
                print("Frontend authentication will still work with Firebase")
                print("To enable backend verification, add serviceAccountKey.json")
                print("="*60 + "\n")
                return None

        if cred:
            firebase_app = firebase_admin.initialize_app(cred)
            print("Firebase Admin SDK initialized successfully")

    except Exception as e:
        print(f"\nFirebase Admin SDK initialization error: {str(e)}")
        print(f"Project ID: {os.getenv('FIREBASE_PROJECT_ID')}")
        print(f"Client Email: {os.getenv('FIREBASE_CLIENT_EMAIL')}")
        print(f"Private Key exists: {bool(os.getenv('FIREBASE_PRIVATE_KEY'))}")
        print("Frontend authentication will still work\n")
        import traceback
        traceback.print_exc()
        return None

    return firebase_app

def verify_token(id_token):
    """Verify Firebase ID token and return decoded token"""
    try:
        if not firebase_app:
            # Development mode - return mock user
            return {
                'uid': 'dev-user',
                'email': 'dev@example.com',
                'name': 'Dev User'
            }

        decoded_token = firebase_auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        print(f"Error verifying token: {e}")
        return None

def get_user(uid):
    """Get Firebase user by UID"""
    try:
        if not firebase_app:
            # Development mode
            return {
                'uid': uid,
                'email': 'dev@example.com',
                'display_name': 'Dev User'
            }

        user = firebase_auth.get_user(uid)
        return {
            'uid': user.uid,
            'email': user.email,
            'display_name': user.display_name,
            'photo_url': user.photo_url
        }
    except Exception as e:
        print(f"Error getting user: {e}")
        return None

def firebase_required(f):
    """Decorator to require Firebase authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No authorization token provided'}), 401

        id_token = auth_header.split('Bearer ')[1]
        decoded_token = verify_token(id_token)

        if not decoded_token:
            return jsonify({'error': 'Invalid authorization token'}), 401

        request.firebase_user = decoded_token
        return f(*args, **kwargs)

    return decorated_function