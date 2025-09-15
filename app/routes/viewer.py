from flask import Blueprint, render_template, request, jsonify, abort, make_response, url_for
from flask_login import current_user
from app.models import Zine, User, Analytics, Page
from app import db
from datetime import datetime
import qrcode
import io
import base64

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
                    "type": "text",
                    "content": "<h1>Welcome to Zines!</h1><p>This is a demo zine to show how the viewer works.</p>",
                    "x": 50,
                    "y": 100,
                    "width": 300,
                    "height": 200
                }
            ]
        }),
        DemoPage(2, {
            "elements": [
                {
                    "type": "text",
                    "content": "<h2>Create Your Own</h2><p>Sign up to create and share your own digital zines!</p>",
                    "x": 50,
                    "y": 50,
                    "width": 300,
                    "height": 150
                }
            ]
        })
    ]

    is_following = False
    return render_template('viewer/view.html', zine=zine, creator=creator, pages=pages, is_following=is_following)

@bp.route('/<username>')
def creator_profile(username):
    creator = User.query.filter_by(username=username).first_or_404()
    zines = creator.zines.filter_by(status='published').order_by(Zine.published_at.desc()).all()

    is_following = False
    if current_user.is_authenticated:
        is_following = current_user.is_following(creator)

    return render_template('viewer/creator.html', creator=creator, zines=zines, is_following=is_following)

@bp.route('/<username>/<slug>')
def view_zine(username, slug):
    creator = User.query.filter_by(username=username).first_or_404()
    zine = Zine.query.filter_by(creator_id=creator.id, slug=slug).first_or_404()

    if zine.status == 'draft':
        if not current_user.is_authenticated or current_user.id != creator.id:
            abort(404)

    pages = zine.pages.order_by(Page.order).all()

    zine.views_count += 1

    session_id = request.cookies.get('session_id', None)
    if not session_id:
        import uuid
        session_id = str(uuid.uuid4())

    existing_view = Analytics.query.filter_by(
        zine_id=zine.id,
        session_id=session_id,
        event_type='view'
    ).first()

    if not existing_view:
        zine.unique_readers += 1
        analytics = Analytics(
            zine_id=zine.id,
            user_id=current_user.id if current_user.is_authenticated else None,
            event_type='view',
            referrer=request.referrer,
            session_id=session_id
        )
        db.session.add(analytics)

    db.session.commit()

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(request.url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer)
    qr_code = base64.b64encode(buffer.getvalue()).decode()

    is_following = False
    if current_user.is_authenticated:
        is_following = current_user.is_following(creator)

    response = make_response(render_template(
        'viewer/view.html',
        zine=zine,
        pages=pages,
        creator=creator,
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
        analytics = Analytics.query.filter_by(
            zine_id=zine_id,
            session_id=session_id,
            event_type='view'
        ).first()

        if analytics:
            analytics.read_time = read_time

            zine = Zine.query.get(zine_id)
            if zine:
                total_read_time = db.session.query(db.func.sum(Analytics.read_time)).filter_by(zine_id=zine_id).scalar() or 0
                read_count = Analytics.query.filter_by(zine_id=zine_id).filter(Analytics.read_time.isnot(None)).count()
                if read_count > 0:
                    zine.avg_read_time = total_read_time / read_count

            db.session.commit()

    return jsonify({'success': True})