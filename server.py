# server.py - Python Webserver mit Basic Auth

from flask import Flask, send_from_directory, request, Response
import os

app = Flask(__name__)

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

# --- KORRIGIERTE ROUTE FÜR STATIC-DATEIEN ---
# Diese Route fängt Anfragen an /static/ ab (z.B. /static/chemie.png)
# und wendet den Passwortschutz darauf an.
@app.route('/static/<path:filename>')
@requires_auth
def serve_static(filename):
    # Sie sucht im Ordner 'static' nach der angeforderten Datei
    return send_from_directory('static', filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
