## Future Plans

### Documentation Updates
- Fix Project Structure as it's behind by a few major versions but I can't be bothered right now
- Determine better setup/install method so we don't HAVE to install Git on the Pi

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