from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Zine, Page, ZineVersion, Tag, Notification
from app import db
from datetime import datetime
import json
import re

bp = Blueprint('editor', __name__, url_prefix='/editor')

def generate_slug(title):
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug

@bp.route('/new')
@login_required
def new_zine():
    return render_template('editor/new.html')

@bp.route('/create', methods=['POST'])
@login_required
def create_zine():
    title = request.form.get('title')
    description = request.form.get('description')
    layout_type = request.form.get('layout_type', 'A5')

    slug = generate_slug(title)
    counter = 1
    original_slug = slug
    while Zine.query.filter_by(creator_id=current_user.id, slug=slug).first():
        slug = f"{original_slug}-{counter}"
        counter += 1

    zine = Zine(
        creator_id=current_user.id,
        title=title,
        slug=slug,
        description=description,
        layout_type=layout_type,
        status='draft'
    )
    db.session.add(zine)
    db.session.commit()

    first_page = Page(
        zine_id=zine.id,
        order=0,
        content={'blocks': []},
        template='blank'
    )
    db.session.add(first_page)
    db.session.commit()

    return redirect(url_for('editor.edit', zine_id=zine.id))

@bp.route('/<int:zine_id>')
@login_required
def edit(zine_id):
    zine = Zine.query.get_or_404(zine_id)
    if zine.creator_id != current_user.id:
        flash('You can only edit your own zines', 'error')
        return redirect(url_for('main.index'))

    pages = zine.pages.all()
    return render_template('editor/edit.html', zine=zine, pages=pages)

@bp.route('/<int:zine_id>/save', methods=['POST'])
@login_required
def save(zine_id):
    zine = Zine.query.get_or_404(zine_id)
    if zine.creator_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    page_id = data.get('page_id')
    content = data.get('content')

    if page_id:
        page = Page.query.get_or_404(page_id)
        if page.zine_id != zine_id:
            return jsonify({'error': 'Invalid page'}), 400
    else:
        last_page = Page.query.filter_by(zine_id=zine_id).order_by(Page.order.desc()).first()
        next_order = (last_page.order + 1) if last_page else 0
        page = Page(zine_id=zine_id, order=next_order)
        db.session.add(page)

    page.content = content
    page.updated_at = datetime.utcnow()
    zine.updated_at = datetime.utcnow()

    version_count = ZineVersion.query.filter_by(zine_id=zine_id).count()
    if version_count >= 10:
        oldest = ZineVersion.query.filter_by(zine_id=zine_id).order_by(ZineVersion.created_at).first()
        db.session.delete(oldest)

    all_pages = Page.query.filter_by(zine_id=zine_id).order_by(Page.order).all()
    snapshot = {
        'pages': [{'order': p.order, 'content': p.content} for p in all_pages]
    }

    version = ZineVersion(
        zine_id=zine_id,
        version_number=version_count + 1,
        content_snapshot=snapshot,
        created_by=current_user.id
    )
    db.session.add(version)
    db.session.commit()

    return jsonify({'success': True, 'page_id': page.id})

@bp.route('/<int:zine_id>/add-page', methods=['POST'])
@login_required
def add_page(zine_id):
    zine = Zine.query.get_or_404(zine_id)
    if zine.creator_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    last_page = Page.query.filter_by(zine_id=zine_id).order_by(Page.order.desc()).first()
    next_order = (last_page.order + 1) if last_page else 0

    page = Page(
        zine_id=zine_id,
        order=next_order,
        content={'blocks': []},
        template='blank'
    )
    db.session.add(page)
    db.session.commit()

    return jsonify({'success': True, 'page_id': page.id, 'order': page.order})

@bp.route('/<int:zine_id>/delete-page/<int:page_id>', methods=['DELETE'])
@login_required
def delete_page(zine_id, page_id):
    zine = Zine.query.get_or_404(zine_id)
    if zine.creator_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    page = Page.query.get_or_404(page_id)
    if page.zine_id != zine_id:
        return jsonify({'error': 'Invalid page'}), 400

    deleted_order = page.order
    db.session.delete(page)

    Page.query.filter(
        Page.zine_id == zine_id,
        Page.order > deleted_order
    ).update({Page.order: Page.order - 1})

    db.session.commit()
    return jsonify({'success': True})

@bp.route('/<int:zine_id>/publish', methods=['POST'])
@login_required
def publish(zine_id):
    zine = Zine.query.get_or_404(zine_id)
    if zine.creator_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    visibility = data.get('visibility', 'public')

    zine.status = 'published' if visibility == 'public' else 'unlisted'
    zine.published_at = datetime.utcnow()

    tags_data = data.get('tags', [])[:3]
    zine.tags = []
    for tag_name in tags_data:
        tag = Tag.query.filter_by(name=tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.session.add(tag)
        zine.tags.append(tag)

    db.session.commit()

    if visibility == 'public':
        for follower in current_user.followers.all():
            if follower.email_notifications:
                notification = Notification(
                    user_id=follower.id,
                    type='new_issue',
                    title='New zine published',
                    message=f'{current_user.username} published "{zine.title}"',
                    link=url_for('viewer.view_zine', username=current_user.username, slug=zine.slug)
                )
                db.session.add(notification)
        db.session.commit()

    return jsonify({
        'success': True,
        'url': url_for('viewer.view_zine', username=current_user.username, slug=zine.slug, _external=True)
    })

@bp.route('/my-zines')
@login_required
def my_zines():
    zines = current_user.zines.order_by(Zine.updated_at.desc()).all()
    return render_template('editor/my_zines.html', zines=zines)