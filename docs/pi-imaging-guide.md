# Raspberry Pi Imaging Guide

This guide walks you through installing Raspberry Pi OS Lite on your microSD card for headless (no monitor) operation.

## What You'll Need

- **Raspberry Pi Zero 2 W** (with pre-soldered headers recommended)
- **MicroSD card** - 8GB minimum, 16GB+ recommended, Class 10 or better
- **MicroSD card reader** for your computer
- **Computer** (Windows, Mac, or Linux)
- **Wi-Fi network** name and password

## Step 1: Download Raspberry Pi Imager

1. Go to [raspberrypi.com/software](https://www.raspberrypi.com/software/)
2. Download the version for your operating system:
   - **Windows:** Raspberry Pi Imager for Windows
   - **macOS:** Raspberry Pi Imager for macOS
   - **Linux:** Available via package manager or download
3. Install and launch the application

## Step 2: Select the Operating System

1. Device selection
1. Click **"Choose OS"**
2. Navigate to: **Raspberry Pi OS (other)**
3. Select: **Raspberry Pi OS Lite (64-bit)**
    - If you're using a pi that doesn't support 64-bit you'll only see 32-bit. I've not tested 32-bit for functionality with this project.

## Step 3: Select Your microSD Card

1. Insert your microSD card into your computer's card reader
2. Click **"Choose Storage"** in Raspberry Pi Imager
3. Select your microSD card from the list
    - **WARNING:** This will erase everything on the card! Make sure you select the correct device.

## Step 4: Configure Customizations

### Hostname
- Enter: `coffee-bot` (or your preferred name)
- This is how you'll access your Pi: `http://coffee-bot/`

### Localization
- Select your timezone from the list. You'll also have the opportunity to set this during coffee-bot setup

### User
- Username: `pi` (or your choice)
- Password: Choose a secure password or leave blank if you're using SSH key auth

### Wi-Fi
- **SSID:** Your Wi-Fi network name (case-sensitive!)
- **Password:** Your Wi-Fi password
- If your network doesn't have a password select the "Open Network" button above the SSID field

### Remote Access
1. Enable SSH
2. Use public key authentication so you don't need to use a password
   - This requires you already have a public key set up on your computer. Review [the official Raspberry Pi setup documentation for more information](https://www.raspberrypi.com/documentation/computers/remote-access.html#configure-ssh-without-a-password).

### Raspberry Pi Connect
- Leave it disabled

## Step 5: Write the Image

1. Review the Summary
2. Click **"Write"** in the main window
3. Confirm the warning about erasing data
4. Wait for the process to complete (about 5-15 minutes depending on card speed)

## Step 6: First Boot

1. **Remove the microSD card** from your computer
2. **Insert it into your Raspberry Pi Zero 2W**
   - The card slot is on the underside
   - Push gently until it clicks
3. **Connect power** via micro USB (use a 5V 2.5A+ adapter)
4. **Wait a few minutes for first boot**
   - The first boot takes longer (expanding filesystem)
   - The green LED will blink during boot
   - When it stops blinking, boot is complete

## Step 7: Verify Network Connection

From your computer, verify the Pi is on your network:

### On Windows:
```cmd
ping coffee-bot
```

### On macOS/Linux:
```bash
ping coffee-bot.local
```

You should see responses like:
```
Reply from 192.168.1.xxx: bytes=32 time=5ms TTL=64
```

**Not responding?**
- Wait another minute or two
- Check your Wi-Fi credentials in Imager settings
- Make sure your computer is on the same Wi-Fi network
- Try rebooting the Pi (unplug and replug power)

## Step 8: First SSH Connection

Connect to your Pi using SSH:

### On Windows:
1. Open your terminal tool of choice, ie PowerShell or Terminal
2. Type: `ssh pi@coffee-bot`
   - You'll be prompted to add the key the first time you connect with SSH, type in yes and hit enter
   - If you setup SSH with public key authentication you won't need a password

### Successful Connection
You should see:
```
Linux coffee-bot 6.1.21-v8+ #1642 SMP PREEMPT Mon Apr  3 17:24:16 BST 2023 aarch64
...
pi@coffee-bot:~ $
```

## Step 9: Update System

Before installing Coffee Bot, update your system:

```bash
sudo apt update && sudo apt upgrade -y
```

This may take 5-15 minutes depending on how many updates are available.

## Step 10: Install Coffee Bot

Now you're ready to install Coffee Bot! Return to the main page at [http://coffee-bot/](http://coffee-bot/) for installation instructions.

## Troubleshooting

### Can't find the Pi on network

**Try finding by IP address:**
1. Log into your router's admin page
2. Look for connected devices
3. Find device named "coffee-bot" or "raspberrypi"
4. Note the IP address (e.g., 192.168.1.150)
5. Try: `ssh pi@192.168.1.150`

**Check Wi-Fi settings:**
- SSID is case-sensitive
- Password is correct
- Country code is set correctly
- Your Wi-Fi broadcasts on 2.4GHz (Pi Zeros don't support 5GHz)

### Wrong password when SSHing

- Double-check the password you set in Raspberry Pi Imager
- Re-flash the card with correct credentials, or set up and use a public key
- Default credentials (`pi`/`raspberry`) don't work anymore on new images

### SSH connection refused

- SSH might not be enabled - re-flash and make sure SSH is enabled in customizations
- Check if Pi has IP address by checking router
- Try rebooting the Pi

### Card won't boot

- Try a different microSD card (some cards have compatibility issues)
- Re-flash the card
- Make sure you selected the right OS image (Lite version)
- Check power supply is 5V 2A+ (weak power causes boot issues)

### Green LED pattern meanings

- **Solid on:** Pi is getting power but not booting (card issue)
- **Blinking regularly:** Normal boot/activity
- **Off:** No power or serious hardware issue