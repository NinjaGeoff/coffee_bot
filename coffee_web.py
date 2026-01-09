#!/usr/bin/env python3
"""
Coffee Bot Web Interface - Servo Control Version
Flask web server for controlling coffee brewing with MG90S servos
"""

from flask import Flask, render_template, request, jsonify, url_for, send_from_directory
import RPi.GPIO as GPIO
import time
from datetime import datetime
import os
import secrets
import qrcode
from io import BytesIO

app = Flask(__name__)

# ============================================================================
# SERVO CONFIGURATION
# ============================================================================

# Servo GPIO Pins (connected directly to Pi GPIO)
SERVO_1_PIN = 12  # GPIO 12 (Pin 32) - Power button
SERVO_2_PIN = 13  # GPIO 13 (Pin 33) - Brew button

# Servo PWM Frequency
SERVO_FREQUENCY = 50  # Hz

# Servo Angle Settings (adjustable via web interface)
servo_config = {
    'rest_angle': 0,      # Starting/resting position (degrees)
    'active_angle': 45,   # Activated position (degrees)
    'hold_time': 0.25,     # Time to hold in active position (seconds)
}

# ============================================================================
# NTFY CONFIGURATION
# ============================================================================

NTFY_TOPIC_FILE = "ntfy_topic.txt"
STATIC_FOLDER = "static"
QR_CODE_PATH = os.path.join(STATIC_FOLDER, "ntfy_qr.png")

def get_or_create_topic():
    """Get existing topic or create a new one"""
    if os.path.exists(NTFY_TOPIC_FILE):
        with open(NTFY_TOPIC_FILE, 'r') as f:
            return f.read().strip()
    else:
        return regenerate_topic()

def regenerate_topic():
    """Generate a new random topic and save it"""
    new_topic = f"coffeebot-{secrets.token_urlsafe(16)}"
    with open(NTFY_TOPIC_FILE, 'w') as f:
        f.write(new_topic)
    generate_qr_code(new_topic)
    return new_topic

def generate_qr_code(topic):
    """Generate QR code for ntfy topic"""
    os.makedirs(STATIC_FOLDER, exist_ok=True)
    ntfy_url = f"https://ntfy.sh/{topic}"
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(ntfy_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(QR_CODE_PATH)

def send_ntfy_notification(message):
    """Send notification to ntfy topic"""
    try:
        import requests
        topic = get_or_create_topic()
        requests.post(
            f"https://ntfy.sh/{topic}",
            data=message.encode('utf-8'),
            headers={"Title": "Coffee Bot"}
        )
    except Exception as e:
        print(f"Failed to send notification: {e}")

# Initialize topic on startup
ntfy_topic = get_or_create_topic()

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
    
    servo1 = GPIO.PWM(SERVO_1_PIN, SERVO_FREQUENCY)
    servo2 = GPIO.PWM(SERVO_2_PIN, SERVO_FREQUENCY)
    
    servo1.start(0)
    servo2.start(0)
    
    # Initialize to rest position
    move_servo(servo1, servo_config['rest_angle'])
    move_servo(servo2, servo_config['rest_angle'])


def angle_to_duty_cycle(angle):
    """Convert angle (0-180) to duty cycle percentage"""
    duty_cycle = 2.5 + (angle / 180.0) * 10.0
    return duty_cycle


def move_servo(servo, angle):
    """Move servo to specified angle"""
    duty = angle_to_duty_cycle(angle)
    servo.ChangeDutyCycle(duty)
    time.sleep(0.5)
    servo.ChangeDutyCycle(0)


def activate_servo(servo, servo_name="Servo"):
    """Activate servo: move to active position, hold, return to rest"""
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Activating {servo_name}")
    
    move_servo(servo, servo_config['active_angle'])
    time.sleep(servo_config['hold_time'])
    move_servo(servo, servo_config['rest_angle'])
    
    print(f"{servo_name} operation complete")


def press_power():
    """Press the power button"""
    print("Pressing POWER button")
    activate_servo(servo1, "Power Button")
    send_ntfy_notification("â˜• Power button pressed")


def press_brew():
    """Press the brew button"""
    print("Pressing BREW button")
    activate_servo(servo2, "Brew Button")
    send_ntfy_notification("â˜• Brew button pressed")


def auto_brew():
    """Automated brew sequence: Power on, wait, then brew"""
    print(f"\n{'='*50}")
    print(f"AUTO BREW SEQUENCE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print('='*50)
    
    send_ntfy_notification("â˜• Starting auto brew sequence...")
    
    # Press power button
    press_power()
    print("Waiting 2 seconds for coffee maker to power on...")
    time.sleep(2)
    
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
    return render_template('index.html', ntfy_topic=ntfy_topic)


@app.route('/press/<button>')
def press_button(button):
    """Handle button presses"""
    if button == 'power':
        press_power()
        return "Power button pressed", 200
    elif button == 'brew':
        press_brew()
        return "Brew button pressed", 200
    elif button == 'auto':
        auto_brew()
        return "Auto brew sequence started", 200
    else:
        return "Invalid button", 400


@app.route('/regenerate_topic', methods=['POST'])
def regenerate_topic_route():
    """Generate a new ntfy topic"""
    global ntfy_topic
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
    print(f"ntfy topic: {ntfy_topic}")
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