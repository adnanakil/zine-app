"""
Firestore database integration for Zine app
Replaces SQLAlchemy with Firebase Firestore for persistent storage on Vercel
"""

from firebase_admin import firestore
from datetime import datetime
import uuid
from werkzeug.security import generate_password_hash, check_password_hash


class FirestoreDB:
    def __init__(self):
        self.db = firestore.client()

    # User operations
    def create_user(self, username, email, firebase_uid, password=None):
        """Create a new user in Firestore"""
        user_id = str(uuid.uuid4())
        user_data = {
            'id': user_id,
            'username': username,
            'email': email,
            'firebase_uid': firebase_uid,
            'created_at': datetime.utcnow(),
            'bio': '',
            'avatar_url': None,
            'followers_count': 0,
            'following_count': 0,
            'email_notifications': True
        }

        if password:
            user_data['password_hash'] = generate_password_hash(password)

        self.db.collection('users').document(user_id).set(user_data)
        return user_data

    def get_user_by_id(self, user_id):
        """Get user by ID"""
        doc = self.db.collection('users').document(user_id).get()
        return doc.to_dict() if doc.exists else None

    def get_user_by_username(self, username):
        """Get user by username"""
        users = self.db.collection('users').where('username', '==', username).limit(1).get()
        return users[0].to_dict() if users else None

    def get_user_by_email(self, email):
        """Get user by email"""
        users = self.db.collection('users').where('email', '==', email).limit(1).get()
        return users[0].to_dict() if users else None

    def get_user_by_firebase_uid(self, firebase_uid):
        """Get user by Firebase UID"""
        users = self.db.collection('users').where('firebase_uid', '==', firebase_uid).limit(1).get()
        return users[0].to_dict() if users else None

    def update_user(self, user_id, data):
        """Update user data"""
        self.db.collection('users').document(user_id).update(data)

    # Zine operations
    def create_zine(self, creator_id, title, slug, description='', status='draft'):
        """Create a new zine"""
        zine_id = str(uuid.uuid4())
        zine_data = {
            'id': zine_id,
            'creator_id': creator_id,
            'title': title,
            'slug': slug,
            'description': description,
            'status': status,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'published_at': datetime.utcnow() if status == 'published' else None,
            'views_count': 0,
            'likes_count': 0,
            'unique_readers': 0,
            'avg_read_time': 0,
            'enable_pdf': False,
            'format': 'A5'
        }

        self.db.collection('zines').document(zine_id).set(zine_data)
        return zine_data

    def get_zine_by_id(self, zine_id):
        """Get zine by ID"""
        doc = self.db.collection('zines').document(zine_id).get()
        return doc.to_dict() if doc.exists else None

    def get_zine_by_slug(self, creator_id, slug):
        """Get zine by creator and slug"""
        zines = self.db.collection('zines')\
            .where('creator_id', '==', creator_id)\
            .where('slug', '==', slug)\
            .limit(1).get()
        return zines[0].to_dict() if zines else None

    def get_user_zines(self, creator_id, status=None):
        """Get all zines by a user"""
        query = self.db.collection('zines').where('creator_id', '==', creator_id)
        if status:
            query = query.where('status', '==', status)
        query = query.order_by('created_at', direction=firestore.Query.DESCENDING)
        return [doc.to_dict() for doc in query.get()]

    def get_published_zines(self, limit=20):
        """Get recently published zines"""
        query = self.db.collection('zines')\
            .where('status', '==', 'published')\
            .order_by('published_at', direction=firestore.Query.DESCENDING)\
            .limit(limit)
        return [doc.to_dict() for doc in query.get()]

    def update_zine(self, zine_id, data):
        """Update zine data"""
        data['updated_at'] = datetime.utcnow()
        self.db.collection('zines').document(zine_id).update(data)

    def delete_zine(self, zine_id):
        """Delete a zine and all its pages"""
        # Delete all pages first
        pages = self.db.collection('pages').where('zine_id', '==', zine_id).get()
        for page in pages:
            page.reference.delete()

        # Delete the zine
        self.db.collection('zines').document(zine_id).delete()

    # Page operations
    def create_page(self, zine_id, order=0, content=None, template='blank'):
        """Create a new page"""
        page_id = str(uuid.uuid4())
        page_data = {
            'id': page_id,
            'zine_id': zine_id,
            'order': order,
            'content': content or {'blocks': []},
            'template': template,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

        self.db.collection('pages').document(page_id).set(page_data)
        return page_data

    def get_page_by_id(self, page_id):
        """Get page by ID"""
        doc = self.db.collection('pages').document(page_id).get()
        return doc.to_dict() if doc.exists else None

    def get_zine_pages(self, zine_id):
        """Get all pages for a zine"""
        query = self.db.collection('pages')\
            .where('zine_id', '==', zine_id)\
            .order_by('order')
        return [doc.to_dict() for doc in query.get()]

    def update_page(self, page_id, data):
        """Update page data"""
        data['updated_at'] = datetime.utcnow()
        self.db.collection('pages').document(page_id).update(data)

    def delete_page(self, page_id):
        """Delete a page"""
        self.db.collection('pages').document(page_id).delete()

    # Follow operations
    def follow_user(self, follower_id, followed_id):
        """Follow a user"""
        follow_id = f"{follower_id}_{followed_id}"
        follow_data = {
            'id': follow_id,
            'follower_id': follower_id,
            'followed_id': followed_id,
            'created_at': datetime.utcnow()
        }

        self.db.collection('follows').document(follow_id).set(follow_data)

        # Update counts
        follower = self.get_user_by_id(follower_id)
        followed = self.get_user_by_id(followed_id)

        if follower:
            self.update_user(follower_id, {'following_count': follower.get('following_count', 0) + 1})
        if followed:
            self.update_user(followed_id, {'followers_count': followed.get('followers_count', 0) + 1})

    def unfollow_user(self, follower_id, followed_id):
        """Unfollow a user"""
        follow_id = f"{follower_id}_{followed_id}"
        self.db.collection('follows').document(follow_id).delete()

        # Update counts
        follower = self.get_user_by_id(follower_id)
        followed = self.get_user_by_id(followed_id)

        if follower:
            self.update_user(follower_id, {'following_count': max(0, follower.get('following_count', 0) - 1)})
        if followed:
            self.update_user(followed_id, {'followers_count': max(0, followed.get('followers_count', 0) - 1)})

    def is_following(self, follower_id, followed_id):
        """Check if user is following another user"""
        follow_id = f"{follower_id}_{followed_id}"
        doc = self.db.collection('follows').document(follow_id).get()
        return doc.exists

    def get_followers(self, user_id):
        """Get all followers of a user"""
        query = self.db.collection('follows').where('followed_id', '==', user_id)
        followers = []
        for doc in query.get():
            follower_data = doc.to_dict()
            follower = self.get_user_by_id(follower_data['follower_id'])
            if follower:
                followers.append(follower)
        return followers

    def get_following(self, user_id):
        """Get all users that a user is following"""
        query = self.db.collection('follows').where('follower_id', '==', user_id)
        following = []
        for doc in query.get():
            follow_data = doc.to_dict()
            followed = self.get_user_by_id(follow_data['followed_id'])
            if followed:
                following.append(followed)
        return following

    # Analytics operations
    def track_view(self, zine_id, user_id=None, session_id=None, referrer=None):
        """Track a zine view"""
        analytics_id = str(uuid.uuid4())
        analytics_data = {
            'id': analytics_id,
            'zine_id': zine_id,
            'user_id': user_id,
            'session_id': session_id,
            'event_type': 'view',
            'referrer': referrer,
            'created_at': datetime.utcnow()
        }

        self.db.collection('analytics').document(analytics_id).set(analytics_data)

        # Update zine view count
        zine = self.get_zine_by_id(zine_id)
        if zine:
            self.update_zine(zine_id, {'views_count': zine.get('views_count', 0) + 1})

    def track_read_time(self, zine_id, session_id, read_time):
        """Update read time for a session"""
        query = self.db.collection('analytics')\
            .where('zine_id', '==', zine_id)\
            .where('session_id', '==', session_id)\
            .where('event_type', '==', 'view')\
            .limit(1)

        docs = query.get()
        if docs:
            doc = docs[0]
            doc.reference.update({'read_time': read_time})

    # Initialize demo data
    def init_demo_data(self):
        """Initialize demo data if database is empty"""
        # Check if demo user exists
        demo_user = self.get_user_by_username('dev')

        if not demo_user:
            # Create demo user
            demo_user = self.create_user(
                username='dev',
                email='dev@archgest.com',
                firebase_uid='demo_firebase_uid',
                password='demo123'
            )

            # Create demo zine
            demo_zine = self.create_zine(
                creator_id=demo_user['id'],
                title='BestBest',
                slug='bestbest',
                description='A sample zine',
                status='published'
            )

            # Create demo page with green square
            self.create_page(
                zine_id=demo_zine['id'],
                order=0,
                content={
                    'blocks': [
                        {
                            'type': 'shape',
                            'x': '150px',
                            'y': '200px',
                            'width': '100px',
                            'height': '100px',
                            'style': {
                                'background': '#4CAF50',
                                'borderRadius': '0'
                            }
                        }
                    ]
                }
            )

            # Also create the sample-zine for demo route
            sample_zine = self.create_zine(
                creator_id=demo_user['id'],
                title='Sample Zine',
                slug='sample-zine',
                description='This is a demo zine to showcase the viewer',
                status='published'
            )

            # Create sample pages
            self.create_page(
                zine_id=sample_zine['id'],
                order=0,
                content={
                    "elements": [
                        {
                            "type": "image",
                            "src": "https://images.unsplash.com/photo-1755868679492-a708c7626971?q=80&w=985&auto=format&fit=crop",
                            "x": 0,
                            "y": 0,
                            "width": "100%",
                            "height": "100%"
                        },
                        {
                            "type": "text",
                            "content": "<h1 style='color: white; text-shadow: 2px 2px 8px rgba(0,0,0,0.9); font-size: 2.5em;'>Welcome to Zines!</h1>",
                            "x": 20,
                            "y": 80,
                            "width": "90%",
                            "height": 200
                        }
                    ]
                }
            )


# Global instance
firestore_db = FirestoreDB()