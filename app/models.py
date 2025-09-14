from datetime import datetime
from flask_login import UserMixin
from app import db
import json

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firebase_uid = db.Column(db.String(128), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    display_name = db.Column(db.String(255))
    avatar_url = db.Column(db.String(255))
    bio = db.Column(db.Text)
    website = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    email_notifications = db.Column(db.Boolean, default=True)

    zines = db.relationship('Zine', backref='creator', lazy='dynamic', cascade='all, delete-orphan')
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    analytics = db.relationship('Analytics', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def get_feed(self):
        followed_zines = Zine.query.join(
            followers, (followers.c.followed_id == Zine.creator_id)
        ).filter(
            followers.c.follower_id == self.id,
            Zine.status == 'published'
        )
        own = Zine.query.filter_by(creator_id=self.id, status='published')
        return followed_zines.union(own).order_by(Zine.published_at.desc())

class Zine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    cover_image = db.Column(db.String(255))
    status = db.Column(db.String(20), default='draft')  # draft, published, unlisted
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    published_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    views_count = db.Column(db.Integer, default=0)
    unique_readers = db.Column(db.Integer, default=0)
    avg_read_time = db.Column(db.Float, default=0)
    enable_pdf = db.Column(db.Boolean, default=True)
    layout_type = db.Column(db.String(20), default='A5')  # A5, A4, square

    pages = db.relationship('Page', backref='zine', lazy='dynamic', cascade='all, delete-orphan', order_by='Page.order')
    tags = db.relationship('Tag', secondary='zine_tags', backref='zines', lazy='dynamic')
    analytics = db.relationship('Analytics', backref='zine', lazy='dynamic', cascade='all, delete-orphan')
    versions = db.relationship('ZineVersion', backref='zine', lazy='dynamic', cascade='all, delete-orphan', order_by='ZineVersion.created_at.desc()')

    def __repr__(self):
        return f'<Zine {self.title}>'

    def get_url(self):
        return f'/{self.creator.username}/{self.slug}'

class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    zine_id = db.Column(db.Integer, db.ForeignKey('zine.id'), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    content = db.Column(db.JSON)  # Stores page blocks as JSON
    template = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Page {self.order} of Zine {self.zine_id}>'

class ZineVersion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    zine_id = db.Column(db.Integer, db.ForeignKey('zine.id'), nullable=False)
    version_number = db.Column(db.Integer, nullable=False)
    content_snapshot = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    category = db.Column(db.String(50))

zine_tags = db.Table('zine_tags',
    db.Column('zine_id', db.Integer, db.ForeignKey('zine.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # new_issue, new_follower, etc.
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text)
    link = db.Column(db.String(255))
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Analytics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    zine_id = db.Column(db.Integer, db.ForeignKey('zine.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    event_type = db.Column(db.String(50))  # view, read, share, follow
    referrer = db.Column(db.String(255))
    session_id = db.Column(db.String(100))
    read_time = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)