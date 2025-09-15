#!/usr/bin/env python3
"""
Convert Firebase private key to base64 for easy environment variable setup
"""

import base64
import json

# Read the service account key file
with open('serviceAccountKey.json', 'r') as f:
    data = json.load(f)

private_key = data['private_key']

# Encode to base64
encoded_key = base64.b64encode(private_key.encode()).decode()

print("="*80)
print("FIREBASE_PRIVATE_KEY_BASE64:")
print("="*80)
print(encoded_key)
print("="*80)
print("\nCopy the above base64 string and set it as FIREBASE_PRIVATE_KEY_BASE64 in Vercel")
print("This avoids any newline/formatting issues")