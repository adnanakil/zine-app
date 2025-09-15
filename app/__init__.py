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
    firebase_app = init_firebase()

    # Initialize Firestore database with demo data only if Firebase is configured
    try:
        if firebase_app:  # Only use Firestore if Firebase Admin SDK is initialized
            print("Firebase app initialized, attempting Firestore connection...")
            from app.firestore_db import firestore_db
            if firestore_db.is_available():
                firestore_db.init_demo_data()
                print("Firestore initialized successfully")
            else:
                print("Firestore API not enabled - using SQLAlchemy only")
        else:
            print("Firebase not configured - using SQLAlchemy only")
    except Exception as e:
        print(f"Error initializing Firestore: {e}")
        print("Falling back to SQLAlchemy database")
        import traceback
        traceback.print_exc()

    from app.models import User

    # Check if Firestore is available
    use_firestore = False
    try:
        from app.firestore_db import firestore_db
        if firestore_db.is_available():
            from app.firestore_models import FirestoreUser
            use_firestore = True
            print("Using Firestore for user storage")
        else:
            print("Using SQLAlchemy for user storage")
    except Exception as e:
        print(f"Firestore not available for users: {e}")

    @login_manager.user_loader
    def load_user(user_id):
        if use_firestore:
            # Try Firestore
            try:
                firestore_user = FirestoreUser.get(user_id)
                if firestore_user:
                    return firestore_user
            except Exception as e:
                print(f"Error loading user from Firestore: {e}")

        # Fallback to SQLAlchemy
        try:
            return User.query.get(int(user_id))
        except:
            return None

    from app.routes import main, auth, editor, viewer, api
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(editor.bp)
    app.register_blueprint(viewer.bp)
    app.register_blueprint(api.bp)

    with app.app_context():
        db.create_all()
        # SQLAlchemy tables are created but we're using Firestore for actual data
        # Demo data is initialized in Firestore via firestore_db.init_demo_data()

    return app