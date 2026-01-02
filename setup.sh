#!/bin/bash

# 1. Update system and install system dependencies
echo "--- Installing System Dependencies ---"
sudo apt update
sudo apt install -y git python3-pip python3-venv

# 2. Set up Python Virtual Environment
echo "--- Setting up Python Virtual Environment ---"
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
if [ ! -d "$DIR/env" ]; then
    python3 -m venv "$DIR/env"
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi

# 3. Install Python Libraries inside the environment
echo "--- Installing Python Libraries ---"
$DIR/env/bin/pip install flask RPi.GPIO

# 4. Create the Systemd Service
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

# 5. Enable and Start
echo "--- Starting Service ---"
sudo systemctl daemon-reload
sudo systemctl enable coffeebot.service
sudo systemctl restart coffeebot.service

echo "------------------------------------------------"
echo "SETUP COMPLETE!"
echo "Your Coffee Bot should be live at: http://$(hostname -I | awk '{print $1}'):5000"
echo "Check status with: sudo systemctl status coffeebot.service"