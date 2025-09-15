import sys
import os
sys.path.insert(0, '/Users/adnanakil/Documents/Projects/Archgest/zine-app')
os.chdir('/Users/adnanakil/Documents/Projects/Archgest/zine-app')

from app import create_app

app = create_app()
with app.app_context():
    from app.firestore_db import firestore_db
    
    # Check the dev user
    dev_user = firestore_db.get_user_by_username('dev')
    if dev_user:
        print(f"Dev user found: {dev_user['username']} (ID: {dev_user['id']})")
        
        # Check all zines for dev user
        all_zines = firestore_db.get_user_zines(dev_user['id'])
        print(f"\nAll zines for dev user:")
        for zine in all_zines:
            print(f"  - {zine.get('title')} (slug: {zine.get('slug')}, status: {zine.get('status')})")
        
        # Check for birding zine
        birding = firestore_db.get_zine_by_slug(dev_user['id'], 'birding')
        if birding:
            print(f"\nBirding zine details:")
            print(f"  ID: {birding['id']}")
            print(f"  Title: {birding.get('title')}")
            print(f"  Status: {birding.get('status')}")
            print(f"  Creator ID: {birding.get('creator_id')}")
