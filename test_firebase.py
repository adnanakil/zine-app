#!/usr/bin/env python3
"""
Test Firebase initialization with base64 encoded key
"""

import os
import base64
from dotenv import load_dotenv

load_dotenv()

# Set the base64 key from our generated value
os.environ['FIREBASE_PRIVATE_KEY_BASE64'] = 'LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCk1JSUV2Z0lCQURBTkJna3Foa2lHOXcwQkFRRUZBQVNDQktnd2dnU2tBZ0VBQW9JQkFRQzkvbG91L3ZvSmpJVVQKVVdmZ2UrT3UzcWZlVG54S0lmNkZpT3l2cGZqVU42cUtzRlhhMkd2V1NFYlB1b0dHWXFUWDNGcngzOUJXanFGRQo0cUswZjdzaklyR0Nrb0RkTjhrbTRZS0J0dmozWmZGWUpQUVZzbUtFVkVveWVOUmFDYTR2MUFFYW9MVlJHdlJDCnhORy90ZHhEWFhWajhwQlhvR1ZJZklHTkFvTy82Y1pmbUJFZ2UrSDl1YjhZMDM0OGpGbFI1aVZPalNtTjY1OWMKdG1yeDUwUEVLVld1c0dYTUQ4bE1iL1V1VmF1eVZYc1owbE1NbUMzQ3JrdGo5WmVodngzVWQ0VWVrZFZnTCtUZQpwUjhMZys1UEhjOFduKzFuRk1NcmlLZ3lJVitKZnNQMUF4Nkl5ZG9BV2d5Sm1DckJmcEQ0WnNsdXhJaUM4bFgrCjEvbXpMQXBWQWdNQkFBRUNnZ0VBQTdxblV5bDhCNDN6aFdLTC9iMm1HcnVTRGV5bEhJdGk3eTlnZmVqRERvbnkKZ0tXMHViRS94SnFja1RLTVI1MU9DNmZ1a21BZDVicGM4MDR1SlY3UWNkWEUwdGJ2VFQyWUVYbWhweUYybDRjdgp0U3d4MTVuWVp5MHZCazNxMVJoQU5xakc4TVV3dnpaejVEcEZaNm1PZU9BRkVDdDYrODFSSlBBVXJEWXl3Yzh3CmZ3aTdkNzRUQzdXb25BZndrOVlsMlNKSTlRYkRCVlRnbnVpeCt6Q3JCK0xwbDM0WEhUOE1RTFFvUlVHQlo0b0oKZnY2Nk1EMW1kcFlBMjVxMGpCMENpL0oxbGdiSnV3bjBuZEtIYUhsb0lLTm1yYndRL1g0TUZMZ3hKaHlFbEVTbApXRFR4dE1HMlF6WElUUmhFK1hkOHRaSnlpYTVJNUxuMjF3OFExdVpLelFLQmdRRHZGai81TEhTWVJTbFZuYVhNClB2eTBjeUFlbmVUUTQrTEtBSVBNL3NVZGoyUGZ0VC9ucUlTVTlXQTNWQy9yT3VaVFNNeE55ZWlEeUpTVWU4dkwKWktuZDR5V1U2S2RESWJYZ0M1d0ZlZ1RLTk1NdGNvd3JIdUhQdXp3b1BoYlJFUkVTTFBJYlhwb2RhV0F3MnJmVwpvK1l1TFlQRCtyY1d2aklHbm53SzE1b0x3d0tCZ1FETGJ3dVNZc1duc3Z2ekQvKzcvRnIzdkxjbDhKanlTUkZtCmpSZTBtQTNmUHhDbzZIUW5QQitCRTZWNCtoblA2aHlmbmdmNVpIZk12YlM1dEhDZCtISExFQm1UeFZUMXlVQzAKWm1rY3I0UzU4OWJBL2ZNOTAxNmV4VnRSeWFhbFpsYnpmR0lZWXVPVGlySEhlVzAzdFh3WE9LVk9BSWE2dlJXVApLM0NWbzYvb0J3S0JnRTNKQldOQ0RXVUZDMStwZkttb3pIckJBZkEwR3AvRHBLTm42M21rWWVrdUg2Wkd4OVhNCncrWGF0MFVKQk5ZWlFacFRFdlV6L1l2eWxEU0MybGtBRlN2MW5PS0hsdk9HWWkvVVZ4eUpDRW5wUko3aXA2dlgKemt2UmRNNzY5RjFzbWdzNXlFTVRVanpEYmVJM0pweVVrbXp2cmZEeS91Sk5XdVZBWnNiNFFrd1ZBb0dCQUlZcApuTk1VeXMrM0xZdjJNQ3owMTdWc1Fza0ZySWlWQWFIRlNTM3ozYW91ZURrODNHV0h0Q3MzSHJqekVCVGJpN2NFCnpMTi91N1pPSWlNYXllNlVpODlrdGNtTHFXVlRMWllMdUNTUDZKT09LVUlyK0wvOFp2bUVwSjRDeENGdXBjZDgKYjJFdnpuQmVWcko3OVRoNU92WkJpRnN4NDZqQnpMbTdPMHVrb1B6L0FvR0JBTDk2U3MzNXBCZXExQVZWelhXWQpJd3gzelBvMjhxVmVrem1VOVdTRTFlWlJHMUN5bVM0emREdkZQSGZkSWxrU2pORCszZVA5QXpiNnlQVHFKNEJYCjQzc3U4dFliS2dyc1I4aEpmcnZZem51dXhwYm1JbGVWckR2MnBCQzJ0aWtpbjBsSTh6SExjWmcwMTdPT01CSVAKTm5udm0zdldMS2lQOXBVZGNvT0NNYlhiCi0tLS0tRU5EIFBSSVZBVEUgS0VZLS0tLS0K'
os.environ['FIREBASE_PROJECT_ID'] = 'archgest-20638'
os.environ['FIREBASE_PRIVATE_KEY_ID'] = '8ae833316034a7746167d59a007a5a40345aed0a'
os.environ['FIREBASE_CLIENT_EMAIL'] = 'firebase-adminsdk-fbsvc@archgest-20638.iam.gserviceaccount.com'
os.environ['FIREBASE_CLIENT_ID'] = '103978167173051622695'
os.environ['FIREBASE_CLIENT_CERT_URL'] = 'https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40archgest-20638.iam.gserviceaccount.com'

print("Testing Firebase initialization...")

try:
    # Test Firebase initialization
    from app.firebase_auth import init_firebase
    firebase_app = init_firebase()

    if firebase_app:
        print("✓ Firebase initialized successfully!")

        # Test Firestore
        print("\nTesting Firestore connection...")
        from firebase_admin import firestore
        db = firestore.client()
        print("✓ Firestore client created successfully!")

        # Try to read/write
        test_doc = db.collection('test').document('test_doc')
        test_doc.set({'test': 'value', 'timestamp': firestore.SERVER_TIMESTAMP})
        print("✓ Successfully wrote to Firestore!")

        doc = test_doc.get()
        if doc.exists:
            print(f"✓ Successfully read from Firestore: {doc.to_dict()}")

        # Clean up test document
        test_doc.delete()
        print("✓ Cleaned up test document")

        print("\n✅ All tests passed! Firebase and Firestore are working correctly.")
    else:
        print("❌ Firebase initialization returned None")

except Exception as e:
    print(f"❌ Error during testing: {e}")
    import traceback
    traceback.print_exc()