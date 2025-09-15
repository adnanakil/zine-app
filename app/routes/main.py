from flask import Blueprint, render_template, request, redirect, url_for, current_app
from flask_login import current_user, login_required
from app.models import Zine, User, Tag, Analytics, Notification
from app import db
from sqlalchemy import or_

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    if current_user.is_authenticated:
        feed_zines = current_user.get_feed().limit(20).all()
        return render_template('index.html', zines=feed_zines, feed=True)
    else:
        featured_zines = Zine.query.filter_by(status='published').order_by(Zine.views_count.desc()).limit(12).all()
        return render_template('index.html', zines=featured_zines, feed=False)

@bp.route('/explore')
def explore():
    category = request.args.get('category')
    search = request.args.get('search')

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
    notifications = current_user.notifications.order_by(Notification.created_at.desc()).limit(50).all()
    Notification.query.filter_by(user_id=current_user.id, read=False).update({'read': True})
    db.session.commit()
    return render_template('notifications.html', notifications=notifications)

@bp.route('/follow/<int:user_id>')
@login_required
def follow(user_id):
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
    user = User.query.get_or_404(user_id)
    current_user.unfollow(user)
    db.session.commit()
    return redirect(request.referrer or url_for('main.index'))

@bp.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return redirect(url_for('main.explore'))

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