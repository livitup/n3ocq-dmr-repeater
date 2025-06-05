#!/bin/bash

# Exit on error
set -e

# Variables
INSTALL_DIR="/opt/hblink"
VENV_DIR="${INSTALL_DIR}/venv"
HBLINK_REPO="https://github.com/n0mjs710/HBlink3.git"
HBLINK_BRANCH="main"
CONFIG_REPO="${HOME}/hblink3-config"

echo "==> Installing system dependencies..."
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git

echo "==> Cloning HBLink3 repository..."
sudo git clone ${HBLINK_REPO} ${INSTALL_DIR}
cd ${INSTALL_DIR}
sudo git checkout ${HBLINK_BRANCH}

echo "==> Creating Python virtual environment..."
sudo python3 -m venv ${VENV_DIR}

echo "==> Installing Python packages..."
sudo ${VENV_DIR}/bin/pip install --upgrade pip
sudo ${VENV_DIR}/bin/pip install -r requirements.txt

echo "==> Copying HBlink configuration..."
sudo cp ${CONFIG_REPO}/config/hblink.cfg ${INSTALL_DIR}/hblink.cfg

echo "==> Copying systemd service file..."
sudo cp ${CONFIG_REPO}/systemd/hblink3.service /etc/systemd/system/hblink3.service

echo "==> Reloading systemd..."
sudo systemctl daemon-reload
sudo systemctl enable hblink3.service

echo "==> HBLink3 install complete!"
echo "You may now start HBLink3 with: sudo systemctl start hblink3.service"

