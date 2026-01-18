---
layout: default
title: Coffee Bot Documentation
---

# Coffee Bot Documentation

A Raspberry Pi project to remotely control a coffee maker using servo motors. Control your coffee maker via web interface and receive mobile notifications through ntfy.

## Quick Links

- [Hardware Setup & Wiring Guide](hardware-setup) - Detailed hardware assembly instructions
- [Raspberry Pi Imaging Guide](pi-imaging-guide) - Step-by-step OS installation
- [Parts List & Shopping Guide](parts-list) - Everything you need to buy
- [Advanced Troubleshooting](troubleshooting-advanced) - Solutions for common issues

## Getting Started

If you're new to Raspberry Pi or hardware projects, we recommend following the guides in this order:

1. **[Parts List](parts-list)** - Order all necessary components
2. **[Raspberry Pi Imaging Guide](pi-imaging-guide)** - Set up your microSD card
3. **[Hardware Setup](hardware-setup)** - Assemble the hardware
4. **[Main README](https://github.com/NinjaGeoff/coffee_bot)** - Run the setup script and start brewing!

## Features

- **Web Interface** - Control your coffee maker from any device on your network
- **Servo Control** - Precise angular control using PCA9685 servo driver
- **Mobile Notifications** - Get alerts via ntfy when buttons are pressed
- **Adjustable Settings** - Configure servo angles and timing
- **Secure Topics** - Randomly generated ntfy topics for privacy
- **Auto-Start** - Runs as a systemd service, starts on boot
- **Rate Limiting** - Prevents accidental button spam and servo abuse

## Hardware Requirements

- **Controller:** Raspberry Pi Zero 2 W
- **Servo Driver:** Waveshare Servo Driver HAT (PCA9685-based)
- **Actuators:** 2x MG90S Servo Motors
- **Power:** 5-6V DC Power Supply (2A+ recommended)

## Need Help?

If you encounter issues, check the [Advanced Troubleshooting](troubleshooting-advanced) guide or [open an issue on GitHub](https://github.com/NinjaGeoff/coffee_bot/issues).

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/NinjaGeoff/coffee_bot/blob/main/LICENSE) file for details.