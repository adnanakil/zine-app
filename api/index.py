from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello from Flask on Vercel!'

@app.route('/test')
def test():
    return 'Test route working!'

# For Vercel, the app object is used directly