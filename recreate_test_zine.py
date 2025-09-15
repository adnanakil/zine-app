#!/usr/bin/env python3
"""
Recreate the test zine in Firestore
Run this whenever the zine goes missing
"""

import os
os.environ['FLASK_APP'] = 'app'

from app import create_app
from app.firestore_db import firestore_db

def recreate_test_zine():
    """Recreate the test zine"""
    print("🚀 Recreating test zine in Firestore...")

    if not firestore_db.is_available():
        print("❌ Firestore is not available")
        return False

    # Get or create dev user
    user = firestore_db.get_user_by_username('dev')
    if not user:
        print("Creating dev user...")
        user = firestore_db.create_user(
            username='dev',
            email='dev@archgest.com',
            firebase_uid='dev_firebase_uid',
            password='demo123'
        )

    print(f"✅ User 'dev' ID: {user['id']}")

    # Check if test zine exists
    test_zine = firestore_db.get_zine_by_slug(user['id'], 'test')

    if not test_zine:
        print("Creating 'test' zine...")
        test_zine = firestore_db.create_zine(
            creator_id=user['id'],
            title='Test Zine',
            slug='test',
            description='Testing zine creation',
            status='published'
        )
        print(f"✅ Created zine 'test' with ID: {test_zine['id']}")

        # Create a page
        page = firestore_db.create_page(
            zine_id=test_zine['id'],
            order=0,
            content={
                'elements': [
                    {
                        'type': 'text',
                        'content': '<h1>Test Zine</h1><p>This is a test zine!</p>',
                        'x': 20,
                        'y': 100,
                        'width': 360,
                        'height': 200
                    }
                ]
            }
        )
        print(f"✅ Created page for test zine")
    else:
        print(f"✅ Zine 'test' already exists with ID: {test_zine['id']}")

    print("\n✅ Test zine is available at: https://archgest.com/dev/test")
    return True

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        recreate_test_zine()