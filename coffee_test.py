import RPi.GPIO as GPIO
import time

# Waveshare Motor Driver HAT Pin Definitions
# Motor A (Solenoid 1 - Power)
MA_PWM = 21  # PWM Pin
MA_IN2 = 20  # Direction Pin

# Motor B (Solenoid 2 - Brew)
MB_PWM = 16  # PWM Pin
MB_IN2 = 19  # Direction Pin

# Constants
PWM_FREQ = 1000  # 1kHz frequency
DUTY_CYCLE = 33  # Start at 33% (approx 3V)

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # Setup pins
    GPIO.setup([MA_PWM, MA_IN2, MB_PWM, MB_IN2], GPIO.OUT)
    
    # Initialize PWM on the speed pins
    global pwm_a, pwm_b
    pwm_a = GPIO.PWM(MA_PWM, PWM_FREQ)
    pwm_b = GPIO.PWM(MB_PWM, PWM_FREQ)
    
    # Start with 0 duty cycle (off)
    pwm_a.start(0)
    pwm_b.start(0)
    
    # Set direction pins to LOW
    GPIO.output(MA_IN2, GPIO.LOW)
    GPIO.output(MB_IN2, GPIO.LOW)

def push_power():
    print("Pressing Power Button (PWM)...")
    pwm_a.ChangeDutyCycle(DUTY_CYCLE)
    time.sleep(0.4) 
    pwm_a.ChangeDutyCycle(0)
    print("Released.")

def push_brew():
    print("Pressing Brew Button (PWM)...")
    pwm_b.ChangeDutyCycle(DUTY_CYCLE)
    time.sleep(0.4)
    pwm_b.ChangeDutyCycle(0)
    print("Released.")

if __name__ == "__main__":
    try:
        setup()
        print("System Ready.")
        while True:
            cmd = input("Enter 'p' (Power), 'b' (Brew), or 'q' (Quit): ").lower()
            if cmd == 'p':
                push_power()
            elif cmd == 'b':
                push_brew()
            elif cmd == 'q':
                break
    finally:
        pwm_a.stop()
        pwm_b.stop()
        GPIO.cleanup()
        print("GPIO Cleaned up.")