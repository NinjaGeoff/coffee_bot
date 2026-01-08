# Coffee Bot

A Raspberry Pi project to remotely control a coffee maker using servo motors. Control your coffee maker via web interface and receive mobile notifications through ntfy.

## Features
- **Web Interface** - Control your coffee maker from any device on your network
- **Servo Control** - Precise angular control for pressing buttons
- **Mobile Notifications** - Get alerts via ntfy when buttons are pressed
- **Adjustable Settings** - Configure servo angles and timing via web UI
- **Secure Topics** - Randomly generated ntfy topics for privacy
- **Topic Regeneration** - Change your notification topic anytime via web UI
- **Auto-Start** - Runs as a systemd service, starts on boot

## Hardware
- **Controller:** Raspberry Pi Zero W or Pi 3 B+ running Raspberry Pi OS Lite (32-bit or 64-bit)
- **Power Hat:** Waveshare Motor Driver HAT (for power regulation via VIN)
- **Actuators:** 2x MG90S Servo Motors
- **Power:** 9V 2A DC Power Supply (connected to Motor Driver HAT VIN)

## Servo Connections

Servos are connected directly to Raspberry Pi GPIO pins (bypassing the motor driver for signal control):

**Servo 1 (Power Button):**
- Brown/Black (Ground) → Pi Pin 6 (Ground)
- Red (Power) → Pi Pin 2 (5V)
- Orange/Yellow (Signal) → Pi Pin 32 (GPIO 12)

**Servo 2 (Brew Button):**
- Brown/Black (Ground) → Pi Pin 9 (Ground) 
- Red (Power) → Pi Pin 4 (5V)
- Orange/Yellow (Signal) → Pi Pin 33 (GPIO 13)

**Power:**
- 9V 2A power supply connected to Waveshare Motor Driver HAT VIN terminal
- HAT provides regulated power to the Raspberry Pi
- Servos powered directly from Pi's 5V GPIO pins

## Pinout Mapping

| Component | Function | GPIO Pin | Physical Pin |
| :--- | :--- | :--- | :--- |
| **Servo 1 (Power)** | PWM Signal | GPIO 12 | Pin 32 |
| **Servo 2 (Brew)** | PWM Signal | GPIO 13 | Pin 33 |
| **Power (Servo 1)** | 5V | - | Pin 2 |
| **Ground (Servo 1)** | GND | - | Pin 6 |
| **Power (Servo 2)** | 5V | - | Pin 4 |
| **Ground (Servo 2)** | GND | - | Pin 9 |

## Prepping your Raspberry Pi

This project uses **Raspberry Pi OS Lite** (32-bit or 64-bit) to keep the system lightweight. It runs headless, so no monitor, mouse, or keyboard will need to be hooked up. We'll use SSH to connect to and configure the Pi.

1. **Download Raspberry Pi Imager:** Get it from [raspberrypi.com/software](https://www.raspberrypi.com/software/). Once installed, run it.
2. **Select OS:** Choose `Raspberry Pi OS (Other)` -> `Raspberry Pi OS Lite (32-bit)` or `Raspberry Pi OS Lite (64-bit)`.
3. **Select Storage:** Choose your microSD card.
4. **Edit Settings (The Gear Icon):**
   - **Hostname:** Set to `coffee-bot` (or your choice).
   - **SSH:** Enable SSH and use password authentication or public key.
   - **User:** Set a username (e.g., `pi`) and password if not using a public key.
   - **Wi-Fi:** Enter your SSID and Password. Set the Wireless LAN country.
5. **Write:** Click "Write" and wait for it to finish.
6. **Boot:** Insert the card into the Pi and power it on. It will take 1-2 minutes to perform the first boot and connect to your network.

### Accessing the Pi and running updates
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
   git clone --branch dev https://github.com/NinjaGeoff/coffee_bot.git
   cd coffee_bot
   chmod +x setup.sh
   ./setup.sh
   ```
   - During setup it will ask you to confirm your timezone and will offer to adjust it if it's incorrect. Currently only has USA timezones programmed in.
   - The setup script will automatically configure port forwarding from port 80 to port 5000 without prompts using iptables-persistent.

2. **Access the web interface at:**  
   `http://coffee-bot/` or `http://<your-pi-ip>/`

## Using the Web Interface

The web interface allows you to:

* **Auto Brew** - Automatically powers on the coffee maker, waits 5 seconds, then starts brewing
* **Manual Controls** - Press individual power and brew buttons
* **Servo Testing** - Test each servo individually to verify connections and adjust angles
* **Servo Configuration** - Adjust rest angle (default 0°), active angle (default 90°), and hold time (default 2 seconds)
* **Mobile Alerts** - Scan QR code to receive push notifications when buttons are pressed

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

## Updating the Code

If you've made changes to the code on GitHub and want to update your Pi:

```bash
cd ~/coffee_bot
git pull origin dev
sudo systemctl restart coffeebot.service
```

## Project Structure

```
coffee_bot/
├── coffee_web.py          # Main Flask application
├── setup.sh               # Automated setup script
├── templates/
│   └── index.html         # Web interface
├── static/                # Folder generates on first run
│   └── ntfy_qr.png        # Auto-generated QR code
├── ntfy_topic.txt         # Auto-generated topic file (do not commit)
├── servo_test.py          # Interactive servo testing script
└── README.md
```

## Servo Tuning Guide

The default servo settings are:
- **Rest Angle:** 0° (starting position)
- **Active Angle:** 90° (button press position)
- **Hold Time:** 2 seconds (how long to hold the button)

To adjust these:
1. Use the web interface "Servo Configuration" section
2. Or run `servo_test.py` for interactive testing
3. Adjust angles in 5-10 degree increments until you find the optimal position for your setup

## Safety Notes
- The MG90S servos are rated for 4.8-6V and are powered from the Pi's 5V pins
- The Motor Driver HAT is used only for power regulation (9V to 5V for the Pi)
- Each servo can draw up to 1A under load - if using both servos simultaneously under heavy load, consider an external 5V power supply
- Always disconnect power when making hardware changes

## Troubleshooting

**Web interface won't load:**
- Check service status: `sudo systemctl status coffeebot.service`
- Verify the Pi is on your network: `ping coffee-bot`
- Check for errors in logs: `sudo journalctl -u coffeebot.service -n 50`

**Notifications not working:**
- Verify you're subscribed to the correct topic in the ntfy app
- Check that the topic is displayed correctly on the web interface
- Test by pressing a button and checking the app

**Servos not moving:**
- Verify GPIO connections match the pinout table
- Check that PWM is enabled on your Raspberry Pi
- Test individual servos using the web interface "Test Servo" buttons
- Ensure 9V power supply is connected to the Motor Driver HAT VIN
- Run `servo_test.py` for interactive debugging

**Servos moving too much/too little:**
- Adjust the "Active Angle" setting in the web interface
- Try values between 10-180 degrees to find the optimal range
- Adjust "Hold Time" if buttons need to be pressed longer

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Future Plans
- Add scheduling/timer feature for automatic brewing at set times
- Add ability to see and cancel scheduled brew times
- Breakout different sections of the web UI into tabs or a menu
- Add a physical button for manual activation
- Design an enclosure for the hardware
- Add a third servo for different brew sizes (if coffee maker supports it)