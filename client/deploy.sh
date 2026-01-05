#!/bin/bash
#
# Deploy script for Call Status Client
# This script deploys the client on a Raspberry Pi Zero
#

set -e

echo "=========================================="
echo "Call Status Client Deployment"
echo "=========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (use sudo)"
  exit 1
fi

# Configuration
INSTALL_DIR="/opt/call-status-client"
SERVICE_FILE="call-status-client.service"

# Prompt for API URL if not provided
if [ -z "$API_URL" ]; then
  read -p "Enter API URL (default: http://localhost:5000/status): " API_URL
  API_URL=${API_URL:-"http://localhost:5000/status"}
fi

echo "Installing dependencies..."
apt-get update
apt-get install -y python3 python3-pip python3-venv

echo "Creating installation directory..."
mkdir -p "$INSTALL_DIR"

echo "Copying application files..."
cp status_client.py "$INSTALL_DIR/"
cp requirements.txt "$INSTALL_DIR/"

echo "Creating virtual environment..."
python3 -m venv "$INSTALL_DIR/venv"

echo "Installing Python dependencies..."
"$INSTALL_DIR/venv/bin/pip" install --upgrade pip
"$INSTALL_DIR/venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt"

echo "Setting permissions..."
chown -R pi:pi "$INSTALL_DIR" 2>/dev/null || chown -R $SUDO_USER:$SUDO_USER "$INSTALL_DIR"

echo "Configuring systemd service..."
# Update the service file with the provided API URL
sed "s|Environment=\"API_URL=.*\"|Environment=\"API_URL=$API_URL\"|g" "$SERVICE_FILE" > /tmp/call-status-client.service
cp /tmp/call-status-client.service /etc/systemd/system/
rm /tmp/call-status-client.service
systemctl daemon-reload

echo "Enabling and starting service..."
systemctl enable call-status-client.service
systemctl restart call-status-client.service

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Service status:"
systemctl status call-status-client.service --no-pager
echo ""
echo "To check logs, run:"
echo "  sudo journalctl -u call-status-client.service -f"
echo ""
echo "Configuration:"
echo "  API URL: $API_URL"
echo "  Poll Interval: 60 seconds"
