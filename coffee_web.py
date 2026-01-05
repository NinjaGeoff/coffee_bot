import os
import secrets
import qrcode
import apprise
from flask import Flask, render_template, request, jsonify
# import RPi.GPIO as GPIO
from adafruit_pca9685 import PCA9685
import time
import threading
from board import SCL, SDA
import busio

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


# Setup I2C and PCA9685
i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c)
pca.frequency = 1600

# Power Setting: 0xFFFF is 100% (9V).
# 0x7FFF is ~50% (approx 4.5V), safer for your 3-5V solenoids.
SAFE_POWER = 0xFFFF

def fire_ma(duration):
    print(f"Firing Solenoid A (MA) for {duration}s...")
    pca.channels[0].duty_cycle = SAFE_POWER
    pca.channels[1].duty_cycle = 0x0000
    pca.channels[2].duty_cycle = 0xFFFF # Enable Pin
    time.sleep(duration)
    # Turn Off
    pca.channels[0].duty_cycle = 0x0000
    pca.channels[2].duty_cycle = 0x0000

def fire_mb(duration):
    print(f"Firing Solenoid B (MB) for {duration}s...")
    # MB uses channels 3, 4, and 5
    pca.channels[3].duty_cycle = SAFE_POWER
    pca.channels[4].duty_cycle = 0x0000
    pca.channels[5].duty_cycle = 0xFFFF # Enable Pin
    time.sleep(duration)
    # Turn Off
    pca.channels[3].duty_cycle = 0x0000
    pca.channels[5].duty_cycle = 0x0000

def auto_brew_sequence():
    """Power on, wait 5 seconds, then start brewing"""
    # Power button
    fire_ma(0.25)
    apobj.notify(
        title="☕ Coffee Bot",
        body="Auto-brew started: Power button pressed"
    )
    
    # Wait 5 seconds
    time.sleep(5)
    
    # Brew button
    fire_mb(0.25)
    apobj.notify(
        title="☕ Coffee Bot",
        body="Auto-brew: Brewing started! Coffee will be ready soon."
    )

@app.route('/')
def index():
    return render_template('index.html', ntfy_topic=NTFY_TOPIC)

@app.route('/press/<button_id>')
def press(button_id):
    if button_id == 'power':
        fire_ma(0.25)
        apobj.notify(
            title="☕ Coffee Bot",
            body="Power button pressed"
        )
    elif button_id == 'brew':
        fire_mb(0.25)
        apobj.notify(
            title="☕ Coffee Bot",
            body="Brew started! Coffee will be ready soon."
        )
    elif button_id == 'auto':
        # Run auto-brew in a separate thread so it doesn't block the response
        thread = threading.Thread(target=auto_brew_sequence)
        thread.daemon = True
        thread.start()
        return "Auto-brew sequence started!", 200
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
        # Ensure everything is off if script crashes
        pca.deinit()