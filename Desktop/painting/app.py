from flask import Flask, request, render_template, send_file, jsonify, after_this_request, session, redirect, url_for, flash
import os
import subprocess
import tempfile
import uuid
import shutil
from werkzeug.utils import secure_filename
import time
from functools import wraps

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SECRET_KEY'] = 'particle_animation_secret_key_2024'  # Change this in production

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
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html', user_email=session.get('user_email'))

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload an image file.'}), 400
        
        # Get animation options from form
        duration = int(request.form.get('duration', 10))  # Default 10 seconds
        quality = request.form.get('quality', 'ultra')    # Default ultra quality
        style = request.form.get('style', 'particle_powder')  # Default particle style
        
        # Validate duration (5-30 seconds)
        duration = max(5, min(30, duration))
        
        # Create temporary directory for this job
        job_id = str(uuid.uuid4())
        temp_dir = tempfile.mkdtemp(prefix=f'painting_job_{job_id}_')
        
        try:
            # Save uploaded file temporarily
            filename = secure_filename(file.filename)
            file_extension = filename.rsplit('.', 1)[1].lower()
            input_path = os.path.join(temp_dir, f'input.{file_extension}')
            output_path = os.path.join(temp_dir, 'output.mp4')
            
            file.save(input_path)
            
            # Run the animation script
            script_path = os.path.abspath('animate_painting_premium.py')
            
            # Modify the environment to use our temp files and options
            env = os.environ.copy()
            env['PAINTING_INPUT_PATH'] = input_path
            env['PAINTING_OUTPUT_PATH'] = output_path
            env['ANIMATION_DURATION'] = str(duration)
            env['ANIMATION_QUALITY'] = quality
            env['ANIMATION_STYLE'] = style
            
            print(f"🎬 Starting animation for job {job_id}")
            print(f"📁 Input: {input_path}")
            print(f"📁 Output: {output_path}")
            print(f"⏱️ Duration: {duration}s | Quality: {quality} | Style: {style}")
            
            # Calculate timeout based on duration (longer videos need more time)
            timeout_seconds = max(300, duration * 30)  # At least 5 minutes, more for longer videos
            
            # Run the script
            result = subprocess.run(
                ['python', script_path],
                env=env,
                cwd=os.path.dirname(script_path),
                capture_output=True,
                text=True,
                timeout=timeout_seconds
            )
            
            if result.returncode != 0:
                print(f"❌ Animation failed for job {job_id}")
                print(f"Error: {result.stderr}")
                return jsonify({
                    'error': f'Animation failed: {result.stderr}'
                }), 500
            
            if not os.path.exists(output_path):
                return jsonify({
                    'error': 'Animation completed but output file not found'
                }), 500
            
            print(f"✅ Animation completed for job {job_id}")
            
            # Clean up function to run after response is sent
            @after_this_request
            def cleanup(response):
                try:
                    time.sleep(1)  # Give time for download to start
                    shutil.rmtree(temp_dir)
                    print(f"🧹 Cleaned up temporary files for job {job_id}")
                except Exception as e:
                    print(f"⚠️ Cleanup failed for job {job_id}: {e}")
                return response
            
            # Send the video file
            return send_file(
                output_path,
                as_attachment=True,
                download_name=f'particle_animation_{duration}s_{quality}_{int(time.time())}.mp4',
                mimetype='video/mp4'
            )
            
        except subprocess.TimeoutExpired:
            return jsonify({'error': f'Animation processing timed out ({timeout_seconds//60} minute limit)'}), 500
        except Exception as e:
            print(f"❌ Unexpected error for job {job_id}: {e}")
            return jsonify({'error': f'Processing error: {str(e)}'}), 500
        finally:
            # Fallback cleanup in case something goes wrong
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
            except:
                pass
                
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return jsonify({'error': f'Upload error: {str(e)}'}), 500

@app.route('/status')
@login_required
def status():
    return jsonify({'status': 'ready', 'user': session.get('user_email')})

if __name__ == '__main__':
    # Ensure templates directory exists
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)  # For logo and other static files
    
    print("🎨 Particle Animation Web App")
    print("🌐 Starting Flask server...")
    print("📁 Make sure animate_painting_premium.py is in the same directory")
    print("🚀 Visit: http://localhost:5001")
    print("🔐 Login: olimpia@makincome.com / Chanel2808")
    
    app.run(debug=True, host='0.0.0.0', port=5001) 