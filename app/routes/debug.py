from flask import Blueprint, jsonify
import os
import base64

bp = Blueprint('debug', __name__)

@bp.route('/debug/firebase')
def debug_firebase():
    """Debug Firebase initialization issues"""

    debug_info = {
        'env_vars': {},
        'decoding': {},
        'firebase_init': {},
        'errors': []
    }

    # Check environment variables
    env_vars = [
        'FIREBASE_SERVICE_ACCOUNT_BASE64',  # Full service account JSON (PREFERRED)
        'FIREBASE_PROJECT_ID',
        'FIREBASE_PRIVATE_KEY_BASE64',  # Just the private key
        'FIREBASE_PRIVATE_KEY',
        'FIREBASE_CLIENT_EMAIL',
        'FIREBASE_CLIENT_ID',
        'FIREBASE_PRIVATE_KEY_ID'
    ]

    for var in env_vars:
        value = os.getenv(var, '')
        debug_info['env_vars'][var] = {
            'exists': bool(value),
            'length': len(value) if value else 0,
            'first_10': value[:10] if value else 'NOT SET',
            'last_10': value[-10:] if value else 'NOT SET'
        }

    # Check for the full service account JSON first (PREFERRED)
    service_account_base64 = os.getenv('FIREBASE_SERVICE_ACCOUNT_BASE64', '')
    if service_account_base64:
        debug_info['service_account'] = {
            'found': True,
            'length': len(service_account_base64),
            'message': '✅ FIREBASE_SERVICE_ACCOUNT_BASE64 found (GOOD!)'
        }
        try:
            # Try to decode and parse it
            import json
            decoded = base64.b64decode(service_account_base64).decode('utf-8')
            parsed = json.loads(decoded)
            debug_info['service_account']['valid_json'] = True
            debug_info['service_account']['project_id'] = parsed.get('project_id')
            debug_info['service_account']['has_private_key'] = bool(parsed.get('private_key'))
        except Exception as e:
            debug_info['service_account']['error'] = str(e)
    else:
        debug_info['service_account'] = {
            'found': False,
            'message': '❌ FIREBASE_SERVICE_ACCOUNT_BASE64 not found - ADD THIS TO VERCEL!'
        }

    # Try to decode the base64 key (fallback method)
    private_key_base64 = os.getenv('FIREBASE_PRIVATE_KEY_BASE64', '')
    if private_key_base64:
        debug_info['decoding'] = {}
        debug_info['decoding']['base64_found'] = True
        debug_info['decoding']['base64_length'] = len(private_key_base64)

        # Check for common issues
        debug_info['decoding']['has_spaces'] = ' ' in private_key_base64
        debug_info['decoding']['has_newlines'] = '\n' in private_key_base64
        debug_info['decoding']['starts_with'] = private_key_base64[:20]
        debug_info['decoding']['ends_with'] = private_key_base64[-20:]

        try:
            # Try to decode
            decoded_bytes = base64.b64decode(private_key_base64)
            debug_info['decoding']['decode_success'] = True
            debug_info['decoding']['decoded_bytes_length'] = len(decoded_bytes)

            # Try to convert to string
            private_key = decoded_bytes.decode('utf-8')
            debug_info['decoding']['utf8_decode_success'] = True
            debug_info['decoding']['key_length'] = len(private_key)
            debug_info['decoding']['key_starts_with'] = private_key[:50] if private_key else 'EMPTY'
            debug_info['decoding']['key_ends_with'] = private_key[-50:] if private_key else 'EMPTY'
            debug_info['decoding']['has_begin_marker'] = '-----BEGIN' in private_key
            debug_info['decoding']['has_end_marker'] = '-----END' in private_key

        except base64.binascii.Error as e:
            debug_info['errors'].append(f"Base64 decode error: {str(e)}")
            debug_info['decoding']['decode_success'] = False
        except UnicodeDecodeError as e:
            debug_info['errors'].append(f"UTF-8 decode error: {str(e)}")
            debug_info['decoding']['utf8_decode_success'] = False
        except Exception as e:
            debug_info['errors'].append(f"Unknown decode error: {str(e)}")
    else:
        debug_info['decoding']['base64_found'] = False

    # Try Firebase initialization
    try:
        import firebase_admin
        from firebase_admin import credentials

        debug_info['firebase_init']['firebase_admin_imported'] = True

        # Check if already initialized
        try:
            existing_app = firebase_admin.get_app()
            debug_info['firebase_init']['existing_app'] = True
            debug_info['firebase_init']['app_name'] = existing_app.name
        except ValueError:
            debug_info['firebase_init']['existing_app'] = False

            # Try to initialize
            if private_key_base64 and 'private_key' in locals():
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

                debug_info['firebase_init']['config_created'] = True
                debug_info['firebase_init']['has_project_id'] = bool(firebase_config.get('project_id'))
                debug_info['firebase_init']['has_private_key'] = bool(firebase_config.get('private_key'))
                debug_info['firebase_init']['has_client_email'] = bool(firebase_config.get('client_email'))

                try:
                    cred = credentials.Certificate(firebase_config)
                    debug_info['firebase_init']['credential_created'] = True

                    app = firebase_admin.initialize_app(cred)
                    debug_info['firebase_init']['app_initialized'] = True
                    debug_info['firebase_init']['app_name'] = app.name

                    # Clean up for next test
                    firebase_admin.delete_app(app)

                except Exception as e:
                    debug_info['errors'].append(f"Firebase init error: {str(e)}")
                    debug_info['firebase_init']['credential_created'] = False
            else:
                debug_info['firebase_init']['config_created'] = False
                debug_info['errors'].append("No private key available for Firebase config")

    except ImportError as e:
        debug_info['errors'].append(f"Import error: {str(e)}")
        debug_info['firebase_init']['firebase_admin_imported'] = False
    except Exception as e:
        debug_info['errors'].append(f"Firebase error: {str(e)}")

    # Test Firestore availability
    try:
        from app.firestore_db import firestore_db
        debug_info['firestore'] = {
            'available': firestore_db.is_available(),
            '_available_flag': firestore_db._available
        }
    except Exception as e:
        debug_info['errors'].append(f"Firestore check error: {str(e)}")
        debug_info['firestore'] = {'available': False, 'error': str(e)}

    # Add summary and recommendations
    debug_info['summary'] = {
        'firebase_ready': False,
        'firestore_ready': False,
        'action_required': []
    }

    # Check if Firebase can be initialized
    if service_account_base64:
        if 'valid_json' in debug_info.get('service_account', {}) and debug_info['service_account']['valid_json']:
            debug_info['summary']['firebase_ready'] = True
            debug_info['summary']['message'] = '✅ Firebase configuration looks good!'
        else:
            debug_info['summary']['action_required'].append('Fix FIREBASE_SERVICE_ACCOUNT_BASE64 value')
    else:
        debug_info['summary']['action_required'].append(
            '🚨 ADD FIREBASE_SERVICE_ACCOUNT_BASE64 to Vercel Environment Variables!'
        )
        debug_info['summary']['action_required'].append(
            'Copy the value from .env.production (line 6) - it starts with eyJ0eXBlIjo...'
        )
        debug_info['summary']['action_required'].append(
            'It should be 3144 characters long'
        )

    # Check Firestore status
    if debug_info.get('firestore', {}).get('available'):
        debug_info['summary']['firestore_ready'] = True
    else:
        if not debug_info['summary']['firebase_ready']:
            debug_info['summary']['action_required'].append('Fix Firebase configuration first')
        else:
            debug_info['summary']['action_required'].append('Check Firestore is enabled in Google Cloud Console')

    return jsonify(debug_info)