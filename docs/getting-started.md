# Getting Started with Coffee Bot

This guide walks you through the complete setup process from ordering parts to brewing your first remote-controlled cup of coffee.

## Overview

The setup process takes about 1-2 hours and follows these steps:

1. Order hardware components
2. Flash Raspberry Pi OS to microSD card
3. Connect and configure your Pi
4. Install Coffee Bot software
5. Assemble hardware and mount servos
6. Configure and test

## Step 1: Order Parts

Review the [Parts List](parts-list) and order all required components. You'll need:

- Raspberry Pi Zero 2 W (with pre-soldered headers)
- Waveshare Servo Driver HAT
- 2× MG90S Servo Motors
- 9V 2A Power Supply with barrel jack adapter
- MicroSD card (16GB+ recommended)
- Micro USB cable for Pi power

**Budget:** Approximately $60-80 USD depending on availability and shipping.

**Delivery time:** 2-5 days for most parts if ordered from Amazon.

## Step 2: Prepare the Raspberry Pi

### 2.1 Flash the OS

Follow the [Pi Imaging Guide](pi-imaging-guide) to:

1. Download Raspberry Pi Imager
2. Flash Raspberry Pi OS Lite (64-bit) to your microSD card
3. Configure Wi-Fi, SSH, and hostname during imaging
4. Set timezone and localization

**Important settings:**
- **Hostname:** `coffee-bot` (or your choice)
- **Username:** `pi`
- **Enable SSH:** Yes (with public key or password)
- **Wi-Fi:** Your network name and password

### 2.2 First Boot

1. Insert microSD card into your Pi Zero 2 W
2. Connect micro USB power (5V 2.5A+)
3. Wait 2-3 minutes for first boot to complete
4. Verify network connection: `ping coffee-bot`

### 2.3 Initial SSH Connection

Connect to your Pi:

```bash
ssh pi@coffee-bot
```

Update the system:

```bash
sudo apt update && sudo apt upgrade -y
```

This may take 10-15 minutes on a Pi Zero 2 W.

## Step 3: Install Coffee Bot

Run the one-line installer:

```bash
curl -sSL https://raw.githubusercontent.com/NinjaGeoff/coffee_bot/main/install.sh | bash
```

The installer will:
- Download Coffee Bot files (no Git needed!)
- Prompt you to confirm/adjust your timezone
- Enable I2C interface
- Install Python dependencies
- Configure port forwarding (80 → 5000)
- Verify I2C hardware detection
- Set up systemd service for auto-start

**Installation time:** 5-10 minutes

### What the Installer Does

```
☕ Coffee Bot Installer
=======================
Downloading Coffee Bot...
Extracting files...
Running setup script...

Calling Timezone Setup Script
-----------------------------------------------
Attempting to auto-detect timezone via IP...
Detected Timezone: America/Phoenix
Use this timezone? (Y/n): y
Timezone set to America/Phoenix.

--- Enabling I2C Interface ---
I2C enabled

--- Installing System Dependencies ---
...

--- Setting up Python Virtual Environment ---
Virtual environment created.

--- Installing Python Libraries ---
...

--- Verifying I2C Configuration ---
I2C bus 1 detected. Running i2cdetect...
Expected: PCA9685 should appear at address 0x40

     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:                         -- -- -- -- -- -- -- -- 
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
40: 40 -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
...

If you see '40' in the grid above, your Servo Driver HAT is detected!

--- Starting Service ---
...

SETUP COMPLETE!
------------------------------------------------
Your Coffee Bot should be live at:
  http://coffee-bot/
  http://192.168.1.xxx/
```

### Post-Installation Verification

1. **Check service status:**
   ```bash
   sudo systemctl status coffeebot.service
   ```
   Should show "active (running)"

2. **Verify web interface:**
   Open `http://coffee-bot/` in your browser
   You should see the Coffee Bot control panel

3. **Check I2C detection:**
   ```bash
   i2cdetect -y 1
   ```
   Should show `40` at address 0x40

## Step 4: Hardware Assembly

Follow the [Hardware Setup Guide](hardware-setup) to:

1. **Mount the Servo Driver HAT** on your Pi's GPIO header
2. **Connect servos:**
   - Channel 0 (S0): Power button servo
   - Channel 1 (S1): Brew button servo
3. **Connect external power:**
   - 9V power supply to VIN/GND terminals on HAT
4. **Position servos** on your coffee maker
5. **Attach servo horns** to press buttons

**Assembly time:** 30-45 minutes

### Important Hardware Notes

- ⚠️ **Disconnect all power** before making hardware changes
- 🔌 **External power is required** - servos cannot run from Pi's 5V pins
- 📐 **Servo orientation matters** - position servos so they rotate toward buttons
- 🔧 **Test range before mounting** - verify servos can reach buttons

## Step 5: Configuration and Testing

### 5.1 Test Servo Movement

From the web interface at `http://coffee-bot/`:

1. Click **"Power Toggle"** button
   - Servo on channel 0 should move to 45° and back to 0°
2. Click **"Start Brewing"** button
   - Servo on channel 1 should move to 45° and back to 0°

### 5.2 Adjust Servo Positions

If servos don't press buttons correctly, see [Configuration Guide](configuration) to:
- Adjust servo angles
- Modify timing settings
- Fine-tune button press duration

### 5.3 Set Up Mobile Notifications

1. Install ntfy app on your phone:
   - [iOS](https://apps.apple.com/us/app/ntfy/id1625396347)
   - [Android](https://play.google.com/store/apps/details?id=io.heckel.ntfy)

2. In the Coffee Bot web interface, go to **Mobile Alerts** tab

3. Scan the QR code with your phone

4. Test notification: press any button and verify you receive a push notification

Full details in [Usage Guide](usage-guide).

### 5.4 Test Auto Brew Sequence

1. Ensure coffee maker is off and loaded with water and grounds
2. Click **"☕ Auto Brew"** button in the web interface
3. Observe the sequence:
   - Power button pressed (servo on channel 0)
   - 2-second delay
   - Brew button pressed (servo on channel 1)
   - Coffee starts brewing!

## Step 6: Final Setup

### Secure Your System

2. **Update regularly:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

### Optional Optimizations

1. **Fix SSH performance issues** (if experiencing slowness):
   See [Troubleshooting: Network Issues](troubleshooting-advanced#network-issues)

2. **Reduce log file size:**
   ```bash
   # Add log rotation (already configured by setup script)
   sudo cat /etc/logrotate.d/coffeebot
   ```

3. **Create a backup:**
   ```bash
   # Backup ntfy topic
   cp ~/coffee_bot/ntfy_topic.txt ~/ntfy_topic_backup.txt
   ```

## Common Setup Issues

### Can't Connect to Pi After Flashing

**Check:**
- Wi-Fi credentials are correct (SSID is case-sensitive)
- Your computer is on the same network
- Pi has had 2-3 minutes to boot
- Try accessing by IP address instead of hostname

**Solution:** Check router for Pi's IP address, then `ssh pi@<ip-address>`

### I2C Shows No Device at 0x40

**Check:**
- Servo Driver HAT is fully seated on GPIO pins
- External power supply is connected
- I2C is enabled: `sudo raspi-config` → Interface Options → I2C

**Solution:** Reseat HAT, reboot Pi, check connections

### Web Interface Won't Load

**Check:**
```bash
sudo systemctl status coffeebot.service
```

**Solution:** If failed, check logs:
```bash
sudo journalctl -u coffeebot.service -n 50
```

### Servos Not Moving

**Check:**
- External 9V power supply connected to VIN/GND
- Servo wires properly inserted in S0 and S1
- I2C detection shows `40`

**Solution:** See [Troubleshooting Guide](troubleshooting-advanced)

## Next Steps

Once everything is working:

1. **Customize servo settings** - See [Configuration Guide](configuration)
2. **Learn the web interface** - See [Usage Guide](usage-guide)
3. **Set up schedules** (coming soon) - See [Future Plans](../future_plans)
4. **Add more servos** - Third servo for brew size selection
5. **Design an enclosure** - 3D print a case for your hardware

## Getting Help

- Check the [Troubleshooting Guide](troubleshooting-advanced)
- [Open an issue on GitHub](https://github.com/NinjaGeoff/coffee_bot/issues)
- Search existing issues for solutions

## Success Checklist

Before considering setup complete, verify:

- Web interface loads at `http://coffee-bot/`
- Power button servo moves when clicked
- Brew button servo moves when clicked
- Auto brew sequence works end-to-end
- Mobile notifications arrive on your phone
- Service starts automatically after reboot
- Coffee maker actually brews coffee!

**Congratulations!** Your Coffee Bot is ready to use. Enjoy remote-controlled coffee brewing!