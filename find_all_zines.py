import sys
import os
sys.path.insert(0, '/Users/adnanakil/Documents/Projects/Archgest/zine-app')
os.chdir('/Users/adnanakil/Documents/Projects/Archgest/zine-app')

from app import create_app

app = create_app()
with app.app_context():
    from app.firestore_db import firestore_db
    
    # Get ALL zines
    print("\nALL ZINES IN THE SYSTEM:")
    zines_ref = firestore_db._get_db().collection('zines')
    all_zines = zines_ref.limit(20).get()
    
    for zine_doc in all_zines:
        zine = zine_doc.to_dict()
        print(f"\n  Zine: {zine.get('title')}")
        print(f"    ID: {zine.get('id')}")
        print(f"    Slug: {zine.get('slug')}")
        print(f"    Status: {zine.get('status')}")
        print(f"    Creator ID: {zine.get('creator_id')}")
        
        # If it's the birding zine, show more details
        if zine.get('slug') == 'birding':
            print(f"    *** FOUND BIRDING ZINE ***")
            creator_id = zine.get('creator_id')
            
            # Find the creator
            users_ref = firestore_db._get_db().collection('users')
            creator_doc = users_ref.document(creator_id).get()
            if creator_doc.exists:
                creator = creator_doc.to_dict()
                print(f"    Creator username: {creator.get('username')}")
            else:
                print(f"    Creator not found in users collection!")
