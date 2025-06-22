# N3OCQ DMR Repeater Stack Installer

Fully automated installer for configuring **HBLink3**, **Parrot**, **DMRGateway**, and **MMDVMHost** on:

- VPS (HBLink3 + Parrot)
- Pi-Star–based repeaters
- WPSD-based hotspots

---

## 🔧 Requirements

### For All Systems
- A fresh install of the target OS (see below)
- Internet connectivity
- Root access (or `sudo` privileges)

### OS Support
- **Repeater / Hotspot**: Raspberry Pi OS (Lite recommended)
- **VPS**: Debian/Ubuntu-based distributions

---

## 🚀 1. Repeater Setup (Pi + Radio Modem)

### ✅ Prerequisites
- Fresh install of **Raspberry Pi OS Lite**
- Wired or Wi-Fi internet access
- A valid **DMR Repeater ID**
- Your **BrandMeister API password**

### 📅 Installation

1. Boot your Raspberry Pi and login
2. Run the bootstrap script:

```bash
bash <(curl -s https://raw.githubusercontent.com/livitup/n3ocq-dmr-repeater/main/bootstrap.sh)
```

3. Follow prompts for:
   - Network configuration (DHCP/static/wifi)
   - BrandMeister credentials
   - DMR ID

4. Script will:
   - Install required dependencies
   - Clone this repo
   - Install DMRGateway from source
   - Auto-configure everything
   - Enable and start `dmrgateway.service`

---

## 🛁 2. Hotspot Setup (e.g., WPSD Image)

### ✅ Prerequisites
- WPSD-based Pi image (https://www.w0chp.net/)
- A valid **DMR Hotspot ID**
- Your **BrandMeister API password**

### 📅 Installation

1. SSH into your hotspot
2. Clone this repo and run the installer:

```bash
git clone https://github.com/livitup/n3ocq-dmr-repeater.git
cd n3ocq-dmr-repeater
sudo python3 install.py --role hotspot
```

3. Follow prompts for DMR ID and password.

---

## 🌐 3. VPS Setup (HBLink3 + Parrot)

### ✅ Prerequisites
- Ubuntu 20.04+ or Debian 11+ VPS
- Root access
- Open TCP port 62030 on firewall

### 📅 Installation

1. SSH into your VPS
2. Clone and run the installer:

```bash
git clone https://github.com/livitup/n3ocq-dmr-repeater.git
cd n3ocq-dmr-repeater
sudo python3 install.py --role vps
```

3. Follow prompts:
   - VPS public IP address
   - Repeater peer DMR ID
   - Parrot TG ID (usually 9999)

4. Installer will:
   - Install dependencies
   - Clone and set up HBLink3 and Parrot
   - Deploy config files and services
   - Enable and start `hblink3.service` and `parrot.service`

---

## 📂 File Structure

```
n3ocq-dmr-repeater/
├── bootstrap.sh                  # For repeaters (Pi)
├── install.py                   # Unified installer for all roles
├── templates/                   # Templated config and service files
├── operations.md                # Operational reference
└── logs/                        # Install logs
```

---

## 🛠️ Service Management

```bash
# Restart DMRGateway (Repeater/Hotspot)
sudo systemctl restart dmrgateway

# Restart HBLink3 (VPS)
sudo systemctl restart hblink3

# Restart Parrot (VPS)
sudo systemctl restart parrot
```

---

## 📖 Advanced Usage

### Running Installer Non-Interactively

```bash
sudo python3 install.py --role repeater
```

Roles supported:
- `vps`
- `repeater`
- `hotspot`

---

## ❓ Support

For questions or issues, open an [Issue](https://github.com/livitup/n3ocq-dmr-repeater/issues) or contact N3OCQ.

---

