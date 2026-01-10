#!/usr/bin/env python3
"""
Coffee Bot Web Interface - Servo Control Version
Flask web server for controlling coffee brewing with MG90S servos
"""

from flask import Flask, render_template, request, jsonify
import RPi.GPIO as GPIO
import time
from datetime import datetime, timedelta
import os
import secrets
import qrcode
from io import BytesIO
import threading

app = Flask(__name__)

# ============================================================================
# SERVO CONFIGURATION
# ============================================================================

# Servo GPIO Pins (connected directly to Pi GPIO)
SERVO_1_PIN = 12  # GPIO 12 (Pin 32) - Power button
SERVO_2_PIN = 13  # GPIO 13 (Pin 33) - Brew button

# Servo PWM Frequency
SERVO_FREQUENCY = 50  # Hz (20ms period)

# Servo Pulse Width Settings (in milliseconds)
# These define the pulse widths for minimum (0°) and maximum (180°) positions.
# 
# Standard servos typically use:
#   - min_pulse_ms: 1.0 (0° position)
#   - max_pulse_ms: 2.0 (180° position)
#
# Extended range (current settings):
#   - min_pulse_ms: 0.5 (allows rotation beyond 0°)
#   - max_pulse_ms: 2.5 (allows rotation beyond 180°)
#
# Note: Extended range provides greater rotation but may not work with all servos.
# If your servo jitters, doesn't move, or moves too far, try standard values (1.0-2.0).
servo_pulse_config = {
    'min_pulse_ms': 0.5,   # Pulse width for 0° position
    'max_pulse_ms': 2.5,   # Pulse width for 180° position
}

# Servo Angle Settings
servo_config = {
    'rest_angle': 0,       # Starting/resting position (degrees)
    'active_angle': 45,    # Activated position (degrees)
    'move_time': 0.3,      # Time for servo to complete movement (seconds)
    'hold_time': 0.25,     # Time to hold in active position (seconds)
}

# Set the delay between powering on and brewing for the auto brew sequence
auto_brew_config = {
    'power_on_delay': 2.0,  # Seconds to wait after power on
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
        generate_qr_code(new_topic)
    except IOError as e:
        print(f"Error saving topic: {e}")
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
    except Exception as e:
        print(f"Error generating QR code: {e}")

def send_ntfy_notification(message):
    """Send notification to ntfy topic"""
    try:
        import requests
        topic = get_ntfy_topic()
        requests.post(
            f"https://ntfy.sh/{topic}",
            data=message.encode('utf-8'),
            headers={"Title": "Coffee Bot"},
            timeout=5  # Add timeout
        )
    except Exception as e:
        print(f"Failed to send notification: {e}")

# ============================================================================
# RATE LIMITING AND OPERATION LOCKING
# ============================================================================

# Global lock to prevent concurrent servo operations
servo_operation_lock = threading.Lock()

# Rate limiting to prevent button spam
last_button_press = {}
rate_limit_lock = threading.Lock()

# Minimum seconds between button presses (adjustable)
RATE_LIMIT_SECONDS = 3  # Prevents accidental double-clicks and spam

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
            # First press of this button
            last_button_press[button] = now
            return True, 0
        
        time_since_last = (now - last_press).total_seconds()
        
        if time_since_last >= RATE_LIMIT_SECONDS:
            # Enough time has passed
            last_button_press[button] = now
            return True, 0
        else:
            # Too soon - still in cooldown
            remaining = RATE_LIMIT_SECONDS - time_since_last
            return False, remaining

# ============================================================================
# SERVO CONTROL FUNCTIONS
# ============================================================================

servo1 = None
servo2 = None

def setup_servos():
    """Initialize GPIO and servo PWM"""
    global servo1, servo2
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    GPIO.setup(SERVO_1_PIN, GPIO.OUT)
    GPIO.setup(SERVO_2_PIN, GPIO.OUT)
    
    # Calculate the rest position duty cycle
    rest_duty = angle_to_duty_cycle(servo_config['rest_angle'])
    
    servo1 = GPIO.PWM(SERVO_1_PIN, SERVO_FREQUENCY)
    servo2 = GPIO.PWM(SERVO_2_PIN, SERVO_FREQUENCY)
    
    # Start at rest position instead of 0
    servo1.start(rest_duty)
    servo2.start(rest_duty)
    
    # Give servos time to settle
    time.sleep(0.5)
    
    # Turn off PWM signal after reaching rest position
    servo1.ChangeDutyCycle(0)
    servo2.ChangeDutyCycle(0)


def angle_to_duty_cycle(angle):
    """
    Convert angle (0-180 degrees) to PWM duty cycle percentage.
    
    At 50Hz, the PWM period is 20ms. Servos expect pulse widths between
    their min and max values (typically 1-2ms for standard servos).
    
    The duty cycle is: (pulse_width / period) * 100%
    
    Args:
        angle: Desired angle in degrees (0-180)
        
    Returns:
        Duty cycle as percentage (0-100)
    """
    # Get configured pulse width range
    min_pulse = servo_pulse_config['min_pulse_ms']
    max_pulse = servo_pulse_config['max_pulse_ms']
    
    # Calculate pulse width for the requested angle
    pulse_range = max_pulse - min_pulse
    pulse_width = min_pulse + (angle / 180.0) * pulse_range
    
    # Convert pulse width to duty cycle percentage
    period_ms = 1000.0 / SERVO_FREQUENCY  # 20ms for 50Hz
    duty_cycle = (pulse_width / period_ms) * 100.0
    
    return duty_cycle


def move_servo(servo, angle, hold_position=True):
    """Move servo to specified angle"""
    duty = angle_to_duty_cycle(angle)
    servo.ChangeDutyCycle(duty)
    time.sleep(servo_config['move_time'])
    
    if not hold_position:
        servo.ChangeDutyCycle(0)  # Turn off signal


def activate_servo(servo, servo_name="Servo"):
    """Activate servo: move to active position, hold, return to rest"""
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Activating {servo_name}")
    
    # Move to active and HOLD position (keep signal on)
    move_servo(servo, servo_config['active_angle'], hold_position=True)
    time.sleep(servo_config['hold_time'])
    
    # Return to rest and turn off signal
    move_servo(servo, servo_config['rest_angle'], hold_position=False)
    
    print(f"{servo_name} operation complete")


def press_power():
    """Press the power button"""
    print("Pressing POWER button")
    activate_servo(servo1, "Power Button")
    send_ntfy_notification("☕ Power button pressed")


def press_brew():
    """Press the brew button"""
    print("Pressing BREW button")
    activate_servo(servo2, "Brew Button")
    send_ntfy_notification("☕ Brew button pressed")


def auto_brew():
    """Automated brew sequence: Power on, wait, then brew"""
    print(f"\n{'='*50}")
    print(f"AUTO BREW SEQUENCE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print('='*50)
    
    send_ntfy_notification("☕ Starting auto brew sequence...")
    
    # Press power button
    press_power()
    print("Waiting {auto_brew_config['power_on_delay']} seconds for coffee maker to power on...")
    time.sleep(auto_brew_config['power_on_delay'])
    
    # Press brew button
    press_brew()
    
    print("✓ Auto brew sequence complete!\n")
    send_ntfy_notification("✓ Auto brew sequence complete!")


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
        return jsonify({
            'error': 'Invalid button',
            'message': f'Button must be one of: {", ".join(valid_buttons)}'
        }), 400
    
    # Check rate limit (fast check before acquiring lock)
    allowed, remaining = check_rate_limit(button)
    if not allowed:
        return jsonify({
            'error': 'Rate limit exceeded',
            'message': f'Please wait {remaining:.1f} seconds before pressing {button} again',
            'retry_after': remaining
        }), 429  # HTTP 429 Too Many Requests
    
    # Try to acquire operation lock (non-blocking)
    if not servo_operation_lock.acquire(blocking=False):
        return jsonify({
            'error': 'Operation in progress',
            'message': 'Another servo operation is currently running. Please wait and try again.'
        }), 409  # HTTP 409 Conflict
    
    try:
        # Log the action with timestamp and source IP
        client_ip = request.remote_addr if request else 'unknown'
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"{timestamp} - Button '{button}' pressed from {client_ip}")
        
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
        print(f"ERROR during {button} operation: {e}")
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
    # Add a lock here
    with rate_limit_lock:  # Reuse existing lock or create a new one
        ntfy_topic = regenerate_topic()
        return jsonify({
            'success': True,
            'new_topic': ntfy_topic,
            'message': 'Topic regenerated successfully! Scan the new QR code to resubscribe.'
        })


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("Coffee Bot Web Interface - Servo Version")
    print("-" * 50)
    print(f"ntfy topic: {get_ntfy_topic()}")
    print("-" * 50)
    
    # Setup servos
    setup_servos()
    
    print("Starting web server on port 5000...")
    print("-" * 50)
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        GPIO.cleanup()