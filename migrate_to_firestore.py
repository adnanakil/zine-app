#!/usr/bin/env python3
"""
Migrate zine data to Firestore for persistent storage
"""

import os
import sys
os.environ['FLASK_APP'] = 'app'

from app import create_app
from app.firestore_db import firestore_db

def migrate_zines():
    """Create the dev user and second zine in Firestore"""
    print("🚀 Migrating data to Firestore...")
    print("=" * 50)

    # Check if Firestore is available
    if not firestore_db.is_available():
        print("❌ Firestore is not available. Please ensure:")
        print("   1. Firestore API is enabled")
        print("   2. Database is created")
        print("   3. Credentials are configured")
        return False

    print("✅ Firestore is available!")

    # Check/Create dev user
    print("\n=== Checking for 'dev' user ===")
    user = firestore_db.get_user_by_username('dev')

    if not user:
        print("Creating 'dev' user...")
        user = firestore_db.create_user(
            username='dev',
            email='dev@archgest.com',
            firebase_uid='dev_firebase_uid',
            password='demo123'
        )
        print(f"✅ Created user 'dev' with ID: {user['id']}")
    else:
        print(f"✅ User 'dev' already exists with ID: {user['id']}")

    # Check/Create 'second' zine
    print("\n=== Checking for 'second' zine ===")
    zine = firestore_db.get_zine_by_slug(user['id'], 'second')

    if not zine:
        print("Creating 'second' zine...")
        zine = firestore_db.create_zine(
            creator_id=user['id'],
            title='Second Zine',
            slug='second',
            description='My second zine creation',
            status='published'
        )
        print(f"✅ Created zine 'second' with ID: {zine['id']}")

        # Create a sample page
        print("Creating sample page...")
        page = firestore_db.create_page(
            zine_id=zine['id'],
            order=0,
            content={
                'elements': [
                    {
                        'type': 'text',
                        'content': '<h1>Second Zine</h1><p>Welcome to my second zine!</p>',
                        'x': 20,
                        'y': 100,
                        'width': 360,
                        'height': 200
                    },
                    {
                        'type': 'shape',
                        'x': '150px',
                        'y': '300px',
                        'width': '100px',
                        'height': '100px',
                        'style': {
                            'background': '#2196F3',
                            'borderRadius': '50%'
                        }
                    }
                ]
            }
        )
        print(f"✅ Created page with ID: {page['id']}")
    else:
        print(f"✅ Zine 'second' already exists with ID: {zine['id']}")

    # Also ensure the BestBest zine exists
    print("\n=== Checking for 'bestbest' zine ===")
    bestbest = firestore_db.get_zine_by_slug(user['id'], 'bestbest')

    if not bestbest:
        print("Creating 'bestbest' zine...")
        bestbest = firestore_db.create_zine(
            creator_id=user['id'],
            title='BestBest',
            slug='bestbest',
            description='A sample zine',
            status='published'
        )
        print(f"✅ Created zine 'bestbest' with ID: {bestbest['id']}")

        # Create demo page with green square
        page = firestore_db.create_page(
            zine_id=bestbest['id'],
            order=0,
            content={
                'blocks': [
                    {
                        'type': 'shape',
                        'x': '150px',
                        'y': '200px',
                        'width': '100px',
                        'height': '100px',
                        'style': {
                            'background': '#4CAF50',
                            'borderRadius': '0'
                        }
                    }
                ]
            }
        )
        print(f"✅ Created page for bestbest")
    else:
        print(f"✅ Zine 'bestbest' already exists")

    print("\n" + "=" * 50)
    print("✅ Migration completed successfully!")
    print("\nYour zines should now be accessible at:")
    print("  - https://archgest.com/dev/second")
    print("  - https://archgest.com/dev/bestbest")
    print("\nData is now stored in Firestore and will persist across deployments!")

    return True

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        success = migrate_zines()
        sys.exit(0 if success else 1)