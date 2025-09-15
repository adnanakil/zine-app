from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_cors import CORS
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
migrate = Migrate()

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')

    # Use in-memory database for Vercel (serverless) environment
    # Vercel has read-only file system, so we can't create SQLite files
    if os.getenv('VERCEL') or '/var/task' in os.getcwd():
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///instance/zines.db')

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

    # Firebase config for frontend (strip whitespace from all values)
    app.config['FIREBASE_CONFIG'] = {
        'apiKey': (os.getenv('FIREBASE_API_KEY') or '').strip(),
        'authDomain': (os.getenv('FIREBASE_AUTH_DOMAIN') or '').strip(),
        'projectId': (os.getenv('FIREBASE_PROJECT_ID') or '').strip(),
        'storageBucket': (os.getenv('FIREBASE_STORAGE_BUCKET') or '').strip(),
        'messagingSenderId': (os.getenv('FIREBASE_MESSAGING_SENDER_ID') or '').strip(),
        'appId': (os.getenv('FIREBASE_APP_ID') or '').strip(),
        'measurementId': (os.getenv('FIREBASE_MEASUREMENT_ID') or '').strip()
    }

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    login_manager.login_view = 'auth.login'

    from app.firebase_auth import init_firebase
    init_firebase()

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.routes import main, auth, editor, viewer, api
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(editor.bp)
    app.register_blueprint(viewer.bp)
    app.register_blueprint(api.bp)

    with app.app_context():
        db.create_all()

        # Create demo data if database is empty (for Vercel)
        from app.models import User, Zine, Page
        if not User.query.first():
            # Create demo user
            demo_user = User(
                username='dev',
                email='dev@archgest.com',
                firebase_uid='demo_user_firebase_uid'
            )
            demo_user.set_password('demo123')
            db.session.add(demo_user)
            db.session.commit()

            # Create demo zine
            demo_zine = Zine(
                creator_id=demo_user.id,
                title='BestBest',
                slug='bestbest',
                description='A sample zine',
                status='published',
                published_at=datetime.utcnow()
            )
            db.session.add(demo_zine)
            db.session.commit()

            # Create demo page
            demo_page = Page(
                zine_id=demo_zine.id,
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
            db.session.add(demo_page)
            db.session.commit()

    return app