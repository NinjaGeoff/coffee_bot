# Coffee Bot

A Raspberry Pi project to remotely control a coffee maker using servo motors. Control your coffee maker via web interface and receive mobile notifications through ntfy.

## Features

- **Web Interface** - Control from any device on your network
- **Precise Servo Control** - PCA9685-based 16-channel driver
- **Mobile Notifications** - Push alerts via ntfy.sh
- **Secure Topics** - Randomly generated notification channels
- **Auto-Start Service** - Runs on boot via systemd
- **Rate Limiting** - Protection against button spam
- **Adjustable Settings** - Configurable servo angles and timing

## Hardware Requirements

- **Controller:** Raspberry Pi Zero 2 W (Raspberry Pi OS Lite)
- **Servo Driver:** Waveshare Servo Driver HAT (PCA9685-based)
- **Actuators:** 2× MG90S Servo Motors
- **Power:** 9V 2A DC Power Supply

**[Complete Parts List & Shopping Guide](docs/parts-list)**

## Quick Start

### 1. Prepare Your Raspberry Pi

Flash Raspberry Pi OS Lite to a microSD card with Wi-Fi and SSH configured. Full walkthrough: **[Pi Imaging Guide](docs/pi-imaging-guide)**

### 2. One-Line Installation

SSH into your Pi and run:

```bash
curl -sSL https://raw.githubusercontent.com/NinjaGeoff/coffee_bot/main/install.sh | bash
```

> **Development branch:** Change `main` to `dev` in the URL above

The installer will:
- Download Coffee Bot zip file
- Enable I2C interface
- Install Python dependencies
- Configure port forwarding (80 → 5000)
- Set up systemd auto-start service
- Verify hardware detection

### 3. Connect Hardware

Follow the **[Hardware Setup & Wiring Guide](docs/hardware-setup)** to:
- Mount the Servo Driver HAT
- Connect servos to channels 0 and 1
- Wire external power supply
- Position servos on your coffee maker

### 4. Access the Web Interface

Navigate to `http://coffee-bot/` or `http://<your-pi-ip>/` in your browser.

## Documentation

**Complete documentation:** [https://ninjageoff.github.io/coffee_bot/](https://ninjageoff.github.io/coffee_bot/)

### Guides

- [**Getting Started**](docs/getting-started) - Detailed setup walkthrough
- [**Hardware Setup**](docs/hardware-setup) - Assembly and wiring
- [**Pi Imaging Guide**](docs/pi-imaging-guide) - OS installation
- [**Parts List**](docs/parts-list) - Shopping guide
- [**Usage Guide**](docs/usage-guide) - Web interface and notifications
- [**Configuration**](docs/configuration) - Servo tuning and customization
- [**Troubleshooting**](docs/troubleshooting-advanced) - Advanced debugging

### Quick Links

**Service Management:**
```bash
sudo systemctl status coffeebot.service    # Check status
sudo systemctl restart coffeebot.service   # Restart service
sudo journalctl -u coffeebot.service -f    # View logs
```

**Verify Hardware:**
```bash
i2cdetect -y 1  # Should show '40' at address 0x40
```

## Project Structure

```
coffee_bot/
├── coffee_web.py          # Main Flask application
├── install.sh             # One-line installer
├── setup.sh               # Setup script (called by installer)
├── set_timezone.sh        # Timezone configuration
├── templates/
│   └── index.html         # Web interface
├── static/
│   ├── style.css          # Web UI styles
│   └── ntfy_qr.png        # Generated QR code
├── docs/                  # Documentation (GitHub Pages)
├── ntfy_topic.txt         # Auto-generated (do not commit)
└── coffee_bot.log         # Application logs
```

## How It Works

1. **PCA9685 HAT** communicates with the Pi via I2C (address 0x40)
2. **Flask web server** runs on port 5000 (forwarded from port 80)
3. **Servo channels 0 and 1** control power and brew buttons
4. **External power supply** powers servos independently from Pi
5. **systemd service** ensures Coffee Bot starts on boot
6. **ntfy.sh** sends push notifications to your mobile device

## Contributing

Contributions are welcome! Please:

1. Check [Future Plans](future_plans.md) for planned features
2. Open an issue to discuss major changes
3. Submit pull requests to the `dev` branch

## Troubleshooting

**Can't access web interface?**
- Check service status: `sudo systemctl status coffeebot.service`
- Verify Pi is on network: `ping coffee-bot`

**Servos not moving?**
- Check I2C detection: `i2cdetect -y 1` (should show `40`)
- Verify external power supply is connected
- Check servo connections to S0 and S1 terminals

**More help:** See [Advanced Troubleshooting](docs/troubleshooting-advanced) or [open an issue](https://github.com/NinjaGeoff/coffee_bot/issues)

## Safety Notes

**Important:**
- Always disconnect power before modifying hardware
- Use external power supply for servos (not Pi's 5V pins)
- Ensure power supply can handle 2A+ current
- Keep electronics away from liquids

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## Credits

- [Waveshare Servo Driver HAT](https://www.waveshare.com/wiki/Servo_Driver_HAT)
- [Adafruit CircuitPython ServoKit](https://github.com/adafruit/Adafruit_CircuitPython_ServoKit)
- [ntfy.sh](https://ntfy.sh) - Simple pub-sub notifications

---

**Made by [NinjaGeoff](https://github.com/NinjaGeoff)**