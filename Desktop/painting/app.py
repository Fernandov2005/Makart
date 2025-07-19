from flask import Flask, request, render_template, send_file, jsonify, after_this_request, session, redirect, url_for, flash
import os
import subprocess
import tempfile
import uuid
import shutil
from werkzeug.utils import secure_filename
import time
from functools import wraps

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'particle_animation_secret_key_2024')

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}

# Login credentials
VALID_EMAIL = "olimpia@makincome.com"
VALID_PASSWORD = "Chanel2808"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if email == VALID_EMAIL and password == VALID_PASSWORD:
            session['logged_in'] = True
            session['user_email'] = email
            flash('Welcome! You have successfully logged in.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password. Please try again.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/')
def home():
    # Redirect to login if not authenticated
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('index'))

@app.route('/index')
@login_required  
def index():
    user_email = session.get('user_email', 'User')
    return render_template('index.html', user_email=user_email)

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not supported'}), 400
    
    try:
        # Get animation parameters from form
        duration = int(request.form.get('duration', 10))
        quality = request.form.get('quality', 'ultra')
        style = request.form.get('style', 'particle_powder')
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Save uploaded file
            filename = secure_filename(file.filename)
            file_extension = filename.rsplit('.', 1)[1].lower()
            temp_filename = f"input_{uuid.uuid4()}.{file_extension}"
            input_path = os.path.join(temp_dir, temp_filename)
            file.save(input_path)
            
            # Output file path
            output_filename = f"particle_animation_{uuid.uuid4()}.mp4"
            output_path = os.path.join(temp_dir, output_filename)
            
            # Set environment variables for the animation script
            env = os.environ.copy()
            env['ANIMATION_INPUT_PATH'] = input_path
            env['ANIMATION_OUTPUT_PATH'] = output_path
            env['ANIMATION_DURATION'] = str(duration)
            env['ANIMATION_QUALITY'] = quality
            env['ANIMATION_STYLE'] = style
            
            print(f"🎨 Starting animation: {duration}s, {quality} quality, {style} style")
            print(f"📁 Input: {input_path}")
            print(f"📁 Output: {output_path}")
            
            # Run animation script
            try:
                result = subprocess.run([
                    'python3', 'animate_painting_premium.py'
                ], env=env, capture_output=True, text=True, timeout=300)  # 5 minute timeout
                
                print(f"🔄 Animation script exit code: {result.returncode}")
                if result.stdout:
                    print(f"📝 Script output: {result.stdout}")
                if result.stderr:
                    print(f"⚠️ Script errors: {result.stderr}")
                
                if result.returncode != 0:
                    raise subprocess.CalledProcessError(result.returncode, 'animate_painting_premium.py', result.stderr)
                
            except subprocess.TimeoutExpired:
                print("⏰ Animation script timed out")
                raise Exception("Animation processing timed out. Please try with a smaller image or lower quality setting.")
            except subprocess.CalledProcessError as e:
                print(f"💥 Animation script failed: {e}")
                raise Exception(f"Animation processing failed: {e.stderr}")
            except Exception as e:
                print(f"🚨 Unexpected error: {e}")
                raise Exception(f"Animation processing error: {str(e)}")
            
            # Check if output file was created
            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                raise Exception("Animation file was not generated properly")
            
            print(f"✅ Animation complete: {output_path} ({os.path.getsize(output_path)} bytes)")
            
            # Create a function to cleanup after sending file
            @after_this_request
            def cleanup(response):
                try:
                    shutil.rmtree(temp_dir)
                    print(f"🧹 Cleaned up temporary directory: {temp_dir}")
                except Exception as e:
                    print(f"⚠️ Failed to cleanup {temp_dir}: {e}")
                return response
            
            # Send file with proper headers
            return send_file(
                output_path,
                as_attachment=True,
                download_name=f"particle_animation_{duration}s_{quality}.mp4",
                mimetype='video/mp4'
            )
            
        except Exception as e:
            print(f"💥 Upload processing error: {e}")
            # Cleanup on error
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
            return jsonify({'error': str(e)}), 500
            
    except Exception as e:
        print(f"🚨 General upload error: {e}")
        return jsonify({'error': 'Failed to process file'}), 500

@app.route('/status')
def status():
    return jsonify({
        'status': 'running',
        'message': 'Makart Particle Animation Studio',
        'version': '2.0'
    })

# Ensure directories exist
os.makedirs('templates', exist_ok=True)
os.makedirs('static', exist_ok=True)

# For local development
if __name__ == '__main__':
    print("🎨 Makart Particle Animation Studio")
    print("🌐 Starting Flask server...")
    print("🚀 Visit: http://localhost:5001")
    print("🔐 Login: olimpia@makincome.com / Chanel2808")
    
    app.run(debug=True, host='0.0.0.0', port=5001) 