# Simple test to see if basic WSGI works
def application(environ, start_response):
    import sys
    import os

    try:
        # Add the parent directory to the path so we can import the app module
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        from app import create_app
        app = create_app()

        # If we get here, the import worked, so run the actual app
        return app(environ, start_response)

    except Exception as e:
        import traceback

        # Return detailed error information
        error_msg = f"""Import Error: {str(e)}

Current directory: {os.getcwd()}
Directory contents: {os.listdir('.')}
Python path: {sys.path}

Traceback:
{traceback.format_exc()}"""

        status = '500 Internal Server Error'
        headers = [('Content-Type', 'text/plain')]
        start_response(status, headers)
        return [error_msg.encode('utf-8')]