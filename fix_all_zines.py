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
        
        # Find all zines with integer creator_id
        zines_ref = firestore_db._get_db().collection('zines')
        all_zines = zines_ref.get()
        
        fixed_count = 0
        for zine_doc in all_zines:
            zine_data = zine_doc.to_dict()
            creator_id = zine_data.get('creator_id')
            
            # Check if creator_id is an integer or string integer
            if isinstance(creator_id, int) or (isinstance(creator_id, str) and creator_id.isdigit()):
                print(f"\nFixing zine: {zine_data.get('title')} (slug: {zine_data.get('slug')})")
                print(f"  Old creator_id: {creator_id}")
                
                # Update to the adnanakil user
                zine_doc.reference.update({
                    'creator_id': user['id']
                })
                print(f"  New creator_id: {user['id']}")
                fixed_count += 1
        
        print(f"\n✅ Fixed {fixed_count} zines total")
        
        # List all zines now belonging to adnanakil
        user_zines = firestore_db.get_user_zines(user['id'])
        print(f"\n📚 All zines for 'adnanakil':")
        for zine in user_zines:
            print(f"  - {zine.get('title')} (/{user['username']}/{zine.get('slug')})")
