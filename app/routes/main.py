from flask import Blueprint, render_template, request, redirect, url_for, current_app, jsonify
from flask_login import current_user, login_required
from sqlalchemy import or_
from datetime import datetime

# Always import both systems to avoid import errors
from app.models import Zine, User, Tag, Analytics, Notification
from app import db

# Try to import Firestore
try:
    from app.firestore_db import firestore_db
    # Don't check availability at import time - do it dynamically
    USE_FIRESTORE = None  # Will be determined per request
except Exception as e:
    print(f"Firestore import failed: {e}")
    firestore_db = None
    USE_FIRESTORE = False

def use_firestore():
    """Dynamically check if Firestore should be used"""
    global USE_FIRESTORE
    if USE_FIRESTORE is not None:
        return USE_FIRESTORE

    if firestore_db is None:
        USE_FIRESTORE = False
        return False

    try:
        USE_FIRESTORE = firestore_db.is_available()
        return USE_FIRESTORE
    except Exception as e:
        print(f"Error checking Firestore availability: {e}")
        USE_FIRESTORE = False
        return False

bp = Blueprint('main', __name__)

@bp.route('/health')
def health():
    """Simple health check endpoint"""
    return jsonify({
        'status': 'ok',
        'firestore': use_firestore(),
        'timestamp': datetime.now().isoformat()
    })

@bp.route('/')
def index():
    try:
        if current_user.is_authenticated:
            if use_firestore():
                # Get following list and their recent zines
                following = firestore_db.get_following(current_user.id)
                feed_zines = []
                for followed_user in following:
                    user_zines = firestore_db.get_user_zines(followed_user['id'], status='published')
                    feed_zines.extend(user_zines[:5])  # Limit per user

                # Sort by published_at and limit total
                feed_zines.sort(key=lambda x: x.get('published_at', x.get('created_at')), reverse=True)
                feed_zines = feed_zines[:20]

                # Convert to object-like format for template compatibility
                class ZineObj:
                    def __init__(self, data):
                        self.__dict__.update(data)
                        # Add creator property
                        creator_data = firestore_db.get_user_by_id(data.get('creator_id'))
                        if creator_data:
                            self.creator = type('Creator', (), creator_data)()
                        else:
                            self.creator = None
                        # Add pages property (empty list for feed view)
                        self.pages = []

                feed_zines_objs = [ZineObj(z) for z in feed_zines if z]
                return render_template('index.html', zines=feed_zines_objs, feed=True)
            else:
                # SQLAlchemy fallback
                feed_zines = current_user.get_feed().limit(20).all()
                return render_template('index.html', zines=feed_zines, feed=True)
        else:
            if use_firestore():
                # Get featured zines sorted by views count
                featured_zines = firestore_db.get_published_zines(limit=50)
                # Sort by views_count
                featured_zines.sort(key=lambda x: x.get('views_count', 0), reverse=True)
                featured_zines = featured_zines[:12]

                # Convert to object-like format for template compatibility
                class ZineObj:
                    def __init__(self, data):
                        self.__dict__.update(data)
                        # Add creator property
                        creator_data = firestore_db.get_user_by_id(data.get('creator_id'))
                        if creator_data:
                            self.creator = type('Creator', (), creator_data)()
                        else:
                            self.creator = None
                        # Add pages property (empty list for feed view)
                        self.pages = []

                featured_zines_objs = [ZineObj(z) for z in featured_zines if z]
                return render_template('index.html', zines=featured_zines_objs, feed=False)
            else:
                # SQLAlchemy fallback
                featured_zines = Zine.query.filter_by(status='published').order_by(Zine.views_count.desc()).limit(12).all()
                return render_template('index.html', zines=featured_zines, feed=False)
    except Exception as e:
        print(f"Error in index route: {e}")
        import traceback
        traceback.print_exc()
        # Return a simple error page
        return jsonify({
            'error': str(e),
            'firestore_available': use_firestore() if firestore_db else False
        }), 500

@bp.route('/explore')
def explore():
    category = request.args.get('category')
    search = request.args.get('search')

    if use_firestore():
        # Get all published zines
        zines = firestore_db.get_published_zines(limit=50)

        # Filter by search if provided
        if search:
            search_lower = search.lower()
            zines = [z for z in zines if
                    search_lower in z.get('title', '').lower() or
                    search_lower in z.get('description', '').lower()]

        # Note: Category filtering not yet implemented for Firestore
        # This would require implementing tags in the Firestore schema

        # Convert to object-like format for template compatibility
        class ZineObj:
            def __init__(self, data):
                self.__dict__.update(data)

        zines_objs = [ZineObj(z) for z in zines]
        categories = []  # Categories not yet implemented for Firestore

        return render_template('explore.html', zines=zines_objs, categories=categories, current_category=category)
    else:
        # SQLAlchemy fallback
        query = Zine.query.filter_by(status='published')

        if search:
            query = query.filter(or_(
                Zine.title.contains(search),
                Zine.description.contains(search)
            ))

        if category:
            tag = Tag.query.filter_by(name=category).first()
            if tag:
                query = query.filter(Zine.tags.contains(tag))

        zines = query.order_by(Zine.published_at.desc()).limit(50).all()
        categories = Tag.query.distinct(Tag.category).all()

        return render_template('explore.html', zines=zines, categories=categories, current_category=category)

@bp.route('/notifications')
@login_required
def notifications():
    if use_firestore():
        # Note: Notifications not yet implemented for Firestore
        notifications = []
        return render_template('notifications.html', notifications=notifications)
    else:
        # SQLAlchemy fallback
        notifications = current_user.notifications.order_by(Notification.created_at.desc()).limit(50).all()
        Notification.query.filter_by(user_id=current_user.id, read=False).update({'read': True})
        db.session.commit()
        return render_template('notifications.html', notifications=notifications)

@bp.route('/follow/<int:user_id>')
@login_required
def follow(user_id):
    if use_firestore():
        user = firestore_db.get_user_by_id(str(user_id))
        if not user or user['id'] == current_user.id:
            return redirect(request.referrer or url_for('main.index'))

        firestore_db.follow_user(current_user.id, str(user_id))
        # Note: Notifications not yet implemented for Firestore
        return redirect(request.referrer or url_for('main.index'))
    else:
        # SQLAlchemy fallback
        user = User.query.get_or_404(user_id)
        if user == current_user:
            return redirect(request.referrer or url_for('main.index'))

        current_user.follow(user)
        db.session.commit()

        notification = Notification(
            user_id=user.id,
            type='new_follower',
            title='New Follower',
            message=f'{current_user.username} started following you',
            link=url_for('viewer.creator_profile', username=current_user.username)
        )
        db.session.add(notification)
        db.session.commit()

        return redirect(request.referrer or url_for('main.index'))

@bp.route('/unfollow/<int:user_id>')
@login_required
def unfollow(user_id):
    if use_firestore():
        user = firestore_db.get_user_by_id(str(user_id))
        if user:
            firestore_db.unfollow_user(current_user.id, str(user_id))
        return redirect(request.referrer or url_for('main.index'))
    else:
        # SQLAlchemy fallback
        user = User.query.get_or_404(user_id)
        current_user.unfollow(user)
        db.session.commit()
        return redirect(request.referrer or url_for('main.index'))

@bp.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return redirect(url_for('main.explore'))

    if use_firestore():
        # Get all published zines and filter by search
        all_zines = firestore_db.get_published_zines(limit=100)
        query_lower = query.lower()
        zines = [z for z in all_zines if
                query_lower in z.get('title', '').lower() or
                query_lower in z.get('description', '').lower()][:30]

        # Simple creator search - would need a proper search index for production
        # This is a basic implementation for now
        creators = []  # Creator search not yet implemented for Firestore

        # Convert to object-like format for template compatibility
        class DataObj:
            def __init__(self, data):
                self.__dict__.update(data)

        zines_objs = [DataObj(z) for z in zines]
        creators_objs = [DataObj(c) for c in creators]

        return render_template('search.html', query=query, zines=zines_objs, creators=creators_objs)
    else:
        # SQLAlchemy fallback
        zines = Zine.query.filter(
            Zine.status == 'published',
            or_(
                Zine.title.contains(query),
                Zine.description.contains(query)
            )
        ).limit(30).all()

        creators = User.query.filter(
            or_(
                User.username.contains(query),
                User.bio.contains(query)
            )
        ).limit(20).all()

        return render_template('search.html', query=query, zines=zines, creators=creators)

@bp.route('/test-firebase')
def test_firebase():
    return render_template('test_firebase.html', firebase_config=current_app.config['FIREBASE_CONFIG'])

@bp.route('/health')
def health_check():
    """Health check endpoint that reports Firestore status"""
    import os

    health_status = {
        'status': 'healthy',
        'database': 'firestore' if USE_FIRESTORE else 'sqlalchemy',
        'firestore_available': USE_FIRESTORE,
        'timestamp': datetime.now().isoformat(),
        'env_check': {
            'FIREBASE_PROJECT_ID': bool(os.getenv('FIREBASE_PROJECT_ID')),
            'FIREBASE_PRIVATE_KEY_BASE64': bool(os.getenv('FIREBASE_PRIVATE_KEY_BASE64')),
            'FIREBASE_CLIENT_EMAIL': bool(os.getenv('FIREBASE_CLIENT_EMAIL')),
            'FIREBASE_PRIVATE_KEY_ID': bool(os.getenv('FIREBASE_PRIVATE_KEY_ID'))
        }
    }

    if use_firestore():
        try:
            # Test Firestore connection
            firestore_db.is_available()
            health_status['firestore_connection'] = 'connected'
        except Exception as e:
            health_status['firestore_connection'] = 'failed'
            health_status['firestore_error'] = str(e)
            health_status['status'] = 'degraded'
    else:
        # Check why Firestore is not available
        health_status['firestore_check'] = firestore_db.is_available()

    return jsonify(health_status)