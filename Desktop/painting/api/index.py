from flask import Flask, request, jsonify, session
from flask_cors import CORS
import os
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'makart_secret_key_2024')

# Configure CORS for Vercel
CORS(app, 
     origins=["https://makart.vercel.app", "http://localhost:3000"], 
     methods=["GET", "POST", "OPTIONS"], 
     headers=["Content-Type"], 
     supports_credentials=True)

VALID_EMAIL = "olimpia@makincome.com"
VALID_PASSWORD = "Chanel2808"

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'version': '3.0', 'platform': 'vercel'}), 200

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email')
        password = data.get('password')

        if email == VALID_EMAIL and password == VALID_PASSWORD:
            session['logged_in'] = True
            session['user_email'] = email
            return jsonify({'message': 'Login successful', 'email': email}), 200
        
        return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    session.clear()
    return jsonify({'message': 'Logout successful'}), 200

@app.route('/api/session', methods=['GET'])
def check_session():
    try:
        if 'logged_in' in session:
            return jsonify({'logged_in': True, 'email': session.get('user_email')}), 200
        return jsonify({'logged_in': False}), 200
    except Exception as e:
        return jsonify({'logged_in': False}), 200

@app.route('/api/upload', methods=['POST'])
@login_required
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # For immediate functionality, return success message
        # Animation processing can be added later
        return jsonify({
            'message': 'File uploaded successfully! Animation processing will be available soon.',
            'filename': file.filename,
            'status': 'received'
        }), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Vercel serverless function compatibility
def handler(request):
    return app(request)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 