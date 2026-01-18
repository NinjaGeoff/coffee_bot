# Coffee Bot

A Raspberry Pi project to remotely control a coffee maker using servo motors. Control your coffee maker via web interface and receive mobile notifications through ntfy.

## Features
- **Web Interface** - Control your coffee maker from any device on your network
- **Servo Control** - Precise angular control using PCA9685 servo driver
- **Mobile Notifications** - Get alerts via ntfy when buttons are pressed
- **Adjustable Settings** - Configure servo angles and timing
- **Secure Topics** - Randomly generated ntfy topics for privacy
- **Topic Regeneration** - Change your notification topic anytime via web UI
- **Auto-Start** - Runs as a systemd service, starts on boot
- **Rate Limiting** - Prevents accidental button spam and servo abuse

## Hardware
- **Controller:** Raspberry Pi Zero 2 W running Raspberry Pi OS Lite (32-bit or 64-bit)
- **Servo Driver:** Waveshare Servo Driver HAT (PCA9685-based, 16-channel I2C)
- **Actuators:** 2x MG90S Servo Motors (or similar)
- **Power:** 5-6V DC Power Supply (2A+ recommended, connected to servo terminals on HAT)

## Hardware Connections

### Waveshare Servo Driver HAT
The Waveshare Servo Driver HAT mounts directly onto the Raspberry Pi's 40-pin GPIO header and communicates via I2C.

**I2C Connection (Automatic via HAT):**
- SDA: GPIO 2 (Pin 3)
- SCL: GPIO 3 (Pin 5)
- Default I2C Address: 0x40

**Servo Connections (Connect to HAT terminals):**
- **Power Servo (Channel 0):**
  - Orange/Yellow wire → S0 (signal)
  - Red wire → V+ (via HAT power rail)
  - Brown/Black wire → GND (via HAT power rail)

- **Brew Servo (Channel 1):**
  - Orange/Yellow wire → S1 (signal)
  - Red wire → V+ (via HAT power rail)
  - Brown/Black wire → GND (via HAT power rail)

**External Power:**
- Connect 5-6V DC power supply to the servo power terminals on the HAT
- This powers the servos independently from the Raspberry Pi
- The Pi itself can be powered via USB or through the HAT's input terminals

### Servo Channel Assignment

| Servo Function | PCA9685 Channel | HAT Terminal |
| :--- | :--- | :--- |
| Power Button | 0 | S0 |
| Brew Button | 1 | S1 |

## Prepping your Raspberry Pi

This project uses **Raspberry Pi OS Lite** (32-bit or 64-bit) to keep the system lightweight. It runs headless, so no monitor, mouse, or keyboard will need to be hooked up. We'll use SSH to connect to and configure the Pi.

1. **Download Raspberry Pi Imager:** Get it from [raspberrypi.com/software](https://www.raspberrypi.com/software/). Once installed, run it.
2. **Select OS:** Choose `Raspberry Pi OS (Other)` → `Raspberry Pi OS Lite (32-bit)` or `Raspberry Pi OS Lite (64-bit)`.
3. **Select Storage:** Choose your microSD card.
4. **Edit Settings (The Gear Icon):**
   - **Hostname:** Set to `coffee-bot` (or your choice).
   - **SSH:** Enable SSH and use password authentication or public key.
   - **User:** Set a username (e.g., `pi`) and password if not using a public key.
   - **Wi-Fi:** Enter your SSID and Password. Set the Wireless LAN country.
5. **Write:** Click "Write" and wait for it to finish.
6. **Boot:** Insert the card into the Pi and power it on. It will take 1-2 minutes to perform the first boot and connect to your network.

### Accessing the Pi and Running Updates
Once the Pi is on your network, open your terminal and run:  
```bash
ssh pi@coffee-bot
```

Once connected to the Pi via SSH, check for updates and install them:  
```bash
sudo apt update && sudo apt upgrade -y
```

## Getting Started
1. **Clone the repo to your Pi and run the setup script:**  
   ```bash
   sudo apt install git -y
   git clone https://github.com/NinjaGeoff/coffee_bot.git #add "--branch dev" between clone the the URL to pull dev branch
   cd coffee_bot
   chmod +x setup.sh
   ./setup.sh
   ```
   - During setup it will ask you to confirm your timezone and will offer to adjust it if it's incorrect
   - The setup script will automatically:
     - Enable I2C interface
     - Install required libraries including adafruit-circuitpython-servokit
     - Configure port forwarding from port 80 to port 5000
     - Verify I2C connection and detect the PCA9685 chip
     - Set up the systemd service for auto-start

2. **Verify I2C Connection:**
   After setup, you can manually verify the PCA9685 is detected:
   ```bash
   i2cdetect -y 1
   ```
   You should see `40` in the grid, indicating the PCA9685 at address 0x40.

3. **Access the web interface at:**  
   `http://coffee-bot/` or `http://<your-pi-ip>/`

4. **In-depth Documentation:**
  - [Hardware Setup & Wiring](docs/hardware-setup.md)
  - [Raspberry Pi Imaging Guide](docs/pi-imaging-guide.md)
  - [Advanced Troubleshooting](docs/troubleshooting-advanced.md)
  - [Shopping List](docs/parts-list.md)

## Using the Web Interface

The web interface allows you to:

- **Auto Brew** - Automatically powers on the coffee maker, waits 2 seconds, then starts brewing
- **Manual Controls** - Press individual power and brew buttons
- **Mobile Alerts** - Scan QR code to receive push notifications when buttons are pressed
- **Regenerate Topic** - Create a new notification topic for privacy

## Using Mobile Notifications

Coffee Bot uses [ntfy.sh](https://ntfy.sh) for push notifications to your mobile device.

### Setup Mobile Notifications:
1. Install the ntfy app on your phone:
   - [iOS App Store](https://apps.apple.com/us/app/ntfy/id1625396347)
   - [Android Play Store](https://play.google.com/store/apps/details?id=io.heckel.ntfy)
   - [F-Droid](https://f-droid.org/en/packages/io.heckel.ntfy/)

2. Open the Coffee Bot web interface and scroll to the "Mobile Alerts" section

3. Scan the QR code to get the ntfy topic URL. Android phones should auto-add it to the ntfy app.

4. You'll now receive notifications when buttons are pressed!

### Regenerating Your Topic:
If you want to change your notification topic (for privacy or to revoke access):
1. Click the "Regenerate Topic" button in the web interface
2. Confirm the action
3. Scan the new QR code to resubscribe

**Note:** When you regenerate the topic, all previous subscribers will need to scan the new QR code.

## Managing the Service

Check service status:
```bash
sudo systemctl status coffeebot.service
```

View logs:
```bash
sudo journalctl -u coffeebot.service -f
```

Restart service (after making code changes):
```bash
sudo systemctl restart coffeebot.service
```

Stop service:
```bash
sudo systemctl stop coffeebot.service
```

## Project Structure

```
coffee_bot/
├── coffee_web.py          # Main Flask application
├── setup.sh               # Automated setup script
├── templates/
│   └── index.html         # Web interface
├── static/                # Generated on first run
│   └── ntfy_qr.png        # Auto-generated QR code
├── ntfy_topic.txt         # Auto-generated topic file (do not commit)
└── README.md
```

## Servo Tuning Guide

The default servo settings are:
- **Rest Angle:** 0° (starting position)
- **Active Angle:** 45° (button press position)
- **Move Time:** 0.3 seconds (time allowed for servo to complete movement)
- **Hold Time:** 0.25 seconds (how long to hold the button pressed)

**Total button press time = (move_time × 2) + hold_time = 0.85 seconds**

### Understanding PCA9685 Servo Control

Unlike direct GPIO PWM control, the PCA9685 chip handles all PWM signal generation. When you set an angle, the servo immediately begins moving to that position. The `move_time` setting gives the servo enough time to physically reach the target angle before the next command.

### Tuning Tips:
1. SSH into your Pi
2. Edit `coffee_web.py` and modify the `servo_config` dictionary values
3. Restart the service: `sudo systemctl restart coffeebot.service`

**Adjustment guidelines:**
- If servo doesn't reach full position, increase `move_time`
- If button press is too slow, decrease `move_time` and `hold_time`
- MG90S servos typically move 60° in ~0.1s, so moving 45° needs at least 0.075s
- The `active_angle` can range from 0° to 180° (adjust based on your mechanical setup)
- Start conservative and gradually increase speed as you verify reliability

## Safety Notes
- The PCA9685 servo driver operates at 3.3V logic level (I2C), compatible with Raspberry Pi
- Servos should be powered from external 5-6V supply, NOT from Pi's 5V pins
- MG90S servos draw ~100-300mA normally, up to 500-700mA at peak
- Always ensure external power supply can handle total servo current
- **Always disconnect power when making hardware changes**

## Troubleshooting

### Web interface won't load:
- Check service status: `sudo systemctl status coffeebot.service`
- Verify the Pi is on your network: `ping coffee-bot`
- Check for errors in logs: `sudo journalctl -u coffeebot.service -n 50`

### Notifications not working:
- Verify you're subscribed to the correct topic in the ntfy app
- Check that the topic is displayed correctly on the web interface
- Test by pressing a button and checking the app
- Verify internet connectivity on the Pi

### Servos not moving:
1. **Verify I2C connection:**
   ```bash
   i2cdetect -y 1
   ```
   Should show `40` in the grid

2. **Check external power:**
   - Ensure 5-6V supply is connected to servo terminals
   - Verify power supply can provide 2A+ current
   - Check voltage with multimeter if available

3. **Verify servo connections:**
   - Servos should be connected to S0 and S1 terminals on HAT
   - Check wire connections are secure
   - Verify servo polarity (signal, power, ground)

4. **Test in Python directly:**
   ```bash
   cd ~/coffee_bot
   source env/bin/activate
   python3
   ```
   Then in Python:
   ```python
   from adafruit_servokit import ServoKit
   kit = ServoKit(channels=16)
   kit.servo[0].angle = 45  # Should move servo on channel 0
   kit.servo[0].angle = 0   # Return to rest
   ```

### I2C not detected:
- Verify I2C is enabled: `sudo raspi-config` → Interface Options → I2C → Enable
- Reboot after enabling I2C: `sudo reboot`
- Check HAT is properly seated on GPIO pins
- Verify no I2C address conflicts with other devices

### Servos moving erratically:
- Check external power supply voltage (should be stable 5-6V)
- Verify power supply current rating is adequate (2A+ recommended)
- Ensure servo wires are not too long (keep under 6 inches if possible)
- Check for loose connections on servo terminals

### Rate limit errors:
- Default rate limit is 3 seconds between button presses
- This prevents accidental double-clicks and servo abuse
- Adjust `RATE_LIMIT_SECONDS` in `coffee_web.py` if needed

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits
- Waveshare Servo Driver HAT: [Product Wiki](https://www.waveshare.com/wiki/Servo_Driver_HAT)
- Adafruit ServoKit Library: [GitHub](https://github.com/adafruit/Adafruit_CircuitPython_ServoKit)

## Future Plans

### Scheduling Features
- **Add scheduling/timer feature for automatic brewing at set times**
  - Store scheduled times in a JSON file or database, run a background thread that checks every minute if it's time to trigger auto_brew()
- **Add ability to see and cancel scheduled brew times**
  - Add a `/schedules` route that displays upcoming brews in the web UI with delete buttons that remove entries from storage

~~
### Web Interface Improvements
- **Breakout different sections of the web UI into tabs or a menu**
  - Use CSS/JavaScript tabs or create separate routes (/controls, /notifications, /schedules) with a navigation menu in index.html
~~
- This is done with the current feature set, but I'm leaving this here so I don't forget to expand it when I eventually get to schedules

### Hardware Additions
- **Add a physical button for manual activation of brewer**
  - Connect a button to a GPIO pin, add event detection in coffee_web.py that calls auto_brew() when pressed
- **Add physical button(s) for safely rebooting and/or shutting down the pi**
  - Either two buttons (one for reboot and one for shutdown) or one button (short press for reboot, long press for shutdown)
  - Wire buttons to GPIO pins, detect presses and call `os.system('sudo reboot')` or `os.system('sudo shutdown -h now')` with proper permissions
- **Add physical switch to disconnect power**
  - Even when a Pi is shut down via SSH/terminal/script it will still draw power. I'd like to have a physical disconnect from the power eventually.
- **Design an enclosure for the hardware**
  - Model a 3D printable case in CAD software (Fusion 360, Tinkercad) that fits the Pi, HAT, servos, and mounting hardware
- **Add a third servo for different brew sizes**
  - For coffee makers that support it, such as the OXO 8 cup that has two brew buttons (one for single cup and one for carafe)
  - Connect third servo to channel 2, add brew size buttons to UI that activate different servos or servo combinations

### Advanced Features
- **Add support for RPi camera to monitor brewing status**
  - Install picamera2, capture images on button press or interval, serve via `/camera` route or embed in web UI
- **Update/expand timezone setting for more than just USA timezones**
  - ~~Create a separate `set_timezone.sh` script~~ with full timezone list from `timedatectl list-timezones`, call from setup.sh

## Changelog

### v2.0.0 (PCA9685 Version)
- Migrated from direct GPIO PWM to PCA9685 I2C servo driver
- Added proper I2C initialization and verification
- Updated all documentation for Waveshare Servo Driver HAT
- Improved error handling and servo control reliability