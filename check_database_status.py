#!/usr/bin/env python3
"""
Quick status check script to see which database system is being used
Usage: python check_database_status.py
"""

import os
import sys

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def check_environment():
    """Check environment and database configuration"""
    print("🔍 Database Environment Check")
    print("=" * 40)

    # Check if running on Vercel
    is_vercel = os.getenv('VERCEL') or '/var/task' in os.getcwd()
    print(f"Running on Vercel: {'Yes' if is_vercel else 'No'}")

    # Check Firebase config
    firebase_configured = bool(os.getenv('FIREBASE_PROJECT_ID'))
    print(f"Firebase configured: {'Yes' if firebase_configured else 'No'}")

    # Check database URL
    db_url = os.getenv('DATABASE_URL', 'sqlite:///instance/zines.db')
    print(f"Database URL: {db_url}")

    if is_vercel:
        print("📝 Note: On Vercel, using in-memory SQLite (data resets on deploy)")

    print("\n" + "=" * 40)

def check_firestore_status():
    """Check Firestore availability"""
    print("🔥 Firestore Status")
    print("=" * 20)

    try:
        from app.firestore_db import firestore_db

        if firestore_db.is_available():
            print("✅ Firestore is available and working")

            # Check for demo data
            demo_user = firestore_db.get_user_by_username('dev')
            if demo_user:
                print(f"✅ Demo user 'dev' exists: {demo_user['id']}")

                # Check for zines
                zines = firestore_db.get_user_zines(demo_user['id'])
                print(f"📚 Found {len(zines)} zines for user 'dev':")
                for zine in zines:
                    print(f"  - {zine['slug']}: {zine['title']} ({zine['status']})")

                # Specifically check for 'second' zine
                second_zine = firestore_db.get_zine_by_slug(demo_user['id'], 'second')
                if second_zine:
                    print(f"✅ Target zine 'second' found: {second_zine['id']}")
                else:
                    print("❌ Target zine 'second' NOT found")
            else:
                print("❌ Demo user 'dev' not found")
        else:
            print("❌ Firestore is not available")

    except Exception as e:
        print(f"❌ Error checking Firestore: {e}")

def check_sqlalchemy_status():
    """Check SQLAlchemy status"""
    print("\n💾 SQLAlchemy Status")
    print("=" * 22)

    try:
        from app import create_app
        from app.models import User, Zine

        app = create_app()

        with app.app_context():
            # Check for demo user
            demo_user = User.query.filter_by(username='dev').first()
            if demo_user:
                print(f"✅ Demo user 'dev' exists: {demo_user.id}")

                # Check for zines
                zines = Zine.query.filter_by(creator_id=demo_user.id).all()
                print(f"📚 Found {len(zines)} zines for user 'dev':")
                for zine in zines:
                    print(f"  - {zine.slug}: {zine.title} ({zine.status})")

                # Specifically check for 'second' zine
                second_zine = Zine.query.filter_by(creator_id=demo_user.id, slug='second').first()
                if second_zine:
                    print(f"✅ Target zine 'second' found: {second_zine.id}")
                else:
                    print("❌ Target zine 'second' NOT found")
            else:
                print("❌ Demo user 'dev' not found")

    except Exception as e:
        print(f"❌ Error checking SQLAlchemy: {e}")

def main():
    """Main function"""
    check_environment()
    check_firestore_status()
    check_sqlalchemy_status()

    print("\n💡 Recommendations:")
    print("- If Firestore is available but missing data: run fix_zine.py")
    print("- If only SQLAlchemy works: run fix_zine.py (it will handle fallback)")
    print("- If neither has the zine: run fix_zine.py to create it")

if __name__ == "__main__":
    main()