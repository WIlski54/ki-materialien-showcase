# server.py - Python Webserver mit Basic Auth und korrekten MIME-Types (Safari-kompatibel)

from flask import Flask, send_from_directory, request, Response, make_response
import os
import mimetypes
from functools import wraps

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
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# ------------------------------------------------------------
# ✅ Wichtigster Fix: korrekter MIME-Type für index.html
# ------------------------------------------------------------
@app.route('/')
@requires_auth
def index():
    """
    Liefert die Startseite mit explizitem MIME-Type für Safari/iOS
    """
    file_path = os.path.join(os.getcwd(), 'index.html')
    if not os.path.exists(file_path):
        return "index.html nicht gefunden.", 404

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    response = make_response(content)
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Cache-Control'] = 'no-cache'
    return response


# ------------------------------------------------------------
# Statische Dateien
# ------------------------------------------------------------
@app.route('/static/<path:filename>')
@requires_auth
def serve_static(filename):
    """
    Serviert Dateien aus dem static-Ordner mit korrekten MIME-Types
    """
    response = send_from_directory('static', filename)

    # MIME-Typ-Header sicherstellen
    mime_type, _ = mimetypes.guess_type(filename)
    if mime_type:
        response.headers['Content-Type'] = mime_type
    else:
        response.headers['Content-Type'] = 'application/octet-stream'

    # Cache-Control für bessere Performance
    response.headers['Cache-Control'] = 'public, max-age=3600'

    return response


@app.after_request
def add_security_headers(response):
    """
    Fügt Sicherheitsheader hinzu
    """
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'no-referrer'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    return response


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
