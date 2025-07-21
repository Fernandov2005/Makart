from flask import Flask, request, jsonify, send_file, session
from flask_cors import CORS
import os
import subprocess
import tempfile
import uuid
import shutil
from werkzeug.utils import secure_filename
from functools import wraps
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a_secure_secret_key')

# Configure CORS to be more robust
CORS(app, 
     origins=["https://makart.vercel.app", "http://localhost:3000"], 
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

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'version': '2.1'}), 200

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({'status': 'running', 'version': '2.1', 'env': 'production'}), 200

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email')
        password = data.get('password')
        
        logger.info(f"Login attempt for email: {email}")

        if email == VALID_EMAIL and password == VALID_PASSWORD:
            session['logged_in'] = True
            session['user_email'] = email
            logger.info("Login successful")
            return jsonify({'message': 'Login successful', 'email': email}), 200
        
        logger.warning("Login failed - invalid credentials")
        return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
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
        logger.error(f"Session check error: {str(e)}")
        return jsonify({'logged_in': False}), 200

@app.route('/api/upload', methods=['POST'])
@login_required
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file'}), 400
        
        duration = int(request.form.get('duration', 10))
        quality = request.form.get('quality', 'ultra')
        style = request.form.get('style', 'particle_powder')
        
        logger.info(f"Processing upload: {file.filename}, duration: {duration}")
        
        # For now, return a demo response since we're in lightweight mode
        # This allows login/auth to work while animation dependencies are being resolved
        return jsonify({
            'message': 'Upload received successfully! Animation processing is being prepared.',
            'filename': file.filename,
            'duration': duration,
            'quality': quality,
            'style': style,
            'status': 'demo_mode'
        }), 202  # 202 Accepted
        
        # TODO: Uncomment below when full dependencies are available
        """
        temp_dir = tempfile.mkdtemp()
        
        try:
            input_path = os.path.join(temp_dir, secure_filename(file.filename))
            file.save(input_path)
            
            output_path = os.path.join(temp_dir, f"animation_{uuid.uuid4()}.mp4")
            
            # Check if animation script exists
            script_path = os.path.join(os.path.dirname(__file__), '..', 'animate_painting_premium.py')
            if not os.path.exists(script_path):
                logger.error(f"Animation script not found at: {script_path}")
                return jsonify({'error': 'Animation service unavailable'}), 500
            
            env = {**os.environ, 
                   'ANIMATION_INPUT_PATH': input_path, 
                   'ANIMATION_OUTPUT_PATH': output_path,
                   'ANIMATION_DURATION': str(duration),
                   'ANIMATION_QUALITY': quality,
                   'ANIMATION_STYLE': style}
            
            logger.info("Starting animation process")
            result = subprocess.run(['python3', script_path], env=env, check=True, timeout=300, 
                                  capture_output=True, text=True)
            
            if not os.path.exists(output_path):
                logger.error("Animation file was not generated")
                return jsonify({'error': 'Animation generation failed'}), 500

            logger.info("Animation completed successfully")
            return send_file(output_path, as_attachment=True, download_name="animation.mp4", mimetype='video/mp4')
        
        finally:
            shutil.rmtree(temp_dir)
        """
            
    except subprocess.TimeoutExpired:
        logger.error("Animation process timed out")
        return jsonify({'error': 'Animation processing timed out'}), 500
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("Starting Makart backend server")
    app.run(debug=True, host='0.0.0.0', port=5001) 