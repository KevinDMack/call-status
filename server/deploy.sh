#!/bin/bash
#
# Deploy script for Call Status API Server
# This script deploys the server on a Raspberry Pi Zero
#

set -e

echo "=========================================="
echo "Call Status Server Deployment"
echo "=========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (use sudo)"
  exit 1
fi

# Configuration
INSTALL_DIR="/opt/call-status-server"
DATA_DIR="/var/lib/call-status"
SERVICE_FILE="call-status-server.service"

echo "Installing dependencies..."
apt-get update
apt-get install -y python3 python3-pip python3-venv

echo "Creating installation directory..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$DATA_DIR"

echo "Copying application files..."
cp api_server.py "$INSTALL_DIR/"
cp requirements.txt "$INSTALL_DIR/"

echo "Creating virtual environment..."
python3 -m venv "$INSTALL_DIR/venv"

echo "Installing Python dependencies..."
"$INSTALL_DIR/venv/bin/pip" install --upgrade pip
"$INSTALL_DIR/venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt"

echo "Setting permissions..."
chown -R www-data:www-data "$INSTALL_DIR"
chown -R www-data:www-data "$DATA_DIR"

echo "Installing systemd service..."
cp "$SERVICE_FILE" /etc/systemd/system/
systemctl daemon-reload

echo "Enabling and starting service..."
systemctl enable call-status-server.service
systemctl restart call-status-server.service

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Service status:"
systemctl status call-status-server.service --no-pager
echo ""
echo "To check logs, run:"
echo "  sudo journalctl -u call-status-server.service -f"
echo ""
echo "API endpoints:"
echo "  GET  http://localhost:5000/status"
echo "  POST http://localhost:5000/status"
echo "  GET  http://localhost:5000/health"
