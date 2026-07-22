from flask import Flask, render_template, jsonify, request, Response, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import cv2
import logging
import requests
import os
import numpy as np
from utils.serial_handler import SerialHandler
from utils.ai_detector import AIDetector
from utils.email_utils import EmailHandler
from models import db, User, ScanLog
from config import *

# Setup logging
logging.basicConfig(level=logging.INFO if not DEBUG else logging.DEBUG)
logger = logging.getLogger(__name__)

# --- Global Variables ---
last_classification = None
bin_levels = {'plastic': 0, 'paper': 0, 'glass': 0}
serial_handler = None
ai_detector = None
email_handler = None
camera_active = False # Global state for the camera

# --- Helper function for reverse geocoding using OpenStreetMap ---
def get_location_name_from_coords(lat, lng):
    """Converts latitude and longitude to a human-readable location name using OpenStreetMap Nominatim."""
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {'format': 'jsonv2', 'lat': lat, 'lon': lng}
        headers = {'User-Agent': 'SmartWasteBinApp/1.0'}
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data and 'display_name' in data:
            return data['display_name']
        else:
            logger.warning(f"Nominatim could not find an address for lat:{lat}, lng:{lng}.")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Request to Nominatim API failed: {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred during geocoding: {e}")
        return None

# --- Application Factory ---

# --- Application Factory ---
def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    
    # --- Database Setup ---
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'users.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)

    # --- Auth Setup ---
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # --- ALL ROUTES MUST BE INSIDE THIS FUNCTION ---
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            lat = request.form.get('latitude')
            lng = request.form.get('longitude')

            if User.query.filter_by(email=username).first():
                flash('User already exists!')
                return render_template('register.html')

            new_user = User(
                email=username,
                location_lat=float(lat) if lat else 0.0,
                location_lng=float(lng) if lng else 0.0
            )
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            flash('Registered! Please login.')
            return redirect(url_for('login'))

        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            lat = request.form.get('latitude')
            lng = request.form.get('longitude')

            user = User.query.filter_by(email=username).first()

            if user and user.check_password(password):
                login_user(user)

                if lat and lng:
                    user.location_lat = float(lat)
                    user.location_lng = float(lng)
                    location_name = get_location_name_from_coords(float(lat), float(lng))
                    user.location_name = location_name
                    db.session.commit()
                    
                    if location_name:
                        flash(f'Logged in successfully from {location_name}!')
                    else:
                        flash('Logged in successfully! (Location could not be determined)')
                else:
                    flash('Logged in successfully!')

                return redirect(url_for('index'))
            else:
                flash('Invalid credentials!')

        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('Logged out!')
        return redirect(url_for('login'))

    @app.route('/')
    @login_required
    def index():
        return render_template('index.html', user=current_user)

    @app.route('/video_feed')
    @login_required
    def video_feed():
        def gen_frames():
            global camera_active
            if not camera_active:
                # Return a single placeholder frame then stop generator
                offline_img = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(offline_img, "CAMERA OFF", (220, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                ret, buffer = cv2.imencode('.jpg', offline_img)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                return

            camera = cv2.VideoCapture(0)
            if not camera.isOpened():
                logger.error("Could not open camera")
                return

            while camera_active:
                success, frame = camera.read()
                if not success:
                    break
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            camera.release()

        return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    @app.route('/toggle_camera', methods=['POST'])
    @login_required
    def toggle_camera():
        global camera_active
        camera_active = not camera_active
        # Clear resources if turning off? video_feed loop handles release
        status = "on" if camera_active else "off"
        return jsonify({'status': f'Camera turned {status}', 'active': camera_active})

    @app.route('/detect_waste', methods=['POST'])
    @login_required
    def detect_waste():
        global last_classification, bin_levels
        
        # Capture single frame
        camera = cv2.VideoCapture(0) # In a real app, share the cap object or use a lock
        if not camera.isOpened():
             return jsonify({'error': 'Camera not available'}), 500
             
        success, frame = camera.read()
        camera.release()
        
        if not success:
            return jsonify({'error': 'Camera capture failed'}), 500

        classification = ai_detector.classify_waste(frame)
        last_classification = classification
        
        if classification and classification != 'unknown':
            # Log the scan
            new_log = ScanLog(waste_type=classification)
            db.session.add(new_log)
            db.session.commit()

            # Determine command key (wrapper -> paper)
            key = classification if classification != 'wrapper' else 'paper'
            if key in SERVO_COMMANDS:
                serial_handler.send_command(SERVO_COMMANDS[key])
            else:
                logger.warning(f"No servo command for classification: {classification}")
        
        bin_levels = serial_handler.get_levels()
        
        # Check alerts
        for bin_type, level in bin_levels.items():
            if level > 90: # Threshold
                email_handler.send_alert(bin_type, level)
        
        mode = " (Dummy Mode)" if not OPENAI_API_KEY else ""
        return jsonify({
            'classification': classification,
            'levels': bin_levels,
            'message': f'Opened {classification} compartment!{mode}'
        })

    @app.route('/manual_control', methods=['POST'])
    @login_required
    def manual_control():
        action = request.json.get('action')
        if not action:
             return jsonify({'error': 'No action provided'}), 400

        # action is like 'plastic', 'paper', 'glass'
        if action in SERVO_COMMANDS:
            if not serial_handler.send_command(SERVO_COMMANDS[action]):
                 return jsonify({'error': 'Arduino not connected (Check USB/Port)'}), 503
        else:
            return jsonify({'error': 'Invalid or unsupported action'}), 400
        
        global bin_levels
        bin_levels = serial_handler.get_levels()
        
        # Add message for UI feedback
        icon_map = {
            'plastic': '🥤', 
            'paper': '📄', 
            'glass': '🍾',
            'beep': '🔊',
            'reset': '🔄'
        }
        icon = icon_map.get(action, '⚙️')
        
        return jsonify({
            'status': 'Command sent',
            'levels': bin_levels,
            'message': f"Opening {action.capitalize()}",
            'icon': icon
        })

    @app.route('/status')
    @login_required
    def status():
        global bin_levels, last_classification
        # FETCH FRESH DATA FROM ARDUINO
        try:
           if serial_handler:
               bin_levels = serial_handler.get_levels()
        except Exception as e:
            logger.error(f"Error fetching levels for status: {e}")

        # Recalculate alerts based on fresh data
        alerts = [f'{k.capitalize()} bin full!' for k, v in bin_levels.items() if v > 80]
        
        # TRIGGER EMAIL ALERTS
        # Now we check for emails in the status loop too, so "Active Sync" monitors for us
        try:
            for bin_type, level in bin_levels.items():
                if level > 90: # Email Threshold
                    if email_handler:
                        email_handler.send_alert(bin_type, level)
        except Exception as e:
            logger.error(f"Error triggering alerts in status: {e}")

        return jsonify({
            'last_classification': last_classification,
            'bin_levels': bin_levels,
            'alerts': alerts
        })

    @app.route('/history')
    @login_required
    def history():
        logs = ScanLog.query.order_by(ScanLog.timestamp.desc()).limit(50).all()
        return render_template('history.html', logs=logs)

    @app.route('/about')
    def about():
        return render_template('about.html')

    @app.route('/test_email')
    @login_required
    def test_email():
        try:
            # Force send ignoring cooldown for test
            email_handler.send_alert("test", 100)
            return jsonify({'status': 'Email sent successfully (check logs if not received)'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # --- Initialize Globals and Handlers (inside factory) ---
    global last_classification, bin_levels, serial_handler, ai_detector, email_handler
    last_classification = None
    bin_levels = {'plastic': 0, 'paper': 0, 'glass': 0}
    serial_handler = SerialHandler(ARDUINO_PORT, BAUD_RATE)
    ai_detector = AIDetector(OPENAI_API_KEY)
    email_handler = EmailHandler()

    return app


# --- Main Execution Block ---
if __name__ == '__main__':
    app = create_app()
    
    # This block creates the database file and tables before the first request
    with app.app_context():
        db.create_all()

    conn_status = serial_handler.test_connection()
    api_status = 'Ready' if OPENAI_API_KEY else 'Dummy mode (set key for real AI)'
    cam_status = 'OK' if cv2.VideoCapture(0).isOpened() else 'Failed - check USB'

    print(f"=== Smart Waste Bin App Starting ===")
    print(f"Database: SQLite (users.db)")
    print(f"Arduino: {'Connected!' if conn_status else 'Not connected (manual off)'}")
    print(f"OpenAI: {api_status}")
    print(f"Camera: {cam_status}")
    print(f"Run at: http://{HOST}:{PORT}")
    print("=====================================")

    app.run(host=HOST, port=PORT, debug=DEBUG)