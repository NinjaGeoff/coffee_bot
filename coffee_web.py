import os
import qrcode
import apprise
from flask import Flask, render_template, request
import RPi.GPIO as GPIO
import time

# --- NTFY CONFIGURATION ---
# Replace with your unique topic name, up to 64 characters
NTFY_TOPIC = "coffee_bot_secure_6412e873"
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')
QR_PATH = os.path.join(STATIC_DIR, 'ntfy_qr.png')

# 1. Initialize Apprise
apobj = apprise.Apprise()
apobj.add(f'ntfy://{NTFY_TOPIC}')

# 2. Ensure static folder exists and generate QR once
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

if not os.path.exists(QR_PATH):
    print("Generating ntfy QR code...")
    data = f"ntfy://ntfy.sh/{NTFY_TOPIC}"
    img = qrcode.make(data)
    img.save(QR_PATH)

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
    return render_template('index.html')

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

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        pwm_a.stop()
        pwm_b.stop()
        GPIO.cleanup()