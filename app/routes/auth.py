from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from app.firebase_auth import verify_token, get_user as get_firebase_user
import re

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    firebase_config = current_app.config.get('FIREBASE_CONFIG', {})
    return render_template('auth/login.html', firebase_config=firebase_config)

@bp.route('/register')
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    firebase_config = current_app.config.get('FIREBASE_CONFIG', {})
    return render_template('auth/register.html', firebase_config=firebase_config)

@bp.route('/firebase-login', methods=['POST'])
def firebase_login():
    """Handle Firebase authentication and create/update local user"""
    data = request.get_json()
    id_token = data.get('idToken')

    if not id_token:
        return jsonify({'error': 'No token provided'}), 400

    # Verify Firebase token
    decoded_token = verify_token(id_token)
    if not decoded_token:
        return jsonify({'error': 'Invalid token'}), 401

    firebase_uid = decoded_token.get('uid')
    email = decoded_token.get('email')
    name = decoded_token.get('name', '')
    picture = decoded_token.get('picture', '')

    # Check if user exists
    user = User.query.filter_by(firebase_uid=firebase_uid).first()

    if not user:
        # Create new user
        # Generate unique username from email or name
        base_username = email.split('@')[0] if email else name.replace(' ', '').lower()
        base_username = re.sub(r'[^a-zA-Z0-9_]', '', base_username)[:20]

        username = base_username
        counter = 1
        while User.query.filter_by(username=username).first():
            username = f"{base_username}{counter}"
            counter += 1

        user = User(
            firebase_uid=firebase_uid,
            email=email,
            username=username,
            display_name=name,
            avatar_url=picture
        )
        db.session.add(user)
        db.session.commit()
    else:
        # Update existing user info
        user.email = email
        user.display_name = name
        if picture:
            user.avatar_url = picture
        db.session.commit()

    # Log in the user
    login_user(user, remember=True)

    return jsonify({
        'success': True,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'display_name': user.display_name,
            'avatar_url': user.avatar_url
        }
    })

@bp.route('/check-username', methods=['POST'])
def check_username():
    """Check if username is available"""
    data = request.get_json()
    username = data.get('username', '').strip()

    if not username:
        return jsonify({'available': False, 'error': 'Username is required'}), 400

    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return jsonify({'available': False, 'error': 'Username can only contain letters, numbers, and underscores'}), 400

    if len(username) < 3 or len(username) > 20:
        return jsonify({'available': False, 'error': 'Username must be between 3 and 20 characters'}), 400

    exists = User.query.filter_by(username=username).first() is not None

    return jsonify({'available': not exists})

@bp.route('/update-username', methods=['POST'])
@login_required
def update_username():
    """Update user's username"""
    data = request.get_json()
    username = data.get('username', '').strip()

    if not username:
        return jsonify({'error': 'Username is required'}), 400

    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return jsonify({'error': 'Username can only contain letters, numbers, and underscores'}), 400

    if len(username) < 3 or len(username) > 20:
        return jsonify({'error': 'Username must be between 3 and 20 characters'}), 400

    # Check if username is taken (excluding current user)
    existing = User.query.filter_by(username=username).first()
    if existing and existing.id != current_user.id:
        return jsonify({'error': 'Username is already taken'}), 400

    current_user.username = username
    db.session.commit()

    return jsonify({'success': True, 'username': username})

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html', user=current_user)

@bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.bio = request.form.get('bio')
        current_user.website = request.form.get('website')
        current_user.email_notifications = request.form.get('email_notifications') == 'on'

        # Handle username update
        new_username = request.form.get('username')
        if new_username and new_username != current_user.username:
            if User.query.filter_by(username=new_username).first():
                flash('Username is already taken', 'error')
                return redirect(url_for('auth.edit_profile'))
            current_user.username = new_username

        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/edit_profile.html', user=current_user)