from flask import Flask, request, jsonify, send_file, session
from flask_cors import CORS
import os
import subprocess
import tempfile
import uuid
import shutil
from werkzeug.utils import secure_filename
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a_secure_secret_key')

# Configure CORS to be more robust
CORS(app, 
     origins=["https://makart.vercel.app"], 
     methods=["GET", "POST", "OPTIONS"], 
     headers=["Content-Type"], 
     supports_credentials=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
VALID_EMAIL = "olimpia@makincome.com"
VALID_PASSWORD = "Chanel2808"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if email == VALID_EMAIL and password == VALID_PASSWORD:
        session['logged_in'] = True
        session['user_email'] = email
        return jsonify({'message': 'Login successful', 'email': email}), 200
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    session.clear()
    return jsonify({'message': 'Logout successful'}), 200

@app.route('/api/session', methods=['GET'])
def check_session():
    if 'logged_in' in session:
        return jsonify({'logged_in': True, 'email': session.get('user_email')}), 200
    return jsonify({'logged_in': False}), 200

@app.route('/api/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file'}), 400
    
    try:
        duration = int(request.form.get('duration', 10))
        quality = request.form.get('quality', 'ultra')
        style = request.form.get('style', 'particle_powder')
        
        temp_dir = tempfile.mkdtemp()
        
        try:
            input_path = os.path.join(temp_dir, secure_filename(file.filename))
            file.save(input_path)
            
            output_path = os.path.join(temp_dir, f"animation_{uuid.uuid4()}.mp4")
            
            env = {**os.environ, 
                   'ANIMATION_INPUT_PATH': input_path, 
                   'ANIMATION_OUTPUT_PATH': output_path,
                   'ANIMATION_DURATION': str(duration),
                   'ANIMATION_QUALITY': quality,
                   'ANIMATION_STYLE': style}
            
            subprocess.run(['python3', 'animate_painting_premium.py'], env=env, check=True, timeout=300)
            
            if not os.path.exists(output_path):
                raise Exception("Animation file was not generated.")

            return send_file(output_path, as_attachment=True, download_name="animation.mp4", mimetype='video/mp4')
        
        finally:
            shutil.rmtree(temp_dir)
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status')
def status():
    return jsonify({'status': 'running', 'version': '2.0'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 