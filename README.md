# Coffee Bot

A Raspberry Pi Zero W project to remotely "press" the physical buttons on a coffee maker using solenoids and a motor driver.

### None of this has actually been tested yet, so I wouldn't try to use it, I don't really know what I'm doing. Seriously, follow this at your own risk, solenoids could potentially zap your pi or pi hat if not hooked up correctly.

## Hardware
- **Controller:** Raspberry Pi Zero W
- **Driver:** Waveshare Motor Driver HAT
- **Actuators:** 2x Mini Push-Pull Solenoids (DS-0420S)
- **Power:** 9V 2A DC Power Supply (PWM throttled via software)

## Pinout Mapping
The Waveshare Motor Driver HAT uses the following GPIO (BCM):

| Component | Function | GPIO Pin |
| :--- | :--- | :--- |
| **Solenoid A (Power)** | PWM (Speed) | 21 |
| **Solenoid A (Power)** | IN2 (Direction) | 20 |
| **Solenoid B (Brew)** | PWM (Speed) | 16 |
| **Solenoid B (Brew)** | IN2 (Direction) | 19 |

## Prepping your Raspberry Pi

This project uses **Raspberry Pi OS Lite (32-bit)** to keep the system lightweight. It runs headless, so no monitor, mouse, or keyboard will need to be hooked up. We'll use SSH to connect to and configure the Pi. These steps may work for other models of the Pi, but I'm working specifically with a Pi Zero W. The below steps are assuming you have a brand new Pi out of the oven and need to set it up from scratch.

1. **Download Raspberry Pi Imager:** Get it from [raspberrypi.com/software](https://www.raspberrypi.com/software/). Once installed, run it.
2. **Select OS:** Choose `Raspberry Pi OS (Other)` -> `Raspberry Pi OS Lite (32-bit)`.
3. **Select Storage:** Choose your microSD card.
4. **Edit Settings (The Gear Icon):**
   - **Hostname:** Set to `coffee-bot` (or your choice).
   - **SSH:** Enable SSH and use password authentication.
   - **User:** Set a username (e.g., `pi`) and password.
   - **Wi-Fi:** Enter your SSID and Password. Set the Wireless LAN country.
5. **Write:** Click "Write" and wait for it to finish.
6. **Boot:** Insert the card into the Pi Zero W and power it on. It will take 1-2 minutes to perform the first boot and connect to your network.

### Accessing the Pi and running updates
Once the Pi is on your network, open your terminal (VS Code or PowerShell) and run:  
`ssh pi@coffee-bot`

Once connected to the Pi via SSH, check for updates and install them:  
`sudo apt update && sudo apt upgrade -y`


## Getting Started
1. **Clone the repo to your Pi and run the setup script:**  
   ```
   git clone https://github.com/NinjaGeoff/coffee_bot.git
   cd coffee_bot
   chmod +x setup.sh
   ./setup.sh
   ```

4. **Access the controls at**  
    `http://<your-pi-ip>:5000`  

## Safety Note
The solenoids are rated for 3V-5V. The software uses a PWM Duty Cycle of 33% to step down the 9V power supply to a safe level (~3V).