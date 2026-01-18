# Advanced Troubleshooting Guide

This guide covers advanced troubleshooting scenarios beyond the basic troubleshooting in the main README.

## Table of Contents

- [Service Won't Start After Reboot](#service-wont-start-after-reboot)
- [Intermittent Servo Issues](#intermittent-servo-issues)
- [I2C Communication Errors](#i2c-communication-errors)
- [Web Interface Performance](#web-interface-performance)
- [Network Issues](#network-issues)
- [Log Analysis](#log-analysis)
- [Recovery Procedures](#recovery-procedures)

---

## Service Won't Start After Reboot

### Symptoms
- Coffee Bot works fine, but after rebooting the Pi, the service fails to start
- `sudo systemctl status coffeebot.service` shows "failed" or "inactive"

### Causes
- I2C bus not ready when service starts
- Network not available when service starts
- Permission issues after system update

### Solution 1: Add Startup Delay

The setup script already includes a 5-second delay, but you may need more:

```bash
sudo nano /etc/systemd/system/coffeebot.service
```

Change:
```ini
ExecStartPre=/bin/sleep 5
```

To:
```ini
ExecStartPre=/bin/sleep 10
```

Then reload and restart:
```bash
sudo systemctl daemon-reload
sudo systemctl restart coffeebot.service
```

### Solution 2: Add Dependency on I2C

Ensure service waits for I2C:

```bash
sudo nano /etc/systemd/system/coffeebot.service
```

Add after `After=network.target`:
```ini
After=network.target multi-user.target
Requires=i2c-bcm2835.service
```

### Solution 3: Check Permissions

```bash
# Verify virtual environment ownership
ls -la ~/coffee_bot/env

# Fix if needed
sudo chown -R pi:pi ~/coffee_bot
```

---

## Intermittent Servo Issues

### Symptoms
- Servos work sometimes but not always
- Servos jitter or move erratically
- Servo position not consistent

### Cause 1: Power Supply Issues

**Check voltage:**
```bash
vcgencmd get_throttled
```

If output is not `0x0`, you have power issues.

**Solutions:**
- Use higher current power supply (3A+ instead of 2A)
- Add capacitors across servo power lines (100µF electrolytic)
- Check power cable quality (some cables have high resistance)

### Cause 2: Electrical Noise

Servos create electrical noise that can interfere with I2C.

**Solutions:**
1. **Add ferrite beads** to servo wires near HAT
2. **Shorten servo wires** if they're longer than 6 inches
3. **Separate power and signal wires** - don't bundle them together
4. **Add 0.1µF ceramic capacitors** across PCA9685 power pins

### Cause 3: Software Timing

If `move_time` is too short, servos may not reach position:

```bash
nano ~/coffee_bot/coffee_web.py
```

Increase move_time:
```python
servo_config = {
    'rest_angle': 0,
    'active_angle': 45,
    'move_time': 0.5,      # Increased from 0.3
    'hold_time': 0.3,      # Increased from 0.25
}
```

Restart service:
```bash
sudo systemctl restart coffeebot.service
```

---

## I2C Communication Errors

### Symptoms
- Servos worked initially but stopped
- Logs show I2C errors: "Remote I/O error"
- `i2cdetect -y 1` shows "UU" or no device

### Check I2C Health

```bash
# Check if I2C is enabled
ls /dev/i2c*

# Should show: /dev/i2c-1

# Scan for devices
i2cdetect -y 1

# Should show '40' at 0x40
```

### Common Fixes

**1. Reseat the HAT:**
```bash
# Shutdown first!
sudo shutdown -h now

# Wait for green LED to stop
# Unplug power
# Carefully remove and reseat HAT
# Power back on
```

**2. Check for conflicts:**
```bash
# List loaded I2C modules
lsmod | grep i2c

# Should see i2c_bcm2835 or similar
```

**3. Reduce I2C speed (if errors persist):**
```bash
sudo nano /boot/config.txt
```

Add at the end:
```
dtparam=i2c_arm=on,i2c_arm_baudrate=50000
```

Reboot:
```bash
sudo reboot
```

**4. Enable I2C explicitly:**
```bash
sudo raspi-config
# Select: Interface Options → I2C → Enable
sudo reboot
```

---

## Web Interface Performance

### Symptoms
- Web interface slow to load
- Button presses take long to respond
- Timeouts when pressing buttons

### Check System Resources

```bash
# Check CPU usage
top

# Check memory
free -h

# Check disk space
df -h
```

### Solutions

**1. Clear log file if it's huge:**
```bash
# Check log size
ls -lh ~/coffee_bot/coffee_bot.log

# If over 100MB, truncate it
> ~/coffee_bot/coffee_bot.log
```

**2. Reduce logging level:**
```bash
nano ~/coffee_bot/coffee_web.py
```

Change:
```python
logging.basicConfig(
    level=logging.WARNING,  # Changed from INFO
    ...
)
```

**3. Disable debug features:**
```bash
# Check if debug mode is on (it shouldn't be)
grep "debug=True" ~/coffee_bot/coffee_web.py

# Should show debug=False
```

**4. Check network latency:**
```bash
# From your computer
ping coffee-bot

# Should be under 10ms on local network
```

---

## Network Issues

### Can't Access Web Interface

**1. Verify service is running:**
```bash
sudo systemctl status coffeebot.service

# Should show "active (running)"
```

**2. Check if port is listening:**
```bash
sudo netstat -tlnp | grep 5000

# Should show Python listening on 0.0.0.0:5000
```

**3. Check firewall (usually not the issue):**
```bash
sudo iptables -L -n

# Check port forwarding rule exists
sudo iptables -t nat -L -n | grep 5000
```

**4. Test from Pi itself:**
```bash
curl http://localhost:5000

# Should return HTML
```

**5. Find Pi's IP address:**
```bash
hostname -I

# Try accessing via IP: http://192.168.1.xxx/
```

**6. SSH is VERY slow**

An odd bug/feature I found on the Pi Zero 2W, that I didn't see when doing the initial development on my Zero W or 3 B+, is pretty bad SSH performance that made SSH downright unusable at times. The easiest thing to check is that your Pi has a strong enough Wi-Fi signal. You can check the signal once you're SSH'd in (yeah, the irony isn't lost on me) with the command ```iwconfig wlan0 | grep Signal```
- -30 to -60 dBm is good and likely isn't the culprit
- -60 to -70 dBm = Fair (may cause sluggishness)
- -70 dBm or worse = Poor (most likely causing issues)

If your Wi-Fi signal is in that -30 to -60 dBm range, or if getting it into that range by moving your Pi to a better location, and you're still getting bad sluggishness, there are a few optimizations we can make by editing ```/etc/ssh/sshd_config```

```bash
# Disable DNS lookup in SSH (prevents timeout waiting for reverse DNS)
sudo sed -i '/^#\?UseDNS/c\UseDNS no' /etc/ssh/sshd_config

# Disable GSSAPI authentication (skips enterprise Kerberos authentication attempt)
sudo sed -i '/^#\?GSSAPIAuthentication/c\GSSAPIAuthentication no' /etc/ssh/sshd_config

# Disable GSSAPI credential cleanup (related to above)
sudo sed -i '/^#\?GSSAPICleanupCredentials/c\GSSAPICleanupCredentials no' /etc/ssh/sshd_config

# Restart SSH to apply changes
sudo systemctl restart ssh

# Restart the Pi for good measure
sudo reboot
```

**What these settings do:**
- **UseDNS no** - Disables reverse DNS lookups on SSH connections. The SSH daemon normally tries to look up the hostname of connecting clients, which can cause 5-30 second delays when the lookup times out (common on home networks).
- **GSSAPIAuthentication no** - Disables Kerberos/enterprise authentication attempts. This is only needed in corporate environments with Active Directory. Disabling it eliminates another authentication timeout.
- **GSSAPICleanupCredentials no** - Disables cleanup of GSSAPI credentials, which aren't being used anyway when GSSAPI is disabled.

These changes only affect SSH connection speed and should have no impact on security for home use. You should notice immediate improvement in terminal responsiveness after running these commands and restarting SSH.

**Note:** You should only need to run these commands once. The settings persist across reboots.

### NTFY Notifications Not Working

**1. Check internet connectivity:**
```bash
ping -c 3 ntfy.sh

# Should get responses
```

**2. Test notification manually:**
```bash
curl -d "Test from terminal" https://ntfy.sh/$(cat ~/coffee_bot/ntfy_topic.txt)
```

**3. Check logs for errors:**
```bash
grep "ntfy" ~/coffee_bot/coffee_bot.log
```

---

## Log Analysis

### View Recent Errors

```bash
# Last 50 lines of application log
tail -n 50 ~/coffee_bot/coffee_bot.log

# Search for errors
grep ERROR ~/coffee_bot/coffee_bot.log

# View systemd service logs
sudo journalctl -u coffeebot.service -n 100
```

### Common Error Messages

**"OSError: [Errno 121] Remote I/O error"**
- I2C communication failed
- Check HAT seating, I2C bus, power

**"ImportError: No module named 'adafruit_servokit'"**
- Virtual environment issue
- Reinstall: `~/coffee_bot/env/bin/pip install adafruit-circuitpython-servokit`

**"Address already in use"**
- Port 5000 is taken
- Check for duplicate service: `ps aux | grep coffee_web.py`
- Kill duplicate: `sudo pkill -f coffee_web.py`

**"Servo controller not detected"**
- Hardware not initialized
- Check I2C with `i2cdetect -y 1`

---

## Recovery Procedures

### Complete Reinstall

If all else fails:

```bash
# Backup ntfy topic
cp ~/coffee_bot/ntfy_topic.txt ~/ntfy_topic_backup.txt

# Remove old installation
cd ~
rm -rf coffee_bot

# Clone fresh
git clone https://github.com/NinjaGeoff/coffee_bot.git
cd coffee_bot

# Restore topic
cp ~/ntfy_topic_backup.txt ntfy_topic.txt

# Run setup
chmod +x setup.sh
./setup.sh
```

### Reset to Factory Defaults

```bash
cd ~/coffee_bot

# Stop service
sudo systemctl stop coffeebot.service

# Reset configuration (keeps code)
rm ntfy_topic.txt
rm -rf static/
rm coffee_bot.log

# Restart
sudo systemctl start coffeebot.service
```

### Nuclear Option: Fresh Pi OS Install

If the Pi itself seems corrupted:

1. Follow [Pi Imaging Guide](pi-imaging-guide) again
2. Fresh microSD card image
3. Run Coffee Bot setup from scratch

---

## Getting More Help

If you've tried everything:

1. **Check GitHub Issues:** [github.com/NinjaGeoff/coffee_bot/issues](https://github.com/NinjaGeoff/coffee_bot/issues)
2. **Collect diagnostic info:**
   ```bash
   # Create diagnostic report
   echo "=== System Info ===" > ~/diagnostic.txt
   uname -a >> ~/diagnostic.txt
   echo "=== I2C ===" >> ~/diagnostic.txt
   i2cdetect -y 1 >> ~/diagnostic.txt
   echo "=== Service Status ===" >> ~/diagnostic.txt
   systemctl status coffeebot.service >> ~/diagnostic.txt
   echo "=== Recent Logs ===" >> ~/diagnostic.txt
   tail -n 50 ~/coffee_bot/coffee_bot.log >> ~/diagnostic.txt
   
   cat ~/diagnostic.txt
   ```
3. **Post to GitHub with your diagnostic report**