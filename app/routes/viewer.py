from flask import Blueprint, render_template, request, jsonify, abort, make_response, url_for
from flask_login import current_user
from datetime import datetime
import qrcode
import io
import base64
import uuid

# Always import both systems to avoid import errors
from app.models import User, Zine, Page, Analytics
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

bp = Blueprint('viewer', __name__)

@bp.route('/demo/sample-zine')
def demo_zine():
    """Demo zine for testing when database is empty"""
    # Create a demo zine object
    class DemoZine:
        title = "Sample Zine"
        description = "This is a demo zine to showcase the viewer"
        slug = "sample-zine"
        views_count = 42
        likes_count = 10
        unique_readers = 25
        format = "A5"
        id = 1

    class DemoCreator:
        username = "demo"
        bio = "Demo creator account"
        id = 1

    class DemoPage:
        def __init__(self, order, content):
            self.order = order
            self.content = content

    zine = DemoZine()
    creator = DemoCreator()
    pages = [
        DemoPage(1, {
            "elements": [
                {
                    "type": "image",
                    "src": "https://images.unsplash.com/photo-1755868679492-a708c7626971?q=80&w=985&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
                    "x": 0,
                    "y": 0,
                    "width": "100%",
                    "height": "100%"
                },
                {
                    "type": "text",
                    "content": "<h1 style='color: white; text-shadow: 2px 2px 8px rgba(0,0,0,0.9); font-size: 2.5em; margin-bottom: 10px;'>Welcome to Zines!</h1><p style='color: white; text-shadow: 2px 2px 6px rgba(0,0,0,0.9); font-size: 1.2em;'>Express yourself through beautiful digital publications</p>",
                    "x": 20,
                    "y": 80,
                    "width": "90%",
                    "height": 200
                }
            ]
        }),
        DemoPage(2, {
            "elements": [
                {
                    "type": "text",
                    "content": "<h2>Full-Screen Experience</h2><p>Every zine is optimized for mobile viewing with immersive full-screen layouts.</p>",
                    "x": 20,
                    "y": 100,
                    "width": 360,
                    "height": 200
                },
                {
                    "type": "text",
                    "content": "<p style='background: #007bff; color: white; padding: 20px; border-radius: 10px; text-align: center;'><strong>Sign up to create your own!</strong></p>",
                    "x": 20,
                    "y": 350,
                    "width": 360,
                    "height": 100
                }
            ]
        })
    ]

    is_following = False
    return render_template('viewer/view.html', zine=zine, creator=creator, pages=pages, is_following=is_following)

@bp.route('/<username>')
def creator_profile(username):
    if use_firestore():
        creator = firestore_db.get_user_by_username(username)
        if not creator:
            abort(404)

        zines = firestore_db.get_user_zines(creator['id'], status='published')

        is_following = False
        if current_user.is_authenticated:
            is_following = firestore_db.is_following(current_user.id, creator['id'])

        # Convert to object-like format for template compatibility
        class CreatorObj:
            def __init__(self, data):
                self.__dict__.update(data)

        creator_obj = CreatorObj(creator)
        zines_objs = [CreatorObj(z) for z in zines]

        return render_template('viewer/creator.html', creator=creator_obj, zines=zines_objs, is_following=is_following)
    else:
        # SQLAlchemy fallback
        creator = User.query.filter_by(username=username).first_or_404()
        zines = creator.zines.filter_by(status='published').order_by(Zine.published_at.desc()).all()

        is_following = False
        if current_user.is_authenticated:
            is_following = current_user.is_following(creator)

        return render_template('viewer/creator.html', creator=creator, zines=zines, is_following=is_following)

@bp.route('/<username>/<slug>')
def view_zine(username, slug):
    print(f"\n{'='*60}")
    print(f"VIEW_ZINE ROUTE HIT")
    print(f"Username: {username}")
    print(f"Slug: {slug}")
    print(f"Using Firestore: {use_firestore()}")
    print(f"{'='*60}")

    if use_firestore():
        creator = firestore_db.get_user_by_username(username)
        print(f"Creator found: {creator}")
        if not creator:
            print(f"ERROR: No creator found with username: {username}")
            abort(404)

        zine = firestore_db.get_zine_by_slug(creator['id'], slug)
        print(f"Zine found: {zine}")
        if not zine:
            print(f"ERROR: No zine found with slug: {slug} for creator ID: {creator['id']}")
            abort(404)

        if zine['status'] == 'draft':
            if not current_user.is_authenticated or current_user.id != creator['id']:
                abort(404)

        pages = firestore_db.get_zine_pages(zine['id'])

        # Track view
        session_id = request.cookies.get('session_id', None)
        if not session_id:
            session_id = str(uuid.uuid4())

        firestore_db.track_view(
            zine_id=zine['id'],
            user_id=current_user.id if current_user.is_authenticated else None,
            session_id=session_id,
            referrer=request.referrer
        )
    else:
        # SQLAlchemy fallback
        creator = User.query.filter_by(username=username).first_or_404()
        zine = Zine.query.filter_by(creator_id=creator.id, slug=slug).first_or_404()

        if zine.status == 'draft':
            if not current_user.is_authenticated or current_user.id != creator.id:
                abort(404)

        pages = zine.pages.order_by(Page.order).all()

        # Track view
        session_id = request.cookies.get('session_id', None)
        if not session_id:
            session_id = str(uuid.uuid4())

        zine.views_count += 1
        db.session.commit()

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(request.url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer)
    qr_code = base64.b64encode(buffer.getvalue()).decode()

    is_following = False

    if use_firestore():
        if current_user.is_authenticated:
            is_following = firestore_db.is_following(current_user.id, creator['id'])

        # Convert to object-like format for template compatibility
        class DataObj:
            def __init__(self, data):
                self.__dict__.update(data)

        zine_obj = DataObj(zine)
        creator_obj = DataObj(creator)
        pages_objs = [DataObj(p) for p in pages]
    else:
        if current_user.is_authenticated:
            is_following = current_user.is_following(creator)

        zine_obj = zine
        creator_obj = creator
        pages_objs = pages

    response = make_response(render_template(
        'viewer/view.html',
        zine=zine_obj,
        pages=pages_objs,
        creator=creator_obj,
        qr_code=qr_code,
        is_following=is_following
    ))
    response.set_cookie('session_id', session_id, max_age=60*60*24*30)  # 30 days
    return response

@bp.route('/<username>/<slug>/pdf')
def download_pdf(username, slug):
    creator = User.query.filter_by(username=username).first_or_404()
    zine = Zine.query.filter_by(creator_id=creator.id, slug=slug).first_or_404()

    if not zine.enable_pdf:
        abort(404)

    if zine.status == 'draft':
        if not current_user.is_authenticated or current_user.id != creator.id:
            abort(404)

    return jsonify({'error': 'PDF generation not yet implemented'}), 501

@bp.route('/api/track-read-time', methods=['POST'])
def track_read_time():
    data = request.get_json()
    zine_id = data.get('zine_id')
    read_time = data.get('read_time')
    session_id = request.cookies.get('session_id')

    if zine_id and read_time and session_id:
        if use_firestore():
            firestore_db.track_read_time(zine_id, session_id, read_time)
        # SQLAlchemy doesn't need special handling here

    return jsonify({'success': True})