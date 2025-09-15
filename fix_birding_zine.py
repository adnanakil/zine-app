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
        
        # Update the birding zine to belong to this user
        zines_ref = firestore_db._get_db().collection('zines')
        birding_query = zines_ref.where('slug', '==', 'birding').limit(1)
        birding_docs = birding_query.get()
        
        if birding_docs:
            birding_doc = birding_docs[0]
            birding_id = birding_doc.id
            print(f"Found birding zine with document ID: {birding_id}")
            
            # Update the creator_id
            birding_doc.reference.update({
                'creator_id': user['id']
            })
            print(f"Updated birding zine creator_id to: {user['id']}")
            
            # Verify the update
            updated = firestore_db.get_zine_by_slug(user['id'], 'birding')
            if updated:
                print(f"\n✅ Successfully updated! Birding zine now belongs to 'adnanakil'")
                print(f"   URL should be: /adnanakil/birding")
            else:
                print("⚠️  Update may not have worked correctly")
    else:
        print("User 'adnanakil' not found!")
