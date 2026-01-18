#!/bin/bash
# Coffee Bot One-Line Installer

echo "============================="
echo "Starting Coffee Bot Install!"
echo "============================="

# Create temp directory
TMP_DIR=$(mktemp -d)

# Download latest release as ZIP (dev branch)
# Change the URL below to switch branch to main before push to main!
echo "Downloading Coffee Bot..."
curl -sSL https://github.com/NinjaGeoff/coffee_bot/archive/refs/heads/dev.zip -o "$TMP_DIR/coffeebot.zip"

# Extract
echo "Extracting files..."
unzip -q "$TMP_DIR/coffeebot.zip" -d "$TMP_DIR"

# Move to home directory
INSTALL_DIR="$HOME/coffee_bot"
if [ -d "$INSTALL_DIR" ]; then
    echo "Backing up existing installation..."
    mv "$INSTALL_DIR" "$INSTALL_DIR.backup.$(date +%s)"
fi

echo "Installing to $INSTALL_DIR..."
# Change to coffee_bot-main for main branch before push to main!
mv "$TMP_DIR/coffee_bot-dev" "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Run setup
echo "Running setup script..."
chmod +x setup.sh
./setup.sh

# Cleanup
rm -rf "$TMP_DIR"

echo "======================"
echo "Installation complete!"
echo "======================"