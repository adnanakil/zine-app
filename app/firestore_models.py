"""
Firestore-compatible User class for Flask-Login
"""
from flask_login import UserMixin
from werkzeug.security import check_password_hash
from app.firestore_db import firestore_db


class FirestoreUser(UserMixin):
    """User model that works with Firestore and Flask-Login"""

    def __init__(self, user_data):
        """Initialize user from Firestore data"""
        if user_data:
            self.id = user_data.get('id')
            self.username = user_data.get('username')
            self.email = user_data.get('email')
            self.firebase_uid = user_data.get('firebase_uid')
            self.password_hash = user_data.get('password_hash')
            self.bio = user_data.get('bio', '')
            self.avatar_url = user_data.get('avatar_url')
            self.display_name = user_data.get('display_name', user_data.get('username', ''))
            self.followers_count = user_data.get('followers_count', 0)
            self.following_count = user_data.get('following_count', 0)
            self.email_notifications = user_data.get('email_notifications', True)
            self.created_at = user_data.get('created_at')
            self._user_data = user_data
        else:
            self.id = None

    @classmethod
    def get(cls, user_id):
        """Get user by ID"""
        user_data = firestore_db.get_user_by_id(user_id)
        return cls(user_data) if user_data else None

    @classmethod
    def get_by_username(cls, username):
        """Get user by username"""
        user_data = firestore_db.get_user_by_username(username)
        return cls(user_data) if user_data else None

    @classmethod
    def get_by_email(cls, email):
        """Get user by email"""
        user_data = firestore_db.get_user_by_email(email)
        return cls(user_data) if user_data else None

    @classmethod
    def get_by_firebase_uid(cls, firebase_uid):
        """Get user by Firebase UID"""
        user_data = firestore_db.get_user_by_firebase_uid(firebase_uid)
        return cls(user_data) if user_data else None

    def check_password(self, password):
        """Check password against hash"""
        if self.password_hash:
            return check_password_hash(self.password_hash, password)
        return False

    def is_following(self, other_user):
        """Check if following another user"""
        if isinstance(other_user, FirestoreUser):
            other_id = other_user.id
        elif isinstance(other_user, dict):
            other_id = other_user.get('id')
        else:
            other_id = str(other_user)

        return firestore_db.is_following(self.id, other_id)

    def follow(self, other_user):
        """Follow another user"""
        if isinstance(other_user, FirestoreUser):
            other_id = other_user.id
        else:
            other_id = str(other_user)

        firestore_db.follow_user(self.id, other_id)

    def unfollow(self, other_user):
        """Unfollow another user"""
        if isinstance(other_user, FirestoreUser):
            other_id = other_user.id
        else:
            other_id = str(other_user)

        firestore_db.unfollow_user(self.id, other_id)

    def get_followers(self):
        """Get all followers"""
        return firestore_db.get_followers(self.id)

    def get_following(self):
        """Get all following"""
        return firestore_db.get_following(self.id)

    @property
    def notifications(self):
        """Return a mock notifications object for compatibility with templates"""
        class MockNotifications:
            def filter_by(self, **kwargs):
                # Return an empty query-like object
                class MockQuery:
                    def count(self):
                        return 0
                    def all(self):
                        return []
                return MockQuery()

            def all(self):
                return []

        return MockNotifications()

    @property
    def zines(self):
        """Return a mock zines object for compatibility with templates"""
        user_id = self.id

        class MockZines:
            def filter_by(self, **kwargs):
                # Get zines from Firestore
                status = kwargs.get('status', None)

                class MockQuery:
                    def order_by(self, field):
                        return self

                    def all(self):
                        # Get zines from Firestore
                        zines = firestore_db.get_user_zines(user_id, status=status)
                        # Convert to object-like format
                        class ZineObj:
                            def __init__(self, data):
                                self.__dict__.update(data)
                        return [ZineObj(z) for z in zines]

                    def count(self):
                        return len(self.all())

                return MockQuery()

            def order_by(self, field):
                return self

            def all(self):
                zines = firestore_db.get_user_zines(user_id)
                class ZineObj:
                    def __init__(self, data):
                        self.__dict__.update(data)
                return [ZineObj(z) for z in zines]

        return MockZines()

    @property
    def followers(self):
        """Return a mock followers object for compatibility with templates"""
        class MockFollowers:
            def all(self):
                return []

        return MockFollowers()

    def update(self, **kwargs):
        """Update user data"""
        firestore_db.update_user(self.id, kwargs)
        # Update local attributes
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        """Convert to dictionary"""
        return self._user_data if hasattr(self, '_user_data') else {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'firebase_uid': self.firebase_uid,
            'bio': self.bio,
            'avatar_url': self.avatar_url,
            'followers_count': self.followers_count,
            'following_count': self.following_count,
            'email_notifications': self.email_notifications
        }