# Configuration Guide

Learn how to customize Coffee Bot's servo settings, timing, and behavior to work perfectly with your coffee maker.

## Overview

Coffee Bot's configuration is stored in `coffee_web.py`. This guide shows you how to safely adjust settings for optimal performance.

## Servo Configuration

### Understanding the Settings

Coffee Bot uses these parameters to control servo movement:

```python
servo_config = {
    'rest_angle': 0,       # Starting/resting position (degrees)
    'active_angle': 45,    # Activated/button-press position (degrees)
    'move_time': 0.3,      # Time for servo to complete movement (seconds)
    'hold_time': 0.25,     # Time to hold button pressed (seconds)
}
```

**Total button press duration = (move_time × 2) + hold_time**
- Default: `(0.3 × 2) + 0.25 = 0.85 seconds` per button press

### Servo Angle Settings

**rest_angle** - The neutral position when servo is not pressing button
- Default: `0°`
- Range: `0°` to `180°`
- Typical: `0°` to `15°`

**active_angle** - The position when pressing the button
- Default: `45°`
- Range: `0°` to `180°`
- Typical: `30°` to `60°`

**How to determine correct angles:**

1. Start with default values
2. Test using web interface
3. If servo doesn't reach button, increase `active_angle`
4. If servo overshoots or hits obstacles, decrease `active_angle`
5. Adjust `rest_angle` if servo interferes with coffee maker at rest

### Timing Settings

**move_time** - Delay to allow servo to reach target position
- Default: `0.3` seconds
- Minimum: ~`0.1` seconds (for MG90S servos moving 60°)
- Typical: `0.2` to `0.5` seconds

**MG90S servo specs:**
- Operating speed: 0.1s per 60° at no load
- For 45° movement: minimum ~0.075s
- Add buffer for loaded conditions: 0.2-0.3s recommended

**hold_time** - How long to keep button pressed
- Default: `0.25` seconds
- Minimum: `0.1` seconds (some coffee makers need longer)
- Typical: `0.2` to `0.5` seconds

**Timing considerations:**
- Too short `move_time`: Servo may not reach position, button won't press
- Too long `move_time`: Slower operation, but more reliable
- Too short `hold_time`: Coffee maker may not register button press
- Too long `hold_time`: Unnecessary delay, but won't harm anything

## How to Modify Configuration

### Step 1: Connect to Your Pi

```bash
ssh pi@coffee-bot
```

### Step 2: Edit Configuration File

```bash
nano ~/coffee_bot/coffee_web.py
```

### Step 3: Find Configuration Section

Scroll to the top of the file (around line 30-40). You'll see:

```python
# ============================================================================
# SERVO CONFIGURATION
# ============================================================================

# Servo Channel Assignments on PCA9685
SERVO_POWER_CHANNEL = 0   # Channel 0 - Power button
SERVO_BREW_CHANNEL = 1    # Channel 1 - Brew button

# Servo Angle Settings
servo_config = {
    'rest_angle': 0,       # Starting/resting position (degrees)
    'active_angle': 45,    # Activated position (degrees)
    'move_time': 0.3,      # Time to allow servo to complete movement (seconds)
    'hold_time': 0.25,     # Time to hold in active position (seconds)
}
```

### Step 4: Modify Values

Example modifications:

**For faster operation:**
```python
servo_config = {
    'rest_angle': 0,
    'active_angle': 45,
    'move_time': 0.2,      # Reduced from 0.3
    'hold_time': 0.15,     # Reduced from 0.25
}
```

**For larger button press movement:**
```python
servo_config = {
    'rest_angle': 0,
    'active_angle': 60,    # Increased from 45
    'move_time': 0.35,     # Increased for longer movement
    'hold_time': 0.25,
}
```

**For more reliable pressing:**
```python
servo_config = {
    'rest_angle': 0,
    'active_angle': 45,
    'move_time': 0.4,      # More time to reach position
    'hold_time': 0.35,     # Hold button longer
}
```

### Step 5: Save and Exit

Press `Ctrl+X`, then `Y`, then `Enter`

### Step 6: Restart Service

```bash
sudo systemctl restart coffeebot.service
```

### Step 7: Test Changes

1. Wait 10-15 seconds for service to start
2. Open web interface: `http://coffee-bot/`
3. Test each button individually
4. Watch servo movement and button pressing
5. Repeat adjustment if needed

## Auto Brew Timing

The auto-brew sequence has its own timing configuration:

```python
auto_brew_config = {
    'power_on_delay': 2.0,  # Seconds to wait after power on before brewing
}
```

**power_on_delay** - Delay between pressing power and pressing brew
- Default: `2.0` seconds
- Minimum: `1.0` second (some coffee makers need more)
- Typical: `1.5` to `3.0` seconds

**How to adjust:**

1. Time how long your coffee maker takes to fully power on
2. Add 0.5-1.0 seconds as buffer
3. Update `power_on_delay` value
4. Test auto brew sequence

**Example for slower coffee maker:**
```python
auto_brew_config = {
    'power_on_delay': 3.5,  # Wait 3.5 seconds for older coffee maker
}
```

## Rate Limiting

To prevent servo abuse and accidental double-clicks:

```python
# Minimum seconds between button presses (adjustable)
RATE_LIMIT_SECONDS = 3
```

**Adjust for your use case:**

**More protective (for heavy use or shared access):**
```python
RATE_LIMIT_SECONDS = 5  # 5 seconds between presses
```

**Less restrictive (for personal use):**
```python
RATE_LIMIT_SECONDS = 1  # 1 second between presses
```

**Disable rate limiting (not recommended):**
```python
RATE_LIMIT_SECONDS = 0  # No rate limiting
```

## Channel Assignment

By default:
- Channel 0 = Power button
- Channel 1 = Brew button

**To swap servo channels:**

```python
SERVO_POWER_CHANNEL = 1   # Now on channel 1
SERVO_BREW_CHANNEL = 0    # Now on channel 0
```

Don't forget to physically swap servo connections on the HAT!

## Adding a Third Servo

For coffee makers with brew size selection (e.g., single cup vs carafe):

### Step 1: Connect Third Servo

Connect servo to channel 2 (S2) on the Servo Driver HAT.

### Step 2: Add Channel Assignment

In `coffee_web.py`:

```python
SERVO_POWER_CHANNEL = 0   # Channel 0 - Power button
SERVO_BREW_CHANNEL = 1    # Channel 1 - Brew button
SERVO_SIZE_CHANNEL = 2    # Channel 2 - Brew size button
```

### Step 3: Add Press Function

Add after the existing `press_brew()` function:

```python
def press_size(notify=True):
    """
    Press the brew size button
    
    Args:
        notify: Send ntfy notification (default: True)
    """
    logger.info("Pressing SIZE button")
    activate_servo(SERVO_SIZE_CHANNEL, "Size Button")
    if notify:
        send_ntfy_notification("☕ Brew size button pressed")
```

### Step 4: Add Web Route

Add a new route:

```python
@app.route('/press/size')
def press_size_route():
    allowed, remaining = check_rate_limit('size')
    if not allowed:
        return jsonify({
            'error': 'Rate limit exceeded',
            'message': f'Please wait {remaining:.1f} seconds'
        }), 429
    
    if not servo_operation_lock.acquire(blocking=False):
        return jsonify({
            'error': 'Operation in progress',
            'message': 'Another servo operation is running'
        }), 409
    
    try:
        press_size()
        return jsonify({'success': True, 'message': 'Size button pressed'}), 200
    except Exception as e:
        logger.error(f"ERROR during size operation: {e}", exc_info=True)
        return jsonify({
            'error': 'Operation failed',
            'message': f'Failed to execute size operation'
        }), 500
    finally:
        servo_operation_lock.release()
```

### Step 5: Update Web Interface

Edit `templates/index.html` to add a button:

```html
<button class="btn size" onclick="pressButton('size')">☕ Size Select</button>
```

Add CSS for the button in `static/style.css`:

```css
.size {
    background-color: #f39c12;
}

.size:hover {
    background-color: #e67e22;
}
```

### Step 6: Test Third Servo

Restart service and test new button in web interface.

## Advanced: Per-Servo Configuration

If you need different settings for each servo:

```python
servo_power_config = {
    'rest_angle': 0,
    'active_angle': 45,
    'move_time': 0.3,
    'hold_time': 0.25,
}

servo_brew_config = {
    'rest_angle': 0,
    'active_angle': 60,    # Different angle
    'move_time': 0.4,      # Slower movement
    'hold_time': 0.3,      # Longer press
}
```

Then modify `press_power()` and `press_brew()` to use their respective configs.

## Configuration Best Practices

### Testing Changes

1. **Test one change at a time** - Don't modify multiple values simultaneously
2. **Start conservative** - Begin with longer times, then optimize
3. **Watch servo movement** - Observe actual button pressing, not just logs
4. **Test all buttons** - Verify power, brew, and auto brew all work
5. **Test after reboot** - Ensure changes persist and service starts correctly

### Safety Guidelines

- **Never set angles beyond servo limits** (0-180°)
- **Don't set timing too low** - Servos need time to move
- **Test mechanical clearance** - Ensure servo horn doesn't hit obstacles
- **Keep rate limiting enabled** - Protects servo hardware

### Backup Your Configuration

Before making changes:

```bash
cp ~/coffee_bot/coffee_web.py ~/coffee_bot/coffee_web.py.backup
```

To restore:

```bash
cp ~/coffee_bot/coffee_web.py.backup ~/coffee_bot/coffee_web.py
sudo systemctl restart coffeebot.service
```

## Troubleshooting Configuration Issues

### Servo Not Reaching Button

**Symptoms:** Button doesn't get pressed, servo stops short

**Solutions:**
1. Increase `active_angle` by 5-10°
2. Increase `move_time` to allow servo to reach position
3. Check servo horn is properly attached
4. Verify servo isn't mechanically blocked

### Servo Overshooting

**Symptoms:** Servo hits obstacles, horn breaks off

**Solutions:**
1. Decrease `active_angle` by 5-10°
2. Adjust physical servo mounting position
3. Check servo horn orientation

### Button Press Not Registering

**Symptoms:** Servo moves but coffee maker doesn't respond

**Solutions:**
1. Increase `hold_time` - some buttons need longer press
2. Check servo horn is making good contact with button
3. Increase `active_angle` for firmer press
4. Verify button is actually being pressed (watch closely)

### Servo Jittering or Stuttering

**Symptoms:** Servo shakes or vibrates during movement

**Solutions:**
1. Check external power supply voltage (should be 5-6V)
2. Ensure power supply can handle current (2A+ recommended)
3. Add capacitor across servo power terminals (100µF)
4. Check for loose servo connections

### Service Won't Start After Changes

**Symptoms:** `sudo systemctl status coffeebot.service` shows failed

**Solutions:**
1. Check for syntax errors: `python3 ~/coffee_bot/coffee_web.py`
2. View error logs: `sudo journalctl -u coffeebot.service -n 50`
3. Restore backup: `cp ~/coffee_bot/coffee_web.py.backup ~/coffee_bot/coffee_web.py`

## Example Configurations

### For Fast, Responsive Coffee Maker

```python
servo_config = {
    'rest_angle': 0,
    'active_angle': 40,
    'move_time': 0.2,
    'hold_time': 0.15,
}

auto_brew_config = {
    'power_on_delay': 1.5,
}

RATE_LIMIT_SECONDS = 2
```

### For Slow, Older Coffee Maker

```python
servo_config = {
    'rest_angle': 0,
    'active_angle': 55,
    'move_time': 0.4,
    'hold_time': 0.4,
}

auto_brew_config = {
    'power_on_delay': 4.0,
}

RATE_LIMIT_SECONDS = 3
```

### For Keurig K-Cup Machines

```python
servo_config = {
    'rest_angle': 0,
    'active_angle': 50,    # Firmer press needed
    'move_time': 0.3,
    'hold_time': 0.3,      # Longer hold for tactile buttons
}

auto_brew_config = {
    'power_on_delay': 2.5,  # Keurigs take a moment to heat
}

RATE_LIMIT_SECONDS = 5  # Prevent accidental multiple cups
```

## Configuration Reference

Quick reference table:

| Setting | Default | Range | Purpose |
|---------|---------|-------|---------|
| `rest_angle` | 0° | 0-180° | Servo neutral position |
| `active_angle` | 45° | 0-180° | Button press position |
| `move_time` | 0.3s | 0.1-1.0s | Servo movement delay |
| `hold_time` | 0.25s | 0.1-1.0s | Button hold duration |
| `power_on_delay` | 2.0s | 1.0-5.0s | Auto brew power-to-brew delay |
| `RATE_LIMIT_SECONDS` | 3 | 0-10 | Cooldown between presses |

## Need More Help?

- [Troubleshooting Guide](troubleshooting-advanced) - Fix hardware issues
- [Usage Guide](usage-guide) - Learn the web interface
- [GitHub Issues](https://github.com/NinjaGeoff/coffee_bot/issues) - Get help from community