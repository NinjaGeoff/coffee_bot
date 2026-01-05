# Coffee Bot

A Raspberry Pi project to remotely "press" the physical buttons on a coffee maker using solenoids and a motor driver. Control your coffee maker via web interface and receive mobile notifications through ntfy. **None of this has been tested with actual solenoids/servos/something connected to GPIO yet, so use at your own risk.**

## Features
- **Web Interface** - Control your coffee maker from any device on your network
- **Mobile Notifications** - Get alerts via ntfy when buttons are pressed
- **Secure Topics** - Randomly generated ntfy topics for privacy
- **Topic Regeneration** - Change your notification topic anytime via web UI
- **Auto-Start** - Runs as a systemd service, starts on boot

## Hardware
- **Controller:** Raspberry Pi Zero W or Pi 3 B+ running Raspberry Pi OS Lite (32-bit or 64-bit)
- **Driver:** Waveshare Motor Driver HAT
- **Actuators:** ~~2x Mini Push-Pull Solenoids (DS-0420S)~~ These aren't strong enough to push the buttons on my Oxo 8 cup brewer. YMMV
- **Power:** 9V 2A DC Power Supply (PWM throttled via software)

<del>
## Pinout Mapping
The Waveshare Motor Driver HAT uses the following GPIO (BCM):

| Component | Function | GPIO Pin |
| :--- | :--- | :--- |
| **Solenoid A (Power)** | PWM (Speed) | 21 |
| **Solenoid A (Power)** | IN2 (Direction) | 20 |
| **Solenoid B (Brew)** | PWM (Speed) | 16 |
| **Solenoid B (Brew)** | IN2 (Direction) | 19 |
</del>

## Prepping your Raspberry Pi

This project uses **Raspberry Pi OS Lite** (32-bit or 64-bit) to keep the system lightweight. It runs headless, so no monitor, mouse, or keyboard will need to be hooked up. We'll use SSH to connect to and configure the Pi.

1. **Download Raspberry Pi Imager:** Get it from [raspberrypi.com/software](https://www.raspberrypi.com/software/). Once installed, run it.
2. **Select OS:** Choose `Raspberry Pi OS (Other)` -> `Raspberry Pi OS Lite (32-bit)` or `Raspberry Pi OS Lite (64-bit)`.
3. **Select Storage:** Choose your microSD card.
4. **Edit Settings (The Gear Icon):**
   - **Hostname:** Set to `coffee-bot` (or your choice).
   - **SSH:** Enable SSH and use password authentication.
   - **User:** Set a username (e.g., `pi`) and password.
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
   git clone https://github.com/NinjaGeoff/coffee_bot.git
   cd coffee_bot
   chmod +x setup.sh
   ./setup.sh
   ```
   - During setup it will ask you to confirm your timezone and will offer to adjust it if it's incorrect. Currently only has USA timezones programmed in.
   - The setup script will automatically configure port forwarding from port 80 to port 5000 without prompts using iptables-persistent.

2. **Access the web interface at:**  
   `http://coffee-bot/` or `http://<your-pi-ip>/`

## Using Mobile Notifications

Coffee Bot uses [ntfy.sh](https://ntfy.sh) for push notifications to your mobile device.

### Setup Mobile Notifications:
1. Install the ntfy app on your phone:
   - [iOS App Store](https://apps.apple.com/us/app/ntfy/id1625396347)
   - [Android Play Store](https://play.google.com/store/apps/details?id=io.heckel.ntfy)
   - [F-Droid](https://f-droid.org/en/packages/io.heckel.ntfy/)

2. Open the Coffee Bot web interface and scroll to the "Mobile Alerts" section

3. Scan the QR code to get the ntfy topic URL. Android phones should auto-add it to the ntfy app, not tested with iOS.

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
git pull origin main
sudo systemctl restart coffeebot.service
```

## Project Structure

```
coffee_bot/
├── coffee_web.py          # Main Flask application
├── setup.sh               # Automated setup script
├── templates/
│   └── index.html         # Web interface
├── static/                # Folder generates on first run of coffee_web.py
│   └── ntfy_qr.png        # Auto-generated QR code
├── ntfy_topic.txt         # Auto-generated topic file (do not commit)
└── README.md
```

## Safety Notes
- The solenoids are rated for 3V-5V. The software uses a PWM Duty Cycle of 33% to step down the 9V power supply to a safe level (~3V).
- Ensure proper wiring and insulation when working with the motor driver HAT.
- Always disconnect power when making hardware changes.

## Troubleshooting

**Web interface won't load:**
- Check service status: `sudo systemctl status coffeebot.service`
- Verify the Pi is on your network: `ping coffee-bot`
- Check for errors in logs: `sudo journalctl -u coffeebot.service -n 50`

**Notifications not working:**
- Verify you're subscribed to the correct topic in the ntfy app
- Check that the topic is displayed correctly on the web interface
- Test by pressing a button and checking the app

**Solenoids not activating:**
- Verify GPIO connections match the pinout table
- Check power supply is connected and providing 9V
- Ensure the motor driver HAT is properly seated on the Pi

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Future Plans
- Add scheduling/timer feature so it can automatically start brewing at the indicated time.
   - Ability to see current scheduled time
   - Ability to cancel current scheduled time
- Breakout different sections of the current web ui into tabs or a menu so it's not so cluttered
- The existing buttons in the web ui don't give you any feedback when pressed, would like to add some sort of click animation
- Add a physical button to activate the brewing process without having to move/remove the actual button pressing solenoids from the coffee maker. And because a large button with a resounding "kerchunk" noise would be fun
- Design an enclousure that will work with the planned hardware, even if it's just a project box with double sided tape and holes drilled in it
   - Custom 3d printed would be great, but I don't know how to do CAD designs and nor do I have a 3d printer
- Add a third solenoid as my coffee maker has two brew functions based on size of the brew
   - Short term will be to figure out a way to at least semi easily choose which button the brew solenoid presses