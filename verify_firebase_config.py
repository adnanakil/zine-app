#!/usr/bin/env python3
"""
Verify Firebase configuration is correct
Run this to test your environment variables before deploying to Vercel
"""

import os
import base64
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.production')

print("=" * 60)
print("FIREBASE CONFIGURATION VERIFICATION")
print("=" * 60)

# Check for the base64 encoded service account
service_account_base64 = os.getenv('FIREBASE_SERVICE_ACCOUNT_BASE64', '').strip()

if not service_account_base64:
    print("❌ FIREBASE_SERVICE_ACCOUNT_BASE64 not found in environment")
    print("   This is required for Vercel deployment!")
    exit(1)

print(f"✅ Found FIREBASE_SERVICE_ACCOUNT_BASE64")
print(f"   Length: {len(service_account_base64)} characters")

# Try to decode it
try:
    # Remove any whitespace
    service_account_base64 = service_account_base64.replace('\n', '').replace('\r', '').replace(' ', '')

    # Decode base64
    decoded_bytes = base64.b64decode(service_account_base64)
    print(f"✅ Base64 decoding successful")
    print(f"   Decoded size: {len(decoded_bytes)} bytes")

    # Parse JSON
    service_account_json = decoded_bytes.decode('utf-8')
    service_account_data = json.loads(service_account_json)
    print(f"✅ JSON parsing successful")

    # Check required fields
    required_fields = {
        'type': 'service_account',
        'project_id': 'archgest-20638',
        'private_key': '-----BEGIN PRIVATE KEY-----',
        'client_email': '@archgest-20638.iam.gserviceaccount.com'
    }

    print("\nVerifying service account fields:")
    all_valid = True

    for field, expected in required_fields.items():
        value = service_account_data.get(field, '')
        if field == 'private_key':
            if expected in value:
                print(f"  ✅ {field}: Contains private key")
            else:
                print(f"  ❌ {field}: Invalid private key format")
                all_valid = False
        elif field == 'client_email':
            if expected in value:
                print(f"  ✅ {field}: {value}")
            else:
                print(f"  ❌ {field}: Invalid email domain")
                all_valid = False
        else:
            if value == expected or (field == 'project_id' and value == expected):
                print(f"  ✅ {field}: {value}")
            else:
                print(f"  ❌ {field}: Expected '{expected}', got '{value}'")
                all_valid = False

    # Check other important fields
    other_fields = ['private_key_id', 'client_id', 'auth_uri', 'token_uri']
    for field in other_fields:
        if service_account_data.get(field):
            print(f"  ✅ {field}: Present")
        else:
            print(f"  ❌ {field}: Missing")
            all_valid = False

    print("\n" + "=" * 60)
    if all_valid:
        print("✅ CONFIGURATION VALID - Ready for Vercel deployment!")
        print("\nNext steps:")
        print("1. Copy the FIREBASE_SERVICE_ACCOUNT_BASE64 value from .env.production")
        print("2. Add it to Vercel Environment Variables")
        print("3. Redeploy your application")
    else:
        print("❌ CONFIGURATION ISSUES DETECTED")
        print("Please check the errors above and fix your configuration")
    print("=" * 60)

except base64.binascii.Error as e:
    print(f"❌ Base64 decode error: {e}")
    print("   Make sure the value is valid base64 without any extra characters")
    exit(1)
except json.JSONDecodeError as e:
    print(f"❌ JSON decode error: {e}")
    print("   The decoded value is not valid JSON")
    exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    exit(1)