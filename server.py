# server.py - Python Webserver mit Basic Auth und korrekten MIME-Types

from flask import Flask, send_from_directory, request, Response
import os
import mimetypes

app = Flask(__name__)

# MIME-Types initialisieren
mimetypes.init()

# Passwort-Schutz
USERNAME = os.environ.get('AUTH_USERNAME', 'admin')
PASSWORD = os.environ.get('AUTH_PASSWORD', 'geheim123')

def check_auth(username, password):
    return username == USERNAME and password == PASSWORD

def authenticate():
    return Response(
        'Zugriff verweigert. Bitte melden Sie sich an.',
        401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

def requires_auth(f):
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    decorated.__name__ = f.__name__
    return decorated

@app.route('/')
@requires_auth
def index():
    return send_from_directory('.', 'index.html')

@app.route('/static/<path:filename>')
@requires_auth
def serve_static(filename):
    """
    Serviert Dateien aus dem static-Ordner mit korrekten MIME-Types
    """
    response = send_from_directory('static', filename)
    
    # Stelle sicher, dass PNG-Dateien den korrekten MIME-Type haben
    if filename.endswith('.png'):
        response.headers['Content-Type'] = 'image/png'
    elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
        response.headers['Content-Type'] = 'image/jpeg'
    elif filename.endswith('.svg'):
        response.headers['Content-Type'] = 'image/svg+xml'
    
    # Cache-Control für bessere Performance
    response.headers['Cache-Control'] = 'public, max-age=3600'
    
    return response

@app.after_request
def add_security_headers(response):
    """
    Fügt Sicherheitsheader hinzu
    """
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
