import sys
import os

# Add the parent directory to the path so we can import the app module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app import create_app
    app = create_app()
except Exception as e:
    # Fallback to a simple Flask app if import fails
    from flask import Flask
    app = Flask(__name__)

    @app.route('/')
    def error():
        return f"Import Error: {str(e)}"

    @app.route('/test')
    def test():
        return "Fallback Flask app working!"

if __name__ == '__main__':
    app.run()