import sys
import os

# Add the parent directory to the path so we can import the app module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Debug: Print current working directory and Python path
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    print(f"Directory contents: {os.listdir('.')}")

    from app import create_app
    print("Successfully imported create_app")

    app = create_app()
    print("Successfully created app")

    # This is the standard way to expose Flask app to Vercel
    # Vercel expects the variable to be named 'app' or 'application'
    application = app

except Exception as e:
    # If there's an error, create a simple WSGI app that returns the error
    import traceback

    def application(environ, start_response):
        error_msg = f"Import Error: {str(e)}\n\nCurrent directory: {os.getcwd()}\nDirectory contents: {os.listdir('.')}\nPython path: {sys.path}\n\nTraceback:\n{traceback.format_exc()}"
        status = '500 Internal Server Error'
        headers = [('Content-Type', 'text/plain')]
        start_response(status, headers)
        return [error_msg.encode('utf-8')]