#!/bin/bash

set -e

# === CONFIGURATION ===
REPO_URL="https://github.com/livitup/n3ocq-dmr-repeater.git"
CLONE_DIR="$HOME/n3ocq-dmr-repeater"
ROLE="2"  # 2 = Repeater
LOG_FILE="/var/log/bootstrap.log"
CONFIG_FILE="/etc/dmr/setup.cfg"

# === FUNCTIONS ===
function say() {
  echo -e "\033[1;32m[BOOTSTRAP]\033[0m $1" | tee -a "$LOG_FILE"
}

function configure_networking() {
  echo "" | tee -a "$LOG_FILE"
  echo "Select network configuration mode:" | tee -a "$LOG_FILE"
  echo "  1) Wired (DHCP)" | tee -a "$LOG_FILE"
  echo "  2) Wired (Static IP)" | tee -a "$LOG_FILE"
  echo "  3) Wi-Fi (DHCP)" | tee -a "$LOG_FILE"
  read -p "Enter choice [1-3]: " net_choice

  case $net_choice in
    1)
      say "Using wired DHCP (default)."
      sudo rm -f /etc/dhcpcd.conf
      echo -e "interface eth0\n  fallback static_eth0" | sudo tee /etc/dhcpcd.conf >> "$LOG_FILE"
      ;;

    2)
      read -p "Enter static IP address (e.g. 192.168.1.100/24): " static_ip
      read -p "Enter gateway (e.g. 192.168.1.1): " gateway
      say "Configuring wired static IP..."
      sudo bash -c "cat > /etc/dhcpcd.conf" <<EOF
interface eth0
  static ip_address=$static_ip
  static routers=$gateway
  static domain_name_servers=8.8.8.8 1.1.1.1
EOF
      ;;

    3)
      read -p "Enter Wi-Fi SSID: " ssid
      read -sp "Enter Wi-Fi Password: " password
      echo ""
      say "Configuring Wi-Fi..."
      sudo bash -c "wpa_passphrase '$ssid' '$password' > /etc/wpa_supplicant/wpa_supplicant.conf"
      sudo rfkill unblock wifi
      sudo systemctl enable wpa_supplicant
      sudo systemctl restart wpa_supplicant
      ;;

    *)
      echo "Invalid selection. Defaulting to wired DHCP." | tee -a "$LOG_FILE"
      ;;
  esac
}

function install_dmrgateway() {
  say "Installing DMRGateway from source..."
  if [ ! -d "$HOME/DMRGateway" ]; then
    git clone https://github.com/g4klx/DMRGateway.git "$HOME/DMRGateway" | tee -a "$LOG_FILE"
  else
    say "DMRGateway source already exists. Skipping clone."
  fi
  cd "$HOME/DMRGateway"
  make -j$(nproc) | tee -a "$LOG_FILE"
  sudo cp DMRGateway /usr/local/bin/
  say "DMRGateway installed to /usr/local/bin/DMRGateway"
}

# Prepare log
mkdir -p /var/log
sudo rm -f "$LOG_FILE"
sudo touch "$LOG_FILE"
sudo chown $(whoami):$(whoami) "$LOG_FILE"

say "Updating package index and installing dependencies..."
sudo apt update | tee -a "$LOG_FILE"
sudo apt full-upgrade -y | tee -a "$LOG_FILE"
sudo apt install -y \
  git \
  python3 python3-venv python3-pip \
  cmake libusb-1.0-0-dev \
  libwxgtk3.2-dev libasound2-dev libudev-dev \
  libpulse-dev libfftw3-dev libgps-dev libi2c-dev \
  wireless-tools wpasupplicant net-tools | tee -a "$LOG_FILE"

configure_networking
install_dmrgateway

say "Cloning dmr-repeater-setup-tools repository..."
if [ ! -d "$CLONE_DIR" ]; then
  git clone "$REPO_URL" "$CLONE_DIR" | tee -a "$LOG_FILE"
else
  say "Repo already cloned. Skipping."
fi

cd "$CLONE_DIR"

if [ -f "$CONFIG_FILE" ]; then
  say "Using config file at $CONFIG_FILE for installation..."
  sudo python3 install.py --role repeater --config "$CONFIG_FILE" | tee -a "$LOG_FILE"
else
  say "No config file found. Proceeding with default role install (role=$ROLE)..."
  echo -e "$ROLE\n" | sudo python3 install.py | tee -a "$LOG_FILE"
fi

say "Enabling and starting DMRGateway service..."
sudo systemctl enable dmrgateway.service | tee -a "$LOG_FILE"
sudo systemctl restart dmrgateway.service | tee -a "$LOG_FILE"

say "Checking status of DMRGateway service..."
if systemctl is-active --quiet dmrgateway.service; then
  say "✅ DMRGateway service is running."
else
  say "❌ DMRGateway service is NOT running. Please review the log at $LOG_FILE"
fi

say "Setup complete. You may reboot if desired."
echo -e "\nTo start services manually:\n  sudo systemctl restart dmrgateway.service" | tee -a "$LOG_FILE"
echo -e "\n✅ Repeater setup ready." | tee -a "$LOG_FILE"
