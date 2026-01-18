# Usage Guide

Learn how to use Coffee Bot's web interface, mobile notifications, and service management features.

## Accessing Coffee Bot

Coffee Bot's web interface is accessible from any device on your local network:

- **By hostname:** `http://coffee-bot/`
- **By IP address:** `http://192.168.1.xxx/` (find IP with `hostname -I` on the Pi)

## Web Interface Overview

The Coffee Bot interface has three tabs:

1. **🎛️ Controls** - Operate your coffee maker
2. **📱 Mobile Alerts** - Configure push notifications
3. **📚 Documentation** - Links to guides and resources

## Using the Controls Tab

### Auto Brew Button

The **☕ Auto Brew** button executes a complete brewing sequence:

1. Presses the power button (channel 0)
2. Waits 2 seconds for coffee maker to power on
3. Presses the brew button (channel 1)
4. Your coffee starts brewing!

**When to use:** This is the main button for daily use. One click starts the entire brewing process.

**Notification:** You'll receive a single notification: "☕ Coffee maker powered on and brew started!"

### Manual Control Buttons

**⚡ Power Toggle**
- Presses the power button servo (channel 0)
- Use to turn coffee maker on or off manually
- Notification: "☕ Power button pressed"

**☕ Start Brewing**
- Presses the brew button servo (channel 1)
- Use when coffee maker is already powered on
- Notification: "☕ Brew button pressed"

**When to use manual controls:**
- Testing servo positions during setup
- Turning off coffee maker without brewing
- Situations where auto-brew sequence doesn't fit your coffee maker

### Button Feedback

After pressing any button, you'll see a message:
- ✅ **Green message:** Operation successful
- ❌ **Red message:** Error or rate limit hit

### Rate Limiting

To protect servo hardware, buttons have a 3-second cooldown:
- If you click too quickly, you'll see: "⏱️ Please wait X seconds"
- This prevents accidental double-clicks and servo abuse
- Configurable in `coffee_web.py` (see [Configuration Guide](configuration))

### Operation Locking

Only one servo operation can run at a time:
- If you click while another operation is running: "⚙️ Another operation is running"
- This prevents servo conflicts and ensures proper sequencing

## Mobile Notifications

Coffee Bot uses [ntfy.sh](https://ntfy.sh) for push notifications - a free, open-source notification service.

### Setting Up Notifications

1. **Install the ntfy app:**
   - [iOS App Store](https://apps.apple.com/us/app/ntfy/id1625396347)
   - [Android Play Store](https://play.google.com/store/apps/details?id=io.heckel.ntfy)
   - [F-Droid](https://f-droid.org/en/packages/io.heckel.ntfy/)

2. **Subscribe to your Coffee Bot:**
   - Open Coffee Bot web interface
   - Click the **📱 Mobile Alerts** tab
   - Scan the QR code with your phone
   - Android: Automatically subscribes
   - iOS: Open the ntfy app and paste the URL

3. **Test notifications:**
   - Press any button in the Controls tab
   - You should receive a push notification within a few moments

### Understanding Notifications

- **Auto Brew:** "☕ Coffee maker powered on and brew started!"
- **Power Button:** "☕ Power button pressed"
- **Brew Button:** "☕ Brew button pressed"

Notifications include:
- Coffee emoji ☕ for easy identification
- Timestamp
- Clickable to view in ntfy app

### Managing Notification Privacy

Your ntfy topic is randomly generated and unique to your Coffee Bot installation. The topic format is: `coffeebot-XXXXXXXXXXXXXXXX`

**To change your topic:**

1. Click **🔄 Regenerate Topic** in the Mobile Alerts tab
2. Confirm the action
3. Scan the new QR code to resubscribe
4. **Important:** All previous subscribers will need the new QR code

**When to regenerate:**
- Someone you don't want to have access has the QR code
- You want to revoke all subscriptions and start fresh
- Periodic security practice

**Topic security:**
- Keep your QR code private
- Only share with trusted users
- Topics are unguessable (cryptographically random)
- Anyone with your topic can see notifications

### Troubleshooting Notifications

**Not receiving notifications?**

1. **Check internet connectivity on Pi:**
   ```bash
   ping ntfy.sh
   ```

2. **Verify subscription in ntfy app:**
   - Open ntfy app
   - Check that your Coffee Bot topic is listed
   - Try unsubscribing and rescanning QR code

3. **Test manually:**
   ```bash
   ssh pi@coffee-bot
   curl -d "Test notification" https://ntfy.sh/$(cat ~/coffee_bot/ntfy_topic.txt)
   ```
   You should receive a "Test notification" on your phone

4. **Check logs for errors:**
   ```bash
   ssh pi@coffee-bot
   grep "ntfy" ~/coffee_bot/coffee_bot.log
   ```

## Service Management

Coffee Bot runs as a systemd service that starts automatically on boot.

### Check Service Status

```bash
sudo systemctl status coffeebot.service
```

You should see:
```
● coffeebot.service - Coffee Bot Flask Web Server
     Loaded: loaded (/etc/systemd/system/coffeebot.service; enabled)
     Active: active (running) since [date/time]
```

### View Live Logs

```bash
sudo journalctl -u coffeebot.service -f
```

Press `Ctrl+C` to stop viewing logs.

### Restart Service

After making configuration changes:

```bash
sudo systemctl restart coffeebot.service
```

Wait 10-15 seconds, then verify:
```bash
sudo systemctl status coffeebot.service
```

### Stop Service

```bash
sudo systemctl stop coffeebot.service
```

To start again:
```bash
sudo systemctl start coffeebot.service
```

### Disable Auto-Start

If you want to prevent Coffee Bot from starting on boot:

```bash
sudo systemctl disable coffeebot.service
```

To re-enable:
```bash
sudo systemctl enable coffeebot.service
```

### View Application Logs

The application also logs to a file:

```bash
tail -f ~/coffee_bot/coffee_bot.log
```

**Log rotation:** Logs are automatically rotated daily and kept for 7 days (configured during setup).

### Common Log Messages

**Normal operation:**
```
2026-01-18 10:30:15 - INFO - Button 'auto' pressed from 192.168.1.100
2026-01-18 10:30:15 - INFO - AUTO BREW SEQUENCE STARTED
2026-01-18 10:30:15 - INFO - Activating Power Button
2026-01-18 10:30:16 - INFO - Power Button operation complete
```

**Rate limit hit:**
```
2026-01-18 10:30:20 - DEBUG - Rate limit hit for power: 1.5s remaining
```

**Hardware error:**
```
2026-01-18 10:30:25 - ERROR - ERROR during power operation: Remote I/O error
```

See [Troubleshooting Guide](troubleshooting-advanced) for error resolution.

## Daily Use Tips

### Morning Routine

1. Load coffee maker with water and grounds the night before
2. In the morning, open Coffee Bot on your phone
3. Tap **Auto Brew**
4. Wait 5-7 minutes for brewing to complete
5. Enjoy fresh coffee!

### Scheduled Brewing

Automatic scheduling is planned but not yet implemented. See [Future Plans](../future_plans.md).

## Advanced Usage

### API Endpoints

Coffee Bot exposes simple HTTP endpoints you can call from scripts or automation:

**Press a button:**
```bash
curl http://coffee-bot/press/auto
curl http://coffee-bot/press/power
curl http://coffee-bot/press/brew
```

**Get status:**
```bash
curl http://coffee-bot/status
```

Returns JSON with current configuration.

**Regenerate ntfy topic:**
```bash
curl -X POST http://coffee-bot/regenerate_topic
```

### Multiple Coffee Bots

If you have multiple Coffee Bots on your network:
1. Give each a unique hostname during Pi setup
2. Each will have its own ntfy topic
3. Bookmark each in your browser: `http://coffee-bot-1/`, `http://coffee-bot-2/`

## Frequently Asked Questions

**Q: Can I add more servos?**
A: Yes! The PCA9685 HAT supports up to 16 servos. See [Configuration Guide](configuration) for adding a third servo for brew size selection.

**Q: Does Coffee Bot work with all coffee makers?**
A: It works with any coffee maker that has physical buttons. Touch screens and capacitive buttons may not work, though you could try fake (or real if you're a psychopath) fingertips on the ends of the servo arms.

**Q: Can I use Coffee Bot with a Keurig?**
A: Yes, if your Keurig model has physical buttons for power and brew.

**Q: Will Coffee Bot drain my coffee maker's water tank?**
A: No, Coffee Bot only presses buttons. You still need to load water and grounds manually.

**Q: Can I schedule brewing for specific times?**
A: Not yet, but it's planned! See [Future Plans](../future_plans.md).

**Q: Is Coffee Bot secure?**
A: On a local network, secure enough. Don't expose to internet without proper authentication.

## Need More Help?

- [Configuration Guide](configuration) - Customize servo settings
- [Troubleshooting Guide](troubleshooting-advanced) - Fix common issues
- [GitHub Issues](https://github.com/NinjaGeoff/coffee_bot/issues) - Get community support
- [All Documentation](https://ninjageoff.github.io/coffee_bot/) - Complete docs site