import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
from functools import wraps
from flask import request, jsonify
import os
import base64
import json
import traceback

cred = None
firebase_app = None

def init_firebase():
    global cred, firebase_app

    # Check if already initialized
    try:
        firebase_app = firebase_admin.get_app()
        print("Firebase Admin SDK already initialized")
        return firebase_app
    except ValueError:
        pass  # Not initialized yet

    print("\n" + "="*60)
    print("FIREBASE INITIALIZATION STARTING")
    print("="*60)

    # Debug: Check environment
    is_vercel = os.getenv('VERCEL') or '/var/task' in os.getcwd()
    print(f"Running on Vercel: {is_vercel}")
    print(f"Current directory: {os.getcwd()}")

    try:
        # Method 1: Try local service account file (for local development)
        if not is_vercel:
            service_account_path = 'serviceAccountKey.json'
            if os.path.exists(service_account_path):
                print(f"Found local service account file: {service_account_path}")
                cred = credentials.Certificate(service_account_path)
                firebase_app = firebase_admin.initialize_app(cred)
                print("✅ Firebase initialized with local service account file")
                return firebase_app

        # Method 2: Try base64 encoded entire service account JSON (best for Vercel)
        service_account_base64 = os.getenv('FIREBASE_SERVICE_ACCOUNT_BASE64', '').strip()

        if service_account_base64:
            print(f"Found FIREBASE_SERVICE_ACCOUNT_BASE64 (length: {len(service_account_base64)})")

            try:
                # Remove any whitespace or newlines
                service_account_base64 = service_account_base64.replace('\n', '').replace('\r', '').replace(' ', '')

                # Decode the entire service account JSON
                service_account_bytes = base64.b64decode(service_account_base64)
                service_account_json = service_account_bytes.decode('utf-8')
                service_account_data = json.loads(service_account_json)

                print(f"Successfully decoded service account JSON")
                print(f"Project ID from JSON: {service_account_data.get('project_id')}")

                # Verify required fields
                required_fields = ['project_id', 'private_key', 'client_email']
                missing_fields = [f for f in required_fields if not service_account_data.get(f)]

                if missing_fields:
                    print(f"❌ Missing required fields in service account JSON: {missing_fields}")
                    return None

                cred = credentials.Certificate(service_account_data)
                firebase_app = firebase_admin.initialize_app(cred)
                print("✅ Firebase initialized with base64 encoded service account JSON")
                return firebase_app

            except base64.binascii.Error as e:
                print(f"❌ Base64 decode error: {e}")
                print("Make sure FIREBASE_SERVICE_ACCOUNT_BASE64 contains valid base64")
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                print("Decoded base64 is not valid JSON")
            except Exception as e:
                print(f"❌ Error processing service account base64: {e}")
                traceback.print_exc()

        # Method 3: Try individual environment variables (fallback)
        print("Trying individual environment variables...")

        project_id = os.getenv('FIREBASE_PROJECT_ID', '').strip()
        client_email = os.getenv('FIREBASE_CLIENT_EMAIL', '').strip()
        private_key_base64 = os.getenv('FIREBASE_PRIVATE_KEY_BASE64', '').strip()
        private_key = os.getenv('FIREBASE_PRIVATE_KEY', '').strip()

        print(f"Project ID exists: {bool(project_id)}")
        print(f"Client Email exists: {bool(client_email)}")
        print(f"Private Key Base64 exists: {bool(private_key_base64)}")
        print(f"Private Key exists: {bool(private_key)}")

        # Try to get the private key
        if private_key_base64:
            try:
                private_key_base64 = private_key_base64.replace('\n', '').replace('\r', '').replace(' ', '')
                private_key = base64.b64decode(private_key_base64).decode('utf-8')
                print("Successfully decoded FIREBASE_PRIVATE_KEY_BASE64")
            except Exception as e:
                print(f"❌ Error decoding FIREBASE_PRIVATE_KEY_BASE64: {e}")
                private_key = ''

        if not private_key:
            print("❌ No valid private key found")
            print("\n" + "="*60)
            print("FIREBASE NOT CONFIGURED - USING IN-MEMORY DATABASE")
            print("This will cause intermittent 404 errors on Vercel!")
            print("="*60 + "\n")
            return None

        # Build the config
        firebase_config = {
            "type": "service_account",
            "project_id": project_id,
            "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID', '').strip(),
            "private_key": private_key,
            "client_email": client_email,
            "client_id": os.getenv('FIREBASE_CLIENT_ID', '').strip(),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{client_email}" if client_email else None
        }

        # Verify required fields
        if not all([project_id, private_key, client_email]):
            print("❌ Missing required Firebase configuration")
            print(f"  Project ID: {bool(project_id)}")
            print(f"  Private Key: {bool(private_key)}")
            print(f"  Client Email: {bool(client_email)}")
            return None

        cred = credentials.Certificate(firebase_config)
        firebase_app = firebase_admin.initialize_app(cred)
        print("✅ Firebase initialized with individual environment variables")
        return firebase_app

    except Exception as e:
        print(f"\n❌ Firebase Admin SDK initialization error: {str(e)}")
        print("\nDEBUG INFO:")
        print(f"  Error type: {type(e).__name__}")
        print(f"  Project ID: {os.getenv('FIREBASE_PROJECT_ID', 'NOT SET')}")
        print(f"  Client Email: {os.getenv('FIREBASE_CLIENT_EMAIL', 'NOT SET')}")
        traceback.print_exc()
        print("\n" + "="*60)
        print("FIREBASE NOT AVAILABLE - USING IN-MEMORY DATABASE")
        print("This will cause intermittent 404 errors on Vercel!")
        print("="*60 + "\n")
        return None

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