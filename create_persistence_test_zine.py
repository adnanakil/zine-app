#!/usr/bin/env python3
"""
Create a test zine to verify persistence on Vercel
"""

import os
import time
os.environ['FLASK_APP'] = 'app'

from app import create_app
from app.firestore_db import firestore_db

def create_persistence_test_zine():
    """Create a test zine with a unique name"""
    print("🚀 Creating persistence test zine in Firestore...")

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

    # Create a unique test zine
    timestamp = int(time.time())
    slug = f'persistence-test-{timestamp}'

    test_zine = firestore_db.create_zine(
        creator_id=user['id'],
        title=f'Persistence Test {timestamp}',
        slug=slug,
        description='Testing Firestore persistence on Vercel',
        status='published'
    )
    print(f"✅ Created zine '{slug}' with ID: {test_zine['id']}")

    # Create a page
    page = firestore_db.create_page(
        zine_id=test_zine['id'],
        order=0,
        content={
            'elements': [
                {
                    'type': 'text',
                    'content': f'<h1>Persistence Test {timestamp}</h1><p>This zine was created to test Firestore persistence on Vercel!</p><p>Created at: {time.strftime("%Y-%m-%d %H:%M:%S")}</p>',
                    'x': 20,
                    'y': 100,
                    'width': 360,
                    'height': 200
                }
            ]
        }
    )
    print(f"✅ Created page for test zine")

    print(f"\n✅ Test zine is available at: https://archgest.com/dev/{slug}")
    return f"https://archgest.com/dev/{slug}"

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        url = create_persistence_test_zine()
        if url:
            print(f"\n📍 URL to test: {url}")