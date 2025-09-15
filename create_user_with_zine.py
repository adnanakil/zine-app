import sys
import os
sys.path.insert(0, '/Users/adnanakil/Documents/Projects/Archgest/zine-app')
os.chdir('/Users/adnanakil/Documents/Projects/Archgest/zine-app')

from app import create_app
from datetime import datetime
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    from app.firestore_db import firestore_db
    
    # First, check what users exist
    print("\nChecking existing users...")
    users_ref = firestore_db._get_db().collection('users')
    users = users_ref.limit(5).get()
    for user in users:
        user_data = user.to_dict()
        print(f"  User: {user_data.get('username')} (ID: {user_data.get('id')})")
    
    # Create or update user 'adnanakil'
    existing = firestore_db.get_user_by_username('adnanakil')
    if not existing:
        print("\nCreating user 'adnanakil'...")
        user_data = {
            'id': 'user_adnanakil',
            'username': 'adnanakil',
            'email': 'adnan@example.com',
            'password_hash': generate_password_hash('password123'),
            'bio': 'Nature enthusiast and bird watcher',
            'created_at': datetime.utcnow(),
            'followers_count': 0,
            'following_count': 0,
            'email_notifications': True
        }
        firestore_db._get_db().collection('users').document(user_data['id']).set(user_data)
        print(f"Created user: {user_data['username']}")
    else:
        print(f"\nUser 'adnanakil' already exists with ID: {existing['id']}")
        user_data = existing
    
    # Check zines for this user
    print(f"\nChecking zines for user {user_data['id']}...")
    zines = firestore_db.get_user_zines(user_data['id'])
    for zine in zines:
        print(f"  Zine: {zine.get('title')} (slug: {zine.get('slug')}, status: {zine.get('status')})")
    
    # Update the birding zine if it exists
    birding = firestore_db.get_zine_by_slug(user_data['id'], 'birding')
    if birding:
        print(f"\nBirding zine found with ID: {birding['id']}")
        print(f"Current status: {birding.get('status')}")
    else:
        print("\nNo birding zine found")
