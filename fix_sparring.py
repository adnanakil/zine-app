import sys
import os
sys.path.insert(0, '/Users/adnanakil/Documents/Projects/Archgest/zine-app')
os.chdir('/Users/adnanakil/Documents/Projects/Archgest/zine-app')

from app import create_app

app = create_app()
with app.app_context():
    from app.firestore_db import firestore_db
    
    # Get the adnanakil user
    user = firestore_db.get_user_by_username('adnanakil')
    if user:
        print(f"Found user 'adnanakil' with ID: {user['id']}")
        
        # Fix the sparring zine
        zines_ref = firestore_db._get_db().collection('zines')
        sparring_query = zines_ref.where('slug', '==', 'sparring').limit(1)
        sparring_docs = sparring_query.get()
        
        if sparring_docs:
            sparring_doc = sparring_docs[0]
            print(f"Found sparring zine, updating creator_id...")
            
            sparring_doc.reference.update({
                'creator_id': user['id']
            })
            
            print(f"✅ Sparring zine now belongs to 'adnanakil'")
            print(f"   URL: https://archgest.com/adnanakil/sparring")
