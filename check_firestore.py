#!/usr/bin/env python3
"""
Check what's in Firestore
"""

import os
os.environ['FLASK_APP'] = 'app'

from app import create_app
from app.firestore_db import firestore_db

app = create_app()
with app.app_context():
    print("Checking Firestore data...")
    print("=" * 50)

    # Get dev user
    user = firestore_db.get_user_by_username('dev')
    if user:
        print(f"✅ User 'dev' found: {user['id']}")

        # Get all zines for dev
        zines = firestore_db.get_user_zines(user['id'])
        print(f"\nZines for user 'dev' ({len(zines)} total):")
        for zine in zines:
            print(f"  - {zine['title']} (slug: {zine['slug']}, status: {zine['status']})")

        # Check specific zine
        second_zine = firestore_db.get_zine_by_slug(user['id'], 'second')
        if second_zine:
            print(f"\n✅ Zine 'second' exists!")
            print(f"   ID: {second_zine['id']}")
            print(f"   Status: {second_zine['status']}")

            # Get pages
            pages = firestore_db.get_zine_pages(second_zine['id'])
            print(f"   Pages: {len(pages)}")
        else:
            print("\n❌ Zine 'second' NOT FOUND")
    else:
        print("❌ User 'dev' not found")