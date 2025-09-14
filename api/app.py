import sys
import os

# Add the parent directory to the path so we can import the app module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app import create_app
    app = create_app()
    # Mark that we successfully imported
    app.config['IMPORT_SUCCESS'] = True
except Exception as e:
    # Fallback to a simple Flask app if import fails
    from flask import Flask
    import traceback

    app = Flask(__name__)
    app.config['DEBUG'] = True  # Enable debug mode to show errors

    error_details = f"Import Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"

    @app.route('/')
    def error():
        return f"<pre>{error_details}</pre>"

    @app.route('/test')
    def test():
        return "Fallback Flask app working - import failed!"

if __name__ == '__main__':
    app.run()