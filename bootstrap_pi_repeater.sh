
#!/bin/bash

set -e

# === CONFIGURATION ===
REPO_URL="https://github.com/livitup/n3ocq-dmr-repeater.git"
CLONE_DIR="/opt/n3ocq-dmr-repeater"
CONFIG_FILE="/etc/dmr/setup.cfg"
LOG_FILE="/var/log/bootstrap.log"
ROLE="repeater"
G4KLX_DIR="/opt"
MMDVM_DIR="/opt"

# === FUNCTIONS ===
say() {
  echo -e "\033[1;32m[BOOTSTRAP]\033[0m $1" | tee -a "$LOG_FILE"
}

configure_uart_for_pi() {
  say "Checking UART configuration..."

  local FIRMWARE_CONFIG_FILE="/boot/firmware/config.txt"
  local CMDLINE_FILE="/boot/firmware/cmdline.txt"

  if [ ! -f "$FIRMWARE_CONFIG_FILE" ]; then
    say "⚠️ Cannot find $FIRMWARE_CONFIG_FILE"
    return
  fi

  MODEL=$(tr -d '\0' < /proc/device-tree/model 2>/dev/null || echo "Unknown")
  say "Detected Raspberry Pi model: $MODEL"

  enable_uart_set=$(grep -E "^enable_uart=1" "$FIRMWARE_CONFIG_FILE" || true)
  disable_bt_set=$(grep -E "^dtoverlay=disable-bt" "$FIRMWARE_CONFIG_FILE" || true)
  uart1_set=$(grep -E "^dtoverlay=uart1" "$FIRMWARE_CONFIG_FILE" || true)

  update_config() {
    sed -i '/^enable_uart=/d' "$FIRMWARE_CONFIG_FILE"
    echo "enable_uart=1" | tee -a "$FIRMWARE_CONFIG_FILE" >> "$LOG_FILE"

    if [[ "$1" == "disable-bt" ]]; then
      sed -i '/^dtoverlay=disable-bt/d' "$FIRMWARE_CONFIG_FILE"
      echo "dtoverlay=disable-bt" | tee -a "$FIRMWARE_CONFIG_FILE" >> "$LOG_FILE"
    elif [[ "$1" == "uart1" ]]; then
      sed -i '/^dtoverlay=uart1/d' "$FIRMWARE_CONFIG_FILE"
      echo "dtoverlay=uart1" | tee -a "$FIRMWARE_CONFIG_FILE" >> "$LOG_FILE"
    fi
  }

  case "$MODEL" in
    *"Raspberry Pi 4"*|*"Raspberry Pi 3"*|*"Compute Module 4"*)
      say "Applying: enable_uart=1 + dtoverlay=disable-bt"
      update_config disable-bt
      ;;
    *"Raspberry Pi 5"*|*"Compute Module 5"*)
      say "Applying: enable_uart=1 + dtoverlay=uart1"
      update_config uart1
      ;;
    *)
      say "⚠️ Unknown Pi model. Skipping UART config."
      return
      ;;
  esac

  # Remove serial console if present in cmdline.txt
  if grep -q "console=serial0" "$CMDLINE_FILE"; then
    say "Removing serial console from cmdline.txt..."
    sed -i 's/console=serial0[^ ]* //g' "$CMDLINE_FILE"
    sed -i 's/console=ttyAMA0[^ ]* //g' "$CMDLINE_FILE"
  fi
  # Disable Bluetooth if necessary
  if [[ "$MODEL" == *"Raspberry Pi 4"* || "$MODEL" == *"Raspberry Pi 3"* || "$MODEL" == *"Compute Module 4"* ]]; then
    say "Disabling hciuart service to free ttyAMA0..."
    systemctl disable hciuart 2>/dev/null || true
  fi
  echo -e "\nUART config updated. A reboot is required."
  read -p "Reboot now? [y/N]: " do_reboot
  if [[ "$do_reboot" =~ ^[Yy]$ ]]; then
    say "Rebooting..."
    reboot
  else
    say "Please reboot manually, then re-run this script."
    exit 1
  fi
}

configure_networking() {
  echo "" | tee -a "$LOG_FILE"
  echo "Select network configuration mode:" | tee -a "$LOG_FILE"
  echo "  1) Wired (DHCP)" | tee -a "$LOG_FILE"
  echo "  2) Wired (Static IP)" | tee -a "$LOG_FILE"
  echo "  3) Wi-Fi (DHCP)" | tee -a "$LOG_FILE"
  read -p "Enter choice [1-3]: " net_choice

  case $net_choice in
    1)
      say "Using wired DHCP (default)."
      cp /etc/dhcpcd.conf /etc/dhcpcd.conf.bak.$(date +%s) 2>/dev/null || true
      rm -f /etc/dhcpcd.conf
      echo -e "interface eth0\n  fallback static_eth0" | tee /etc/dhcpcd.conf >> "$LOG_FILE"
      say "Wrote /etc/dhcpcd.conf:"
      cat /etc/dhcpcd.conf | tee -a "$LOG_FILE"
      ;;
    2)
      read -p "Enter static IP address (e.g. 192.168.1.100/24): " static_ip
      read -p "Enter gateway (e.g. 192.168.1.1): " gateway
      say "Configuring wired static IP..."
      tee /etc/dhcpcd.conf > /dev/null <<EOF
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

      # Check for existing Wi-Fi config
      if [ -f /etc/wpa_supplicant/wpa_supplicant.conf ]; then
        if grep -q "ssid=" /etc/wpa_supplicant/wpa_supplicant.conf; then
          say "⚠️ An existing Wi-Fi configuration may interfere with the new setup:"
          say "    /etc/wpa_supplicant/wpa_supplicant.conf"
          say "    You may want to delete or review it before proceeding."
          read -p "Continue and overwrite it? [y/N]: " confirm_wifi
          if [[ ! "$confirm_wifi" =~ ^[Yy]$ ]]; then
            say "Aborting Wi-Fi configuration."
            return
          fi
        fi
      fi

      say "Configuring Wi-Fi..."
      bash -c "wpa_passphrase '$ssid' '$password' > /etc/wpa_supplicant/wpa_supplicant.conf"
      rfkill unblock wifi
      systemctl enable wpa_supplicant
      systemctl restart wpa_supplicant
      ;;

  esac
}

install_dependencies() {
  say "Updating package index and installing dependencies..."
  apt update | tee -a "$LOG_FILE"
  apt full-upgrade -y | tee -a "$LOG_FILE"
  apt install -y \
    git \
    build-essential cmake \
    python3 python3-venv python3-pip python3-serial \
    libusb-1.0-0-dev \
    libwxgtk3.2-dev libasound2-dev libudev-dev \
    libpulse-dev libfftw3-dev libgps-dev libi2c-dev \
    wireless-tools wpasupplicant net-tools | tee -a "$LOG_FILE"
}

create_user() {
  say "Ensuring mmdvm user and log directory exist..."
  id mmdvm &>/dev/null || useradd --system --home /var/log/mmdvm --shell /usr/sbin/nologin mmdvm
  mkdir -p /var/log/mmdvm
  chown mmdvm:mmdvm /var/log/mmdvm
}

install_dmrgateway() {
  say "Installing DMRGateway from source..."
  if [ ! -d "$G4KLX_DIR/DMRGateway" ]; then
    git clone https://github.com/g4klx/DMRGateway.git "$G4KLX_DIR/DMRGateway" | tee -a "$LOG_FILE"
  else
    say "DMRGateway source already exists. Skipping clone."
  fi
  cd "$G4KLX_DIR/DMRGateway"
  if [ -f DMRGateway ]; then
    say "DMRGateway binary already exists. Skipping build."
  else
    make -j$(nproc) | tee -a "$LOG_FILE"
  fi
  cp DMRGateway /usr/local/bin/
  say "DMRGateway installed to /usr/local/bin/DMRGateway"
}

install_mmdvmhost() {
  say "Installing MMDVMHost from source..."
  if [ ! -d "$MMDVM_DIR/MMDVMHost" ]; then
    git clone https://github.com/g4klx/MMDVMHost.git "$MMDVM_DIR/MMDVMHost" | tee -a "$LOG_FILE"
  else
    say "MMDVMHost source already exists. Skipping clone."
  fi
  cd "$MMDVM_DIR/MMDVMHost"
  if [ -f MMDVMHost ]; then
    say "MMDVMHost binary already exists. Skipping build."
  else
    make -j$(nproc) | tee -a "$LOG_FILE"
  fi
  cp MMDVMHost /usr/local/bin/
  say "MMDVMHost installed to /usr/local/bin/MMDVMHost"
}

run_python_installer() {
  say "Preparing n3ocq-dmr-repeater repository..."
  if [ ! -d "$CLONE_DIR/.git" ]; then
    say "Cloning repository..."
    if git clone "$REPO_URL" "$CLONE_DIR" | tee -a "$LOG_FILE"; then
      say "Repository cloned successfully."
    else
      say "❌ Failed to clone repository. Exiting."
      exit 1
    fi
  else
    say "Repository already exists. Pulling latest changes..."
    cd "$CLONE_DIR" || { say "❌ Failed to cd into $CLONE_DIR"; exit 1; }
    if git pull | tee -a "$LOG_FILE"; then
      say "Repository updated."
    else
      say "⚠️ Failed to update repository. Continuing with existing files."
    fi
  fi

  cd "$CLONE_DIR"

  if [ -f "$CONFIG_FILE" ]; then
    say "Using config file at $CONFIG_FILE for installation..."
    python3 install.py --role "$ROLE" --config "$CONFIG_FILE" | tee -a "$LOG_FILE"
  else
    say "No config file found. Proceeding with interactive install..."
    python3 install.py --role "$ROLE" | tee -a "$LOG_FILE"
  fi
}

stop_services() {
  say "Stopping DMRGateway and MMDVM services..."
  systemctl stop dmrgateway.service | tee -a "$LOG_FILE"
  systemctl stop mmdvmhost.service | tee -a "$LOG_FILE"
}

start_services() {
  say "Enabling and starting DMRGateway service..."
  systemctl daemon-reload | tee -a "$LOG_FILE"
  systemctl enable dmrgateway.service | tee -a "$LOG_FILE"
  systemctl restart dmrgateway.service | tee -a "$LOG_FILE"

  if systemctl is-active --quiet dmrgateway.service; then
    say "✅ DMRGateway service is running."
  else
    say "❌ DMRGateway service failed to start. Check the logs."
  fi
}

# === MAIN ===
[ "$EUID" -ne 0 ] && echo "Please run as root" && exit 1
mkdir -p /var/log
rm -f "$LOG_FILE"
touch "$LOG_FILE"
chown "$(whoami):$(whoami)" "$LOG_FILE"

configure_uart_for_pi
configure_networking
install_dependencies
stop_services
create_user
install_dmrgateway
install_mmdvmhost
run_python_installer
start_services

say "Setup complete. You may reboot if desired."
echo -e "\nTo start services manually:\n  systemctl restart dmrgateway.service\n  systemctl restart mmdvmhost.service" | tee -a "$LOG_FILE"
