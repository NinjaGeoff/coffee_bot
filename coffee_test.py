import time
import busio
from board import SCL, SDA
from adafruit_pca9685 import PCA9685

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

try:
    # 1. Fire MA for 1 second
    fire_ma(0.25)

    # 2. Wait 5 seconds
    print("Waiting 2 seconds...")
    time.sleep(2)

    # 3. Fire MB for 1 second (standardizing to 1s for the test)
    fire_mb(0.25)

    print("Sequence Complete.")

finally:
    # Ensure everything is off if script crashes
    pca.deinit()