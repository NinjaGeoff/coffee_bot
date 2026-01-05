#!/bin/bash

# Get the current system timezone
CURRENT_TZ=$(timedatectl | grep "Time zone" | awk '{print $3}')

echo "-----------------------------------------------"
echo "COFFEE BOT SYSTEM SETUP"
echo "CURRENT TIMEZONE: $CURRENT_TZ"
echo "-----------------------------------------------"

read -p "Is this timezone correct? (y/n): " confirm

if [[ $confirm == [nN] || $confirm == [nN][oO] ]]; then
    echo "Select your Timezone region:"
    
    # Standardized to America/[City] format
    options=(
        "America/New_York" 
        "America/Chicago" 
        "America/Denver" 
        "America/Phoenix" 
        "America/Los_Angeles" 
        "America/Anchorage" 
        "America/Adak"
        "Pacific/Honolulu"
        "Exit"
    )
    
    select opt in "${options[@]}"
    do
        case $opt in
            "America/New_York"|"America/Chicago"|"America/Denver"|"America/Phoenix"|"America/Los_Angeles"|"America/Anchorage"|"America/Adak"|"Pacific/Honolulu")
                echo "Applying timezone: $opt..."
                sudo timedatectl set-timezone "$opt"
                break
                ;;
            "Exit")
                echo "Setup cancelled."
                break
                ;;
            *) echo "Invalid option. Please enter a number from the list.";;
        esac
    done
else
    echo "Timezone confirmed."
fi

echo "The system time is now: $(date)"

# 2. Update system and install system dependencies
echo "--- Installing System Dependencies ---"
sudo apt update
sudo apt install -y git python3-pip python3-venv libopenjp2-7

# Install iptables-persistent without the interactive prompts
echo "Configuring Port 80 to Port 5000 redirection..."
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y iptables-persistent

# Apply the redirect rule
sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 5000

# Save it so it survives reboot
sudo netfilter-persistent save

# 3. Set up Python Virtual Environment
echo "--- Setting up Python Virtual Environment ---"
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
if [ ! -d "$DIR/env" ]; then
    python3 -m venv "$DIR/env"
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi

# 4. Install Python Libraries inside the environment
echo "--- Installing Python Libraries ---"
$DIR/env/bin/pip install flask RPi.GPIO apprise qrcode[pil] adafruit-circuitpython-pca9685

# 5. Create the Systemd Service
echo "--- Configuring Auto-Start Service ---"
USER=$(whoami)
sudo bash -c "cat > /etc/systemd/system/coffeebot.service" << EOF
[Unit]
Description=Coffee Bot Flask Web Server
After=network.target

[Service]
User=$USER
WorkingDirectory=$DIR
ExecStart=$DIR/env/bin/python $DIR/coffee_web.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 6. Enable and Start
echo "--- Starting Service ---"
sudo systemctl daemon-reload
sudo systemctl enable coffeebot.service
sudo systemctl restart coffeebot.service

echo "------------------------------------------------"
echo "SETUP COMPLETE!"
echo "Your Coffee Bot should be live at: http://$(hostname | awk '{print $1}')/ or http://$(hostname -I | awk '{print $1}')/"
echo "Check status with: sudo systemctl status coffeebot.service"