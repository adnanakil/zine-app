#!/usr/bin/env python3
"""
Fix script to create the missing zine at /dev/second
Usage: python fix_zine.py
"""

import os
import sys
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def create_zine_firestore():
    """Create the missing zine in Firestore"""
    print("=== Creating zine in Firestore ===")

    try:
        from app.firestore_db import firestore_db

        if not firestore_db.is_available():
            print("❌ Firestore is not available")
            return False

        print("✅ Firestore is available")

        # Check if user 'dev' exists, create if not
        user = firestore_db.get_user_by_username('dev')
        if not user:
            print("Creating user 'dev'...")
            user = firestore_db.create_user(
                username='dev',
                email='dev@archgest.com',
                firebase_uid='dev_firebase_uid'
            )
            print(f"✅ User 'dev' created: {user['id']}")
        else:
            print(f"✅ User 'dev' found: {user['id']}")

        # Check if zine already exists
        existing_zine = firestore_db.get_zine_by_slug(user['id'], 'second')
        if existing_zine:
            print(f"⚠️ Zine 'second' already exists: {existing_zine['id']}")
            return True

        # Create the zine
        print("Creating zine 'second'...")
        zine = firestore_db.create_zine(
            creator_id=user['id'],
            title='Second Zine',
            slug='second',
            description='A second demo zine for testing',
            status='published'
        )
        print(f"✅ Zine 'second' created: {zine['id']}")

        # Create a sample page
        print("Creating sample page...")
        page = firestore_db.create_page(
            zine_id=zine['id'],
            order=0,
            content={
                'blocks': [
                    {
                        'type': 'text',
                        'x': '50px',
                        'y': '100px',
                        'width': '300px',
                        'height': '100px',
                        'content': '<h1>Welcome to the Second Zine!</h1><p>This zine was recreated to fix the 404 error.</p>',
                        'style': {
                            'color': '#333',
                            'textAlign': 'center'
                        }
                    },
                    {
                        'type': 'shape',
                        'x': '150px',
                        'y': '250px',
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
        print(f"✅ Sample page created: {page['id']}")

        print(f"🎉 Zine is now available at: /dev/second")
        return True

    except Exception as e:
        print(f"❌ Error creating zine in Firestore: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_zine_sqlalchemy():
    """Create the missing zine in SQLAlchemy"""
    print("\n=== Creating zine in SQLAlchemy ===")

    try:
        from app import create_app
        from app.models import User, Zine, Page
        from app import db

        app = create_app()

        with app.app_context():
            # Check if user 'dev' exists, create if not
            user = User.query.filter_by(username='dev').first()
            if not user:
                print("Creating user 'dev'...")
                user = User(
                    username='dev',
                    email='dev@archgest.com',
                    firebase_uid='dev_firebase_uid',
                    display_name='Dev User'
                )
                db.session.add(user)
                db.session.commit()
                print(f"✅ User 'dev' created: {user.id}")
            else:
                print(f"✅ User 'dev' found: {user.id}")

            # Check if zine already exists
            existing_zine = Zine.query.filter_by(creator_id=user.id, slug='second').first()
            if existing_zine:
                print(f"⚠️ Zine 'second' already exists: {existing_zine.id}")
                return True

            # Create the zine
            print("Creating zine 'second'...")
            zine = Zine(
                creator_id=user.id,
                title='Second Zine',
                slug='second',
                description='A second demo zine for testing',
                status='published',
                published_at=datetime.utcnow()
            )
            db.session.add(zine)
            db.session.commit()
            print(f"✅ Zine 'second' created: {zine.id}")

            # Create a sample page
            print("Creating sample page...")
            page = Page(
                zine_id=zine.id,
                order=0,
                content={
                    'blocks': [
                        {
                            'type': 'text',
                            'x': '50px',
                            'y': '100px',
                            'width': '300px',
                            'height': '100px',
                            'content': '<h1>Welcome to the Second Zine!</h1><p>This zine was recreated to fix the 404 error.</p>',
                            'style': {
                                'color': '#333',
                                'textAlign': 'center'
                            }
                        },
                        {
                            'type': 'shape',
                            'x': '150px',
                            'y': '250px',
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
            db.session.add(page)
            db.session.commit()
            print(f"✅ Sample page created: {page.id}")

            print(f"🎉 Zine is now available at: /dev/second")
            return True

    except Exception as e:
        print(f"❌ Error creating zine in SQLAlchemy: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function to create the missing zine"""
    print("🔧 Creating missing zine at /dev/second")
    print("=" * 50)

    # Try Firestore first, fall back to SQLAlchemy
    firestore_success = create_zine_firestore()

    if not firestore_success:
        print("Firestore failed, trying SQLAlchemy...")
        sqlalchemy_success = create_zine_sqlalchemy()

        if not sqlalchemy_success:
            print("❌ Failed to create zine in both databases")
            return False

    print("\n✅ Zine creation completed successfully!")
    print("The zine should now be accessible at: /dev/second")

    return True

if __name__ == "__main__":
    main()