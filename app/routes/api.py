from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import Zine, Analytics, User
from app import db
from datetime import datetime, timedelta
from sqlalchemy import func
import os
from werkzeug.utils import secure_filename
from PIL import Image
import uuid

bp = Blueprint('api', __name__, url_prefix='/api')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
UPLOAD_FOLDER = 'static/uploads'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file and allowed_file(file.filename):
        # Check file size before processing (max 10MB)
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning

        if file_size > 10 * 1024 * 1024:  # 10MB limit
            return jsonify({'error': 'File too large. Maximum size is 10MB'}), 400

        # For Vercel/serverless, we'll use base64 encoding
        # or external image URLs instead of local file storage
        import base64
        from io import BytesIO

        try:
            # Read the file into memory
            img = Image.open(file)
        except Exception as e:
            return jsonify({'error': f'Invalid image file: {str(e)}'}), 400

        # Convert RGBA to RGB if necessary (for JPEG compatibility)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Create a white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background

        # More aggressive resizing for better performance
        # Max dimension of 800px for zine pages (mobile-optimized)
        if img.width > 800 or img.height > 800:
            img.thumbnail((800, 800), Image.Resampling.LANCZOS)

        # Convert to base64 with progressive compression
        buffered = BytesIO()

        # Always use JPEG for photos to reduce size (except for logos/graphics)
        # Check if image has lots of uniform colors (likely a graphic/logo)
        is_graphic = len(img.getcolors(maxcolors=256) or []) < 256 if img.mode == 'RGB' else False

        if is_graphic and file.filename.lower().endswith('.png'):
            # Keep PNG for graphics/logos
            img.save(buffered, format='PNG', optimize=True, compress_level=9)
        else:
            # Use JPEG with lower quality for photos
            img.save(buffered, format='JPEG', optimize=True, quality=75, progressive=True)

        # Check final size and reduce quality if still too large
        if buffered.tell() > 200000:  # If over 200KB, reduce quality further
            buffered = BytesIO()
            img.save(buffered, format='JPEG', optimize=True, quality=60, progressive=True)

        img_str = base64.b64encode(buffered.getvalue()).decode()

        # Determine mime type based on what we actually saved
        if is_graphic and file.filename.lower().endswith('.png'):
            mime_type = "image/png"
        else:
            mime_type = "image/jpeg"

        data_url = f"data:{mime_type};base64,{img_str}"

        return jsonify({
            'success': True,
            'url': data_url,
            'thumbnail': data_url  # For now, same as main image
        })

    return jsonify({'error': 'Invalid file type'}), 400

@bp.route('/analytics/<int:zine_id>')
@login_required
def get_analytics(zine_id):
    zine = Zine.query.get_or_404(zine_id)
    if zine.creator_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)

    daily_views = db.session.query(
        func.date(Analytics.created_at).label('date'),
        func.count(Analytics.id).label('views')
    ).filter(
        Analytics.zine_id == zine_id,
        Analytics.event_type == 'view',
        Analytics.created_at >= start_date
    ).group_by(func.date(Analytics.created_at)).all()

    top_referrers = db.session.query(
        Analytics.referrer,
        func.count(Analytics.id).label('count')
    ).filter(
        Analytics.zine_id == zine_id,
        Analytics.referrer.isnot(None)
    ).group_by(Analytics.referrer).order_by(func.count(Analytics.id).desc()).limit(5).all()

    followers_gained = db.session.query(func.count(Analytics.id)).filter(
        Analytics.zine_id == zine_id,
        Analytics.event_type == 'follow',
        Analytics.created_at >= start_date
    ).scalar() or 0

    return jsonify({
        'views': zine.views_count,
        'unique_readers': zine.unique_readers,
        'avg_read_time': round(zine.avg_read_time, 1) if zine.avg_read_time else 0,
        'followers_gained': followers_gained,
        'daily_views': [{'date': str(d.date), 'views': d.views} for d in daily_views],
        'top_referrers': [{'referrer': r.referrer or 'Direct', 'count': r.count} for r in top_referrers]
    })

@bp.route('/templates')
def get_templates():
    templates = [
        {
            'id': 'blank',
            'name': 'Blank',
            'preview': '/static/images/template-blank.png',
            'blocks': []
        },
        {
            'id': 'cover',
            'name': 'Cover Page',
            'preview': '/static/images/template-cover.png',
            'blocks': [
                {'type': 'text', 'content': 'Your Title', 'style': 'title', 'x': 50, 'y': 40},
                {'type': 'text', 'content': 'Subtitle', 'style': 'subtitle', 'x': 50, 'y': 55}
            ]
        },
        {
            'id': 'photo-text',
            'name': 'Photo + Text',
            'preview': '/static/images/template-photo-text.png',
            'blocks': [
                {'type': 'image', 'x': 10, 'y': 10, 'width': 80, 'height': 40},
                {'type': 'text', 'content': 'Your text here', 'x': 10, 'y': 55, 'width': 80}
            ]
        },
        {
            'id': 'grid',
            'name': 'Grid Layout',
            'preview': '/static/images/template-grid.png',
            'blocks': [
                {'type': 'image', 'x': 10, 'y': 10, 'width': 35, 'height': 35},
                {'type': 'image', 'x': 55, 'y': 10, 'width': 35, 'height': 35},
                {'type': 'image', 'x': 10, 'y': 55, 'width': 35, 'height': 35},
                {'type': 'image', 'x': 55, 'y': 55, 'width': 35, 'height': 35}
            ]
        },
        {
            'id': 'article',
            'name': 'Article',
            'preview': '/static/images/template-article.png',
            'blocks': [
                {'type': 'text', 'content': 'Article Title', 'style': 'heading', 'x': 10, 'y': 10},
                {'type': 'text', 'content': 'Your article text...', 'x': 10, 'y': 20, 'width': 80, 'height': 70}
            ]
        }
    ]
    return jsonify(templates)