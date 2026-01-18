#!/usr/bin/env python3
"""
Coffee Bot Web Interface - PCA9685 Servo Driver Version
Flask web server for controlling coffee brewing with servos via Waveshare Servo Driver HAT
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import time
from datetime import datetime
import os
import secrets
import qrcode
import threading
import requests
from adafruit_servokit import ServoKit
import logging
import markdown

app = Flask(__name__)

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('coffee_bot.log'),
        logging.StreamHandler()  # Still print to console too
    ]
)

# Create logger instance
logger = logging.getLogger(__name__)

# ============================================================================
# SERVO CONFIGURATION
# ============================================================================

# Servo Channel Assignments on PCA9685
SERVO_POWER_CHANNEL = 0   # Channel 0 - Power button
SERVO_BREW_CHANNEL = 1    # Channel 1 - Brew button

# Servo Angle Settings
servo_config = {
    'rest_angle': 0,       # Starting/resting position (degrees)
    'active_angle': 45,    # Activated position (degrees)
    'move_time': 0.3,      # Time to allow servo to complete movement (seconds)
    'hold_time': 0.25,     # Time to hold in active position (seconds)
}

# Auto brew sequence timing
auto_brew_config = {
    'power_on_delay': 2.0,  # Seconds to wait after power on before brewing
}

# ============================================================================
# NTFY CONFIGURATION
# ============================================================================

NTFY_TOPIC_FILE = "ntfy_topic.txt"
STATIC_FOLDER = "static"
QR_CODE_PATH = os.path.join(STATIC_FOLDER, "ntfy_qr.png")

# Topic variable - will be initialized on first use
ntfy_topic = None

def get_or_create_topic():
    """Get existing topic or create a new one"""
    if os.path.exists(NTFY_TOPIC_FILE):
        with open(NTFY_TOPIC_FILE, 'r') as f:
            return f.read().strip()
    else:
        return regenerate_topic()

def get_ntfy_topic():
    """Get the current ntfy topic, initializing if needed (lazy initialization)"""
    global ntfy_topic
    if ntfy_topic is None:
        ntfy_topic = get_or_create_topic()
    return ntfy_topic

def regenerate_topic():
    """Generate a new random topic and save it"""
    new_topic = f"coffeebot-{secrets.token_urlsafe(16)}"
    try:
        with open(NTFY_TOPIC_FILE, 'w') as f:
            f.write(new_topic)
        # Set restrictive permissions (owner read/write only)
        os.chmod(NTFY_TOPIC_FILE, 0o600)
        generate_qr_code(new_topic)
        logger.info(f"Generated new ntfy topic: {new_topic}")
    except IOError as e:
        logger.error(f"Error saving topic: {e}")
    return new_topic

def generate_qr_code(topic):
    """Generate QR code for ntfy topic"""
    try:
        os.makedirs(STATIC_FOLDER, exist_ok=True)
        ntfy_url = f"ntfy://ntfy.sh/{topic}"
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(ntfy_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(QR_CODE_PATH)
        logger.debug("QR code generated successfully")
    except Exception as e:
        logger.error(f"Error generating QR code: {e}")

def send_ntfy_notification(message):
    """Send notification to ntfy topic"""
    try:
        topic = get_ntfy_topic()
        response = requests.post(
            f"https://ntfy.sh/{topic}",
            data=message.encode('utf-8'),
            headers={"Title": "Coffee Bot"},
            timeout=5
        )
        response.raise_for_status()
        logger.debug(f"Notification sent: {message}")
    except requests.RequestException as e:
        logger.warning(f"Failed to send notification: {e}")

# ============================================================================
# RATE LIMITING AND OPERATION LOCKING
# ============================================================================

# Global lock to prevent concurrent servo operations
servo_operation_lock = threading.Lock()

# Lock for topic regeneration
topic_regeneration_lock = threading.Lock()

# Rate limiting to prevent button spam
last_button_press = {}
rate_limit_lock = threading.Lock()

# Minimum seconds between button presses (adjustable)
RATE_LIMIT_SECONDS = 3

def check_rate_limit(button):
    """
    Check if enough time has passed since last button press.
    
    Args:
        button: Button name ('power', 'brew', 'auto')
        
    Returns:
        Tuple of (allowed: bool, seconds_remaining: float)
    """
    with rate_limit_lock:
        now = datetime.now()
        last_press = last_button_press.get(button)
        
        if last_press is None:
            last_button_press[button] = now
            return True, 0
        
        time_since_last = (now - last_press).total_seconds()
        
        if time_since_last >= RATE_LIMIT_SECONDS:
            last_button_press[button] = now
            return True, 0
        else:
            remaining = RATE_LIMIT_SECONDS - time_since_last
            return False, remaining

# ============================================================================
# SERVO CONTROL FUNCTIONS
# ============================================================================

kit = None

def setup_servos():
    """Initialize PCA9685 servo controller"""
    global kit
    
    try:
        # Initialize ServoKit for 16 channels (Waveshare Servo Driver HAT)
        kit = ServoKit(channels=16)
        
        # Set servos to rest position
        kit.servo[SERVO_POWER_CHANNEL].angle = servo_config['rest_angle']
        kit.servo[SERVO_BREW_CHANNEL].angle = servo_config['rest_angle']
        
        # Give servos time to reach position
        time.sleep(0.5)
        
        logger.info("Servos initialized successfully")
        logger.info(f"Power servo: Channel {SERVO_POWER_CHANNEL}")
        logger.info(f"Brew servo: Channel {SERVO_BREW_CHANNEL}")
        
    except Exception as e:
        logger.error(f"ERROR initializing servos: {e}")
        raise

def activate_servo(channel, servo_name="Servo"):
    """
    Activate servo: move to active position, hold, return to rest
    
    Args:
        channel: PCA9685 channel number (0-15)
        servo_name: Descriptive name for logging
    """
    logger.info(f"Activating {servo_name}")
    
    try:
        # Move to active position
        kit.servo[channel].angle = servo_config['active_angle']
        time.sleep(servo_config['move_time'])
        
        # Hold position
        time.sleep(servo_config['hold_time'])
        
        # Return to rest position
        kit.servo[channel].angle = servo_config['rest_angle']
        time.sleep(servo_config['move_time'])
        
        logger.info(f"{servo_name} operation complete")
        
    except Exception as e:
        logger.error(f"ERROR during {servo_name} operation: {e}")
        raise

def press_power(notify=True):
    """
    Press the power button
    
    Args:
        notify: Send ntfy notification (default: True)
    """
    logger.info("Pressing POWER button")
    activate_servo(SERVO_POWER_CHANNEL, "Power Button")
    if notify:
        send_ntfy_notification("☕ Power button pressed")

def press_brew(notify=True):
    """
    Press the brew button
    
    Args:
        notify: Send ntfy notification (default: True)
    """
    logger.info("Pressing BREW button")
    activate_servo(SERVO_BREW_CHANNEL, "Brew Button")
    if notify:
        send_ntfy_notification("☕ Brew button pressed")

def auto_brew():
    """Automated brew sequence: Power on, wait, then brew"""
    logger.info("=" * 50)
    logger.info("AUTO BREW SEQUENCE STARTED")
    logger.info("=" * 50)
    
    send_ntfy_notification("☕ Coffee maker powered on and brew started!")
    
    # Press power button (no notification)
    press_power(notify=False)
    logger.info(f"Waiting {auto_brew_config['power_on_delay']} seconds for coffee maker to power on...")
    time.sleep(auto_brew_config['power_on_delay'])
    
    # Press brew button (no notification)
    press_brew(notify=False)
    
    logger.info("Auto brew sequence complete!")

# ============================================================================
# WEB ROUTES
# ============================================================================

@app.route('/')
def index():
    """Main page"""
    delay = auto_brew_config['power_on_delay']
    delay_text = int(delay) if delay == int(delay) else delay
    return render_template('index.html', 
                          ntfy_topic=get_ntfy_topic(),
                          power_on_delay=delay_text)

@app.route('/press/<button>')
def press_button(button):
    """
    Handle button presses with rate limiting and operation locking.
    
    Validates input, enforces rate limits, and prevents concurrent operations
    to protect servo hardware from abuse or accidental damage.
    """
    # Validate button name
    valid_buttons = ['power', 'brew', 'auto']
    if button not in valid_buttons:
        logger.warning(f"Invalid button request: {button}")
        return jsonify({
            'error': 'Invalid button',
            'message': f'Button must be one of: {", ".join(valid_buttons)}'
        }), 400
    
    # Check if servos are initialized
    if kit is None:
        logger.error("Button press attempted but servos not initialized")
        return jsonify({
            'error': 'Hardware not initialized',
            'message': 'Servo controller not detected. Check I2C connection and restart service.'
        }), 503  # Service Unavailable
    
    # Check rate limit (fast check before acquiring lock)
    allowed, remaining = check_rate_limit(button)
    if not allowed:
        logger.debug(f"Rate limit hit for {button}: {remaining:.1f}s remaining")
        return jsonify({
            'error': 'Rate limit exceeded',
            'message': f'Please wait {remaining:.1f} seconds before pressing {button} again',
            'retry_after': remaining
        }), 429
    
    # Try to acquire operation lock (non-blocking)
    if not servo_operation_lock.acquire(blocking=False):
        logger.warning(f"Operation lock conflict for {button}")
        return jsonify({
            'error': 'Operation in progress',
            'message': 'Another servo operation is currently running. Please wait and try again.'
        }), 409
    
    try:
        # Log the action with timestamp and source IP
        client_ip = request.remote_addr if request else 'unknown'
        logger.info(f"Button '{button}' pressed from {client_ip}")
        
        # Execute the requested action
        if button == 'power':
            press_power()
            message = 'Power button pressed'
        elif button == 'brew':
            press_brew()
            message = 'Brew button pressed'
        elif button == 'auto':
            auto_brew()
            message = 'Auto brew sequence started'
        
        return jsonify({
            'success': True,
            'message': message
        }), 200
        
    except Exception as e:
        # Log error and return failure response
        logger.error(f"ERROR during {button} operation: {e}", exc_info=True)
        return jsonify({
            'error': 'Operation failed',
            'message': f'Failed to execute {button} operation',
            'details': str(e)
        }), 500
    finally:
        # Always release the lock, even if an error occurred
        servo_operation_lock.release()

@app.route('/regenerate_topic', methods=['POST'])
def regenerate_topic_route():
    """Generate a new ntfy topic"""
    global ntfy_topic
    
    client_ip = request.remote_addr if request else 'unknown'
    logger.info(f"Topic regeneration requested from {client_ip}")
    
    with topic_regeneration_lock:
        ntfy_topic = regenerate_topic()
        return jsonify({
            'success': True,
            'new_topic': ntfy_topic,
            'message': 'Topic regenerated successfully! Scan the new QR code to resubscribe.'
        })

@app.route('/status')
def status():
    """Return system status for debugging"""
    servo_status = "initialized" if kit is not None else "not initialized"
    
    status_info = {
        'servo_driver': servo_status,
        'ntfy_topic': get_ntfy_topic(),
        'rate_limit_seconds': RATE_LIMIT_SECONDS,
        'servo_config': servo_config,
        'auto_brew_config': auto_brew_config
    }
    
    logger.debug(f"Status check requested from {request.remote_addr}")
    return jsonify(status_info)

# ============================================================================
# DOCUMENTATION ROUTES
# ============================================================================

@app.route('/docs/')
@app.route('/docs/<path:filename>')
def serve_docs(filename='index'):
    """Serve documentation from /docs folder as HTML"""
    try:
        # Read the markdown file
        md_path = os.path.join('docs', f'{filename}.md')
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Convert to HTML with extensions
        html_content = markdown.markdown(
            content, 
            extensions=[
                'extra',           # Tables, footnotes, attr_list, etc.
                'codehilite',      # Code highlighting
                'fenced_code',     # ```code blocks```
                'tables',          # Table support
                'nl2br',           # Newline to <br>
                'sane_lists',      # Better list handling
                'toc'              # Table of contents with anchor links
            ]
        )
        
        # Wrap in template
        return render_template('docs.html', content=html_content, title=filename.replace('-', ' ').title())
    except FileNotFoundError:
        logger.warning(f"Documentation file not found: {filename}")
        return render_template('docs.html', 
                             content="<h1>404 - Documentation Not Found</h1><p>The requested documentation page could not be found.</p>",
                             title="Not Found"), 404

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    logger.info("Coffee Bot Web Interface - PCA9685 Servo Driver Version")
    logger.info("-" * 50)
    logger.info(f"ntfy topic: {get_ntfy_topic()}")
    logger.info("-" * 50)
    
    servo_init_success = False
    try:
        setup_servos()
        servo_init_success = True
    except Exception as e:
        logger.warning(f"Servo initialization failed: {e}")
        logger.warning("Web interface will start, but servo controls will not work.")
        logger.warning("Check I2C connection and HAT seating, then restart service.")
    
    try:
        logger.info("Starting web server on port 5000...")
        logger.info("-" * 50)
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"ERROR during startup: {e}", exc_info=True)
    finally:
        logger.info("Cleanup complete")