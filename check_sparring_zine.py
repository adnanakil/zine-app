import sys
import os
sys.path.insert(0, '/Users/adnanakil/Documents/Projects/Archgest/zine-app')
os.chdir('/Users/adnanakil/Documents/Projects/Archgest/zine-app')

from app import create_app

app = create_app()
with app.app_context():
    from app.firestore_db import firestore_db
    
    print("\n=== CHECKING FOR SPARRING ZINE ===")
    
    # Check all zines with slug 'sparring'
    zines_ref = firestore_db._get_db().collection('zines')
    sparring_query = zines_ref.where('slug', '==', 'sparring')
    sparring_docs = sparring_query.get()
    
    for doc in sparring_docs:
        zine = doc.to_dict()
        print(f"\nFound sparring zine:")
        print(f"  ID: {zine.get('id')}")
        print(f"  Title: {zine.get('title')}")
        print(f"  Creator ID: {zine.get('creator_id')}")
        print(f"  Status: {zine.get('status')}")
        
        # Check who the creator is
        creator_id = zine.get('creator_id')
        users_ref = firestore_db._get_db().collection('users')
        
        # Try to find the creator
        if isinstance(creator_id, str):
            creator_doc = users_ref.document(creator_id).get()
            if creator_doc.exists:
                creator = creator_doc.to_dict()
                print(f"  Creator username: {creator.get('username')}")
                print(f"  Creator email: {creator.get('email')}")
            else:
                print(f"  ⚠️ Creator with ID '{creator_id}' not found in users collection!")
    
    print("\n=== CHECKING ALL USERS ===")
    users = users_ref.limit(10).get()
    for user_doc in users:
        user = user_doc.to_dict()
        print(f"  User: {user.get('username')} (ID: {user.get('id')}, email: {user.get('email')})")
