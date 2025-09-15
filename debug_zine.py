#!/usr/bin/env python3
"""
Debug script to check if a zine exists in the database
Usage: python debug_zine.py
"""

import os
import sys
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def check_firestore():
    """Check if zine exists in Firestore"""
    print("=== Checking Firestore ===")

    try:
        from app.firestore_db import firestore_db

        if not firestore_db.is_available():
            print("❌ Firestore is not available")
            return False

        print("✅ Firestore is available")

        # Check if user 'dev' exists
        user = firestore_db.get_user_by_username('dev')
        if not user:
            print("❌ User 'dev' not found in Firestore")
            return False

        print(f"✅ User 'dev' found: {user['id']}")

        # Check if zine with slug 'second' exists
        zine = firestore_db.get_zine_by_slug(user['id'], 'second')
        if not zine:
            print("❌ Zine 'second' not found in Firestore")
            return False

        print(f"✅ Zine 'second' found: {zine['id']}")
        print(f"   Title: {zine['title']}")
        print(f"   Status: {zine['status']}")
        print(f"   Created: {zine['created_at']}")

        return True

    except Exception as e:
        print(f"❌ Error checking Firestore: {e}")
        return False

def check_sqlalchemy():
    """Check if zine exists in SQLAlchemy"""
    print("\n=== Checking SQLAlchemy ===")

    try:
        from app import create_app
        from app.models import User, Zine

        app = create_app()

        with app.app_context():
            # Check if user 'dev' exists
            user = User.query.filter_by(username='dev').first()
            if not user:
                print("❌ User 'dev' not found in SQLAlchemy")
                return False

            print(f"✅ User 'dev' found: {user.id}")

            # Check if zine with slug 'second' exists
            zine = Zine.query.filter_by(creator_id=user.id, slug='second').first()
            if not zine:
                print("❌ Zine 'second' not found in SQLAlchemy")
                return False

            print(f"✅ Zine 'second' found: {zine.id}")
            print(f"   Title: {zine.title}")
            print(f"   Status: {zine.status}")
            print(f"   Created: {zine.created_at}")

            return True

    except Exception as e:
        print(f"❌ Error checking SQLAlchemy: {e}")
        return False

def main():
    """Main function to check both databases"""
    print("🔍 Checking for zine at /dev/second")
    print("=" * 50)

    firestore_found = check_firestore()
    sqlalchemy_found = check_sqlalchemy()

    print("\n=== Summary ===")
    if firestore_found:
        print("✅ Zine found in Firestore")
    elif sqlalchemy_found:
        print("✅ Zine found in SQLAlchemy")
    else:
        print("❌ Zine not found in either database")
        print("💡 Use the fix_zine.py script to create the missing zine")

if __name__ == "__main__":
    main()