from flask import Flask, render_template, request
import RPi.GPIO as GPIO
import time

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
    elif button_id == 'brew':
        push_solenoid(pwm_b)
    return f"Done: {button_id}", 200

if __name__ == '__main__':
    try:
        # Run on your local network
        app.run(host='0.0.0.0', port=5000)
    finally:
        GPIO.cleanup()