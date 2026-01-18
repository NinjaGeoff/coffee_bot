# Automatic Security Updates

## Overview

This guide sets up `unattended-upgrades` to automatically install security updates on your Raspberry Pi. The configuration is optimized for:

- **Security-only updates** - No feature upgrades, just patches
- **Minimal SD card wear** - One package at a time
- **Automatic cleanup** - Removes unused dependencies
- **Smart rebooting** - Reboots at 3 AM if kernel updates require it

There's always a chance that an update might break something, but the below guide SHOULD keep it to just security updates, so hopefully that chance is even less.

## Installation

### Step 1: Install unattended-upgrades

SSH into your Pi and install the package:

```bash
sudo apt update
sudo apt install unattended-upgrades
```

### Step 2: Enable Automatic Updates

Run the configuration wizard:

```bash
sudo dpkg-reconfigure unattended-upgrades
```

- Select **Yes** when prompted to enable automatic updates
- Press Enter to confirm

### Step 3: Create Optimized Configuration

Delete the default config file then create a new blank one:

```bash
# Delete original configuration
sudo rm /etc/apt/apt.conf.d/50unattended-upgrades

# Create new optimized configuration
sudo nano /etc/apt/apt.conf.d/50unattended-upgrades
```

Paste this into the config file:

```
// Optimized Config for Raspberry Pi Zero 2W - Security Only
Unattended-Upgrade::Origins-Pattern {
    // Standard Debian Security updates
    "origin=Debian,codename=${distro_codename},label=Debian-Security";
    "origin=Debian,codename=${distro_codename}-security,label=Debian-Security";
    // Critical Raspberry Pi Kernel & Firmware updates
    "origin=Raspberry Pi Foundation,codename=${distro_codename},label=Raspberry Pi Foundation";
};

// Do not upgrade these specific packages
Unattended-Upgrade::Package-Blacklist {
};

// Keep the Pi responsive by updating one package at a time
Unattended-Upgrade::MinimalSteps "true";

// Clean up unused dependencies to save SD card space
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Remove-New-Unused-Dependencies "true";

// Security best practice: Reboot at 3AM if a kernel update requires it
Unattended-Upgrade::Automatic-Reboot "true";
Unattended-Upgrade::Automatic-Reboot-Time "03:00";
Unattended-Upgrade::Automatic-Reboot-WithUsers "true";

// Ensure the process doesn't hang on minor errors
Unattended-Upgrade::AutoFixInterruptedDpkg "true";
```

Save and exit: `Ctrl+X`, then `Y`, then `Enter`

### Step 4: Verify Configuration

Test the configuration without actually installing updates:

```bash
sudo unattended-upgrade --dry-run --debug
```

You should see:
```
Initial blacklist:
Initial whitelist (not strict):
Starting unattended upgrades script
Allowed origins are: origin=Debian,codename=bookworm,label=Debian-Security
...
```

If you see errors, check your configuration syntax.