---
layout: default
title: Coffee Bot Documentation
---

# Coffee Bot Documentation

A Raspberry Pi project to remotely control a coffee maker using servo motors. Control your coffee maker via web interface and receive mobile notifications through ntfy.

## Quick Start

New to Coffee Bot? Follow these guides in order:

1. [**Parts List**](parts-list) - Order all required components
2. [**Pi Imaging Guide**](pi-imaging-guide) - Flash Raspberry Pi OS
3. [**Getting Started**](getting-started) - Complete setup walkthrough
4. [**Hardware Setup**](hardware-setup) - Assemble and wire components
5. [**Usage Guide**](usage-guide) - Learn the web interface
6. [**Configuration**](configuration) - Customize servo settings

## Features

- **Web Interface** - Control from any device on your network
- **Precise Servo Control** - PCA9685-based 16-channel driver
- **Mobile Notifications** - Push alerts via ntfy.sh
- **Secure Topics** - Randomly generated notification channels
- **Auto-Start Service** - Runs on boot via systemd
- **Rate Limiting** - Protection against button spam
- **Adjustable Settings** - Configurable servo angles and timing

## Hardware Requirements

- **Controller:** Raspberry Pi Zero 2 W (Raspberry Pi OS Lite 64-bit)
    - Initial development and testing were done on older Pi Zero W and Pi 3 B+, but I haven't tried the project on those devices in a while so they may or may not function.
- **Servo Driver:** Waveshare Servo Driver HAT (PCA9685-based, 16-channel I2C)
- **Actuators:** 2× MG90S Servo Motors (or similar)
- **Power:** 9V 2A DC Power Supply (with barrel jack adapter)
- **Storage:** MicroSD card (16GB+ recommended)

Full details and purchase links: [Parts List](parts-list)

## Installation

One-line installer (no Git required):

```bash
curl -sSL https://raw.githubusercontent.com/NinjaGeoff/coffee_bot/main/install.sh | bash
```

The installer handles everything:
- Downloads Coffee Bot files
- Configures timezone
- Enables I2C interface
- Installs dependencies
- Sets up auto-start service
- Verifies hardware detection

See [Getting Started](getting-started) for detailed setup instructions.

## Documentation

### Setup Guides

- [**Getting Started**](getting-started) - Complete setup from scratch
- [**Hardware Setup**](hardware-setup) - Assembly and wiring guide
- [**Pi Imaging Guide**](pi-imaging-guide) - Raspberry Pi OS installation
- [**Parts List**](parts-list) - Components and shopping links

### Usage & Configuration

- [**Usage Guide**](usage-guide) - Web interface and mobile notifications
- [**Configuration**](configuration) - Servo tuning and customization
- [**Troubleshooting**](troubleshooting-advanced) - Advanced debugging

### Reference

- [**Main README**](https://github.com/NinjaGeoff/coffee_bot) - Project overview
- [**Future Plans**](https://github.com/NinjaGeoff/coffee_bot/blob/main/future_plans.md) - Upcoming features
- [**License**](https://github.com/NinjaGeoff/coffee_bot/blob/main/LICENSE) - MIT License

## How It Works

Coffee Bot uses a Raspberry Pi to control servo motors that physically press buttons on your coffee maker:

1. **PCA9685 Servo Driver HAT** mounts on the Pi's GPIO header and communicates via I2C
2. **Two MG90S servos** connect to channels 0 and 1, positioned to press power and brew buttons
3. **Flask web server** runs on port 5000 (forwarded from port 80 for easy access)
4. **systemd service** ensures Coffee Bot starts automatically on boot
5. **ntfy.sh integration** sends push notifications to your phone when buttons are pressed

## Quick Reference

### Service Management

```bash
sudo systemctl status coffeebot.service    # Check status
sudo systemctl restart coffeebot.service   # Restart after changes
sudo journalctl -u coffeebot.service -f    # View live logs
```

### Hardware Verification

```bash
i2cdetect -y 1  # Should show '40' at address 0x40
```

### File Locations

- **Application:** `~/coffee_bot/coffee_web.py`
- **Configuration:** Edit servo settings in `coffee_web.py`
- **Logs:** `~/coffee_bot/coffee_bot.log`
- **ntfy Topic:** `~/coffee_bot/ntfy_topic.txt`
- **Service:** `/etc/systemd/system/coffeebot.service`

## Troubleshooting

### Quick Fixes

**Web interface won't load:**
```bash
sudo systemctl status coffeebot.service
ping coffee-bot
```

**Servos not moving:**
```bash
i2cdetect -y 1                    # Check I2C detection
sudo journalctl -u coffeebot.service -n 50  # Check logs
```

**Notifications not working:**
- Verify internet connectivity: `ping ntfy.sh`
- Check subscription in ntfy app
- Test manually: `curl -d "Test" https://ntfy.sh/$(cat ~/coffee_bot/ntfy_topic.txt)`

For detailed troubleshooting: [Advanced Troubleshooting Guide](troubleshooting-advanced)

## Community & Support

- [**GitHub Issues**](https://github.com/NinjaGeoff/coffee_bot/issues) - Report bugs or request features
- [**Star the Project**](https://github.com/NinjaGeoff/coffee_bot) - Show your support!
- [**Contribute**](https://github.com/NinjaGeoff/coffee_bot) - Submit pull requests

## Safety Notes

**Important Safety Information:**

- Always disconnect power before making hardware changes
- Use external power supply for servos (never Pi's 5V pins)
- Ensure power supply can handle 2A+ current draw
- Keep all electronics away from water and liquids
- MG90S servos can draw 500-700mA at peak load
- External 9V supply powers both servos and the Pi

## Project Showcase

Built your own Coffee Bot? We'd love to see it! Share photos and your experience in [GitHub Discussions](https://github.com/NinjaGeoff/coffee_bot/discussions) or tag your project.

**Potential modifications:**
- Different servo types or sizes
- 3D printed enclosures
- Multiple coffee makers
- Integration with smart home systems
- Custom web interface themes

See [Future Plans](https://github.com/NinjaGeoff/coffee_bot/blob/main/future_plans.md) for ideas and upcoming features.

## Credits

- **Waveshare Servo Driver HAT** - [Product Wiki](https://www.waveshare.com/wiki/Servo_Driver_HAT)
- **Adafruit ServoKit Library** - [GitHub](https://github.com/adafruit/Adafruit_CircuitPython_ServoKit)
- **ntfy.sh** - [Simple Pub-Sub Notifications](https://ntfy.sh)

## License

Coffee Bot is licensed under the MIT License - see [LICENSE](https://github.com/NinjaGeoff/coffee_bot/blob/main/LICENSE) for details.

Free to use, modify, and distribute. No warranty provided.

---

**Made by [NinjaGeoff](https://github.com/NinjaGeoff)**