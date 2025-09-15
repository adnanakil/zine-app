import sys
import os
sys.path.insert(0, '/Users/adnanakil/Documents/Projects/Archgest/zine-app')
os.chdir('/Users/adnanakil/Documents/Projects/Archgest/zine-app')

from app import create_app

app = create_app()
with app.app_context():
    from app.firestore_db import firestore_db
    
    # Check if user exists
    user = firestore_db.get_user_by_username('adnanakil')
    print(f"User found: {user}")
    
    if user:
        # Check zines for this user  
        zines = firestore_db.get_user_zines(user['id'], status='published')
        print(f"Published zines: {zines}")
        
        # Check for birding zine specifically
        birding_zine = firestore_db.get_zine_by_slug(user['id'], 'birding')
        print(f"Birding zine: {birding_zine}")
