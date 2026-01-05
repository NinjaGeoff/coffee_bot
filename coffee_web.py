import os
import secrets
import qrcode
import apprise
from flask import Flask, render_template, request, jsonify
import RPi.GPIO as GPIO
import time

# --- NTFY CONFIGURATION ---
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')
QR_PATH = os.path.join(STATIC_DIR, 'ntfy_qr.png')
TOPIC_FILE = os.path.join(os.path.dirname(__file__), 'ntfy_topic.txt')

def generate_random_topic():
    """Generate a random ntfy topic with max length of 64 characters"""
    prefix = "coffee_bot_"
    # 64 total chars - len("coffee_bot_") = 53 chars for random string
    random_length = 64 - len(prefix)
    random_string = secrets.token_urlsafe(random_length)[:random_length]
    # Replace URL-unsafe chars that token_urlsafe might produce with safe ones
    random_string = random_string.replace('-', '').replace('_', '')[:random_length]
    return prefix + random_string

def get_or_create_topic():
    """Get existing topic or create a new one"""
    if os.path.exists(TOPIC_FILE):
        with open(TOPIC_FILE, 'r') as f:
            topic = f.read().strip()
            if topic:
                print(f"Using existing ntfy topic: {topic}")
                return topic
    
    # Generate new topic
    topic = generate_random_topic()
    with open(TOPIC_FILE, 'w') as f:
        f.write(topic)
    print(f"Generated new ntfy topic: {topic}")
    return topic

def regenerate_qr(topic):
    """Generate QR code for the given topic"""
    data = f"ntfy://ntfy.sh/{topic}"
    img = qrcode.make(data)
    img.save(QR_PATH)
    print(f"QR code regenerated for topic: {topic}")

# Get or create the ntfy topic
NTFY_TOPIC = get_or_create_topic()

# 1. Initialize Apprise
apobj = apprise.Apprise()
apobj.add(f'ntfy://{NTFY_TOPIC}')

# 2. Ensure static folder exists and generate QR once
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

if not os.path.exists(QR_PATH):
    regenerate_qr(NTFY_TOPIC)

app = Flask(__name__)

# Hardware Setup (Using your safe 33% Duty Cycle)
MA_PWM, MA_IN2 = 21, 20
MB_PWM, MB_IN2 = 16, 19
DUTY_CYCLE = 33 

GPIO.setmode(GPIO.BCM)
GPIO.setup([MA_PWM, MA_IN2, MB_PWM, MB_IN2], GPIO.OUT)
GPIO.output([MA_IN2, MB_IN2], GPIO.LOW)

pwm_a = GPIO.PWM(MA_PWM, 1000)
pwm_b = GPIO.PWM(MB_PWM, 1000)
pwm_a.start(0)
pwm_b.start(0)

def push_solenoid(pwm_obj):
    pwm_obj.ChangeDutyCycle(DUTY_CYCLE)
    time.sleep(0.4)
    pwm_obj.ChangeDutyCycle(0)

@app.route('/')
def index():
    return render_template('index.html', ntfy_topic=NTFY_TOPIC)

@app.route('/press/<button_id>')
def press(button_id):
    if button_id == 'power':
        push_solenoid(pwm_a)
        apobj.notify(
            title="☕ Coffee Bot",
            body="Power button pressed"
        )
    elif button_id == 'brew':
        push_solenoid(pwm_b)
        apobj.notify(
            title="☕ Coffee Bot",
            body="Brew started! Coffee will be ready soon."
        )
    return f"Done: {button_id}", 200

@app.route('/regenerate_topic', methods=['POST'])
def regenerate_topic():
    global NTFY_TOPIC, apobj
    
    # Generate new topic
    new_topic = generate_random_topic()
    
    # Save to file
    with open(TOPIC_FILE, 'w') as f:
        f.write(new_topic)
    
    # Update global variable
    NTFY_TOPIC = new_topic
    
    # Regenerate QR code
    regenerate_qr(new_topic)
    
    # Reinitialize Apprise with new topic
    apobj = apprise.Apprise()
    apobj.add(f'ntfy://{new_topic}')
    
    print(f"Topic regenerated: {new_topic}")
    
    return jsonify({
        'success': True,
        'new_topic': new_topic,
        'message': 'Topic regenerated successfully! Scan the new QR code to subscribe.'
    })

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        pwm_a.stop()
        pwm_b.stop()
        GPIO.cleanup()