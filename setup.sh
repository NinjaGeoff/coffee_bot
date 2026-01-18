#!/bin/bash

echo "-----------------------------------------------"
echo "Calling Timezone Setup Script"
echo "-----------------------------------------------"
# Define the script directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Ensure the timezone script is executable
if [ -f "$DIR/set_timezone.sh" ]; then
    chmod +x "$DIR/set_timezone.sh"
    "$DIR/set_timezone.sh"
else
    echo "WARNING: set_timezone.sh not found, skipping timezone setup."
fi

# Remove docs folder (not needed on Pi, only used for GitHub Pages)
echo "--- Removing documentation folder (not needed on Pi) ---"
if [ -d "$DIR/docs" ]; then
    rm -rf "$DIR/docs"
    echo "Removed /docs folder"
else
    echo "/docs folder not found (already removed or not present)"
fi

echo "-----------------------------------------------"
echo "COFFEE BOT SYSTEM SETUP - PCA9685 VERSION"
echo "-----------------------------------------------"

# Enable I2C interface (required for PCA9685)
echo "--- Enabling I2C Interface ---"
sudo raspi-config nonint do_i2c 0
echo "I2C enabled"

# Update system and install system dependencies
echo "--- Installing System Dependencies ---"
sudo apt update
sudo apt install -y git python3-pip python3-venv libopenjp2-7 i2c-tools

# Install iptables-persistent without the interactive prompts
echo "Configuring Port 80 to Port 5000 redirection..."
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y iptables-persistent

# Apply the redirect rule
sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 5000

# Save it so it survives reboot
sudo netfilter-persistent save

# Set up Python Virtual Environment
echo "--- Setting up Python Virtual Environment ---"
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
if [ ! -d "$DIR/env" ]; then
    python3 -m venv "$DIR/env"
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi

# Install Python Libraries inside the environment
# Note: Installing adafruit-circuitpython-servokit for PCA9685 control
echo "--- Installing Python Libraries ---"
$DIR/env/bin/pip install --upgrade pip
$DIR/env/bin/pip install flask adafruit-circuitpython-servokit qrcode[pil] requests markdown

# Setup application folder structure
echo "--- Setting Up Application Folder Structure ---"

# Create required folders
mkdir -p "$DIR/static"
mkdir -p "$DIR/templates"

# Verify critical files exist
if [ ! -f "$DIR/coffee_web.py" ]; then
    echo "ERROR: coffee_web.py not found!"
    exit 1
fi

if [ ! -f "$DIR/templates/index.html" ]; then
    echo "ERROR: templates/index.html not found!"
    echo "Please ensure index.html is in the templates/ folder"
    exit 1
fi

echo "Folder structure validated"

# Set secure permissions on ntfy topic file if it exists
if [ -f "$DIR/ntfy_topic.txt" ]; then
    chmod 600 "$DIR/ntfy_topic.txt"
    echo "Set secure permissions on ntfy_topic.txt"
fi

# Verify I2C is working
echo "--- Verifying I2C Configuration ---"
# Detect which I2C bus is available (usually bus 1 on modern Pi)
if i2cdetect -y 1 &> /dev/null; then
    BUS=1
elif i2cdetect -y 0 &> /dev/null; then
    BUS=0
    echo "Note: Using I2C bus 0 (older Pi model)"
else
    echo "ERROR: No I2C bus detected!"
    echo "Make sure I2C is enabled and reboot."
    BUS=1  # Default to 1 for error message
fi

if [ $BUS -eq 1 ] || [ $BUS -eq 0 ]; then
    echo "I2C bus $BUS detected. Running i2cdetect..."
    echo "Expected: PCA9685 should appear at address 0x40"
    i2cdetect -y $BUS
    echo ""
    echo "If you see '40' in the grid above, your Servo Driver HAT is detected!"
else
    echo "WARNING: Could not access I2C bus. Make sure:"
    echo "  1. Servo Driver HAT is properly seated on GPIO pins"
    echo "  2. External power is connected to servo terminals"
    echo "  3. Reboot after this script completes"
fi

# Create the Systemd Service
echo "--- Configuring Auto-Start Service ---"
USER=$(whoami)
sudo bash -c "cat > /etc/systemd/system/coffeebot.service" << EOF
[Unit]
Description=Coffee Bot Flask Web Server (PCA9685 Version)
After=network.target

[Service]
ExecStartPre=/bin/sleep 5
User=$USER
WorkingDirectory=$DIR
ExecStart=$DIR/env/bin/python $DIR/coffee_web.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Configure log rotation
echo "--- Configuring Log Rotation ---"
sudo bash -c "cat > /etc/logrotate.d/coffeebot" << EOF
$DIR/coffee_bot.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
    create 0640 $USER $USER
}
EOF
echo "Log rotation configured (7 days retention)"

# Enable and Start
echo "--- Starting Service ---"
sudo systemctl daemon-reload
sudo systemctl enable coffeebot.service
sudo systemctl restart coffeebot.service

echo "------------------------------------------------"
echo "SETUP COMPLETE!"
echo "------------------------------------------------"
echo "Your Coffee Bot (PCA9685 Version) should be live at:"
echo "  http://$(hostname | awk '{print $1}')/"
echo "  http://$(hostname -I | awk '{print $1}')/"
echo ""
echo "Hardware Configuration:"
echo "  - Waveshare Servo Driver HAT (PCA9685)"
echo "  - I2C Communication (SDA: Pin 3, SCL: Pin 5)"
echo "  - Power Servo: Channel 0"
echo "  - Brew Servo: Channel 1"
echo "  - External 5-6V power required on servo terminals"
echo ""
echo "Check status with: sudo systemctl status coffeebot.service"
echo "View logs with: sudo journalctl -u coffeebot.service -f"
echo ""
echo "IMPORTANT: If servos don't work, verify:"
echo "  1. External power supply connected to servo terminals"
echo "  2. I2C address 0x40 detected (run: i2cdetect -y 1)"
echo "  3. Reboot if I2C was just enabled"
echo "------------------------------------------------"