#!/bin/bash
# Coffee Bot One-Line Installer

set -e

echo "============================="
echo "Starting Coffee Bot Install!"
echo "============================="

# Create temp directory
TMP_DIR=$(mktemp -d)
cd "$TMP_DIR"

# Download latest release as ZIP (dev branch)
echo "Downloading Coffee Bot..."
curl -sSL https://github.com/NinjaGeoff/coffee_bot/archive/refs/heads/dev.zip -o coffeebot.zip

# Extract
echo "Extracting files..."
unzip -q coffeebot.zip
cd coffee_bot-main

# Move to home directory
INSTALL_DIR="$HOME/coffee_bot"
if [ -d "$INSTALL_DIR" ]; then
    echo "Backing up existing installation..."
    mv "$INSTALL_DIR" "$INSTALL_DIR.backup.$(date +%s)"
fi

mv "$TMP_DIR/coffee_bot-main" "$INSTALL_DIR"
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