# Hardware Setup & Wiring Guide

This guide walks you through assembling your Coffee Bot hardware from start to finish.

## What You'll Need

Before starting, make sure you have all the parts from the [Parts List](/docs/parts-list).

**Tools:**
- Small Phillips screwdriver (for servo horn attachment if needed)
- Wire strippers (optional, servo wires are pre-terminated)
- Multimeter (optional, for testing power supply voltage)

## Safety First

**Important Safety Notes:**
- Always disconnect power before making any connections
- Never connect/disconnect servos while powered
- Ensure power supply voltage is correct (5-6V for servos)
- Keep liquids away from electronics

## Step 1: Prepare the Raspberry Pi
1. **Insert the microSD card** with Raspberry Pi OS installed (see [Pi Imaging Guide](/docs/pi-imaging-guide))
2. **Do NOT power on yet** - we'll connect everything first

## Step 2: Attach the Waveshare Servo Driver HAT

The Servo Driver HAT provides 16 channels of servo control via I2C.

1. **Locate the 40-pin GPIO header** on your Raspberry Pi Zero 2W
2. **Align the Servo Driver HAT** carefully over the GPIO pins
3. **Press down firmly** until the HAT is fully seated
   - The HAT should sit flat on the Pi
   - All 40 pins should be fully inserted
4. **Verify alignment** - check from the side that pins aren't bent

## Step 3: Connect the Servos

You'll connect two MG90S servos to channels 0 and 1.

### Understanding Servo Wires

MG90S servos have 3 wires:
- **Brown/Black** = Ground (GND)
- **Red** = Power (V+)
- **Orange/Yellow** = Signal (S)

### Connecting Power Servo (Channel 0)

1. Locate the **S0** terminal on the Servo Driver HAT
2. Insert the servo connector:
   - Brown wire closest to the edge (GND)
   - Red wire in the middle (V+)
   - Orange wire toward the center (S0)
3. The connector should click into place

### Connecting Brew Servo (Channel 1)

1. Locate the **S1** terminal on the Servo Driver HAT
2. Insert the servo connector with the same orientation:
   - Brown → GND
   - Red → V+
   - Orange → S1

**Important:** Both servos should have the same wire orientation (all brown wires on the same side).

## Step 4: Connect External Power

The servos need external 5-6V power (they can't run from the Pi's 5V pins).

### Using the 9V 2A Power Supply

1. **Locate the screw terminals** on the Servo Driver HAT labeled "VIN" and "GND"
2. **Connect the barrel jack adapter** to your 9V power supply
3. **Identify positive and negative**:
   - Center pin = Positive (+)
   - Outer barrel = Negative (-)
4. **Wire to the HAT:**
   - Red wire (positive) → VIN terminal
   - Black wire (negative) → GND terminal
5. **Tighten the screws** firmly

**Verify voltage** before connecting if you have a multimeter. Should read ~9V DC.

## Step 5: Power the Raspberry Pi

You have two options for powering the Pi:

### Option A: USB Power (Recommended for Setup)
1. Use a micro USB cable connected to a 5V 2.5A+ power adapter
2. Connect to the **PWR IN** port on the Pi Zero 2W

### Option B: Power from the HAT
1. The Waveshare HAT can provide power to the Pi from the same 9V supply
2. Check your HAT documentation to enable this feature
3. This keeps cable count down but ties Pi power to servo power

## Step 6: Mechanical Mounting

Now mount the servos to your coffee maker.

### Positioning the Servos

1. **Identify button locations** on your coffee maker
2. **Test servo range** before mounting:
   ```bash
   # After setup, SSH into Pi and test:
   cd ~/coffee_bot
   source env/bin/activate
   python3
   >>> from adafruit_servokit import ServoKit
   >>> kit = ServoKit(channels=16)
   >>> kit.servo[0].angle = 45  # Test power servo
   >>> kit.servo[0].angle = 0   # Return to rest
   ```

3. **Mount servos** using:
   - Double-sided tape (temporary/testing)
   - Hot glue (semi-permanent)
   - 3D printed brackets (permanent, recommended)
   - Screws if your coffee maker has mounting points

4. **Attach servo horns** to press the buttons
   - The horn should reach the button when servo is at 45°
   - Rest position (0°) should be clear of the button

### Servo Orientation Tips

- Position servos so they rotate **toward** the button
- Keep servo wires away from moving parts
- Leave slack in wires for vibration/movement
- Test full range before securing permanently

## Step 7: Cable Management

Keep your wiring tidy and safe:

1. **Bundle servo wires** together with zip ties
2. **Route power cables** away from servo wires
3. **Secure HAT connection** - consider standoffs if shaking is an issue
4. **Label servos** if using more than two

## Step 8: First Power-On Test

1. **Double-check all connections**
2. **Plug in the 9V power supply** first
3. **Plug in the Pi's USB power** (if using separate power)
4. **Wait for Pi to boot** (30-60 seconds)
5. **Check I2C detection:**
   ```bash
   ssh pi@coffee-bot
   i2cdetect -y 1
   ```
   You should see `40` in the output grid

6. **Test servos from web interface:**
   - Navigate to `http://coffee-bot/`
   - Click "Power Toggle" button
   - Servo should move to 45° and back to 0°

## Troubleshooting First Boot

**Servos don't move:**
- Check external power connection
- Verify I2C shows address 0x40
- Check servo connectors are fully seated

**Can't connect to Pi:**
- Wait 2 minutes for first boot
- Check Wi-Fi credentials in Pi Imager
- Try `ping coffee-bot` from your computer

**HAT not detected:**
- Reseat the HAT on GPIO pins
- Reboot the Pi
- Check for bent GPIO pins

## Next Steps

Once hardware is working:

1. Run the setup script (see main README at [http://coffee-bot/](http://coffee-bot/))
2. Fine-tune servo angles in `coffee_web.py`
3. Set up mobile notifications (see main README)

## Advanced: Enclosure Design

Planning to 3D print an enclosure? Consider:

- Ventilation for the Pi
- Access to the microSD card slot
- Cable routing holes
- Mounting points for servos
- Easy access to power connections

---

**Need more help?** Check the [Advanced Troubleshooting](/docs/troubleshooting-advanced) guide.