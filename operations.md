# DMR System Operations Guide

This document outlines how to operate, manage, and troubleshoot the components installed by the `n3ocq-dmr-repeater` project. It applies to repeater, hotspot, and VPS-based configurations.

---

## 🚦 System Roles and Services

| Role     | Services Installed         | Components Included                  |
|----------|-----------------------------|--------------------------------------|
| Repeater | `dmrgateway.service`       | DMRGateway, MMDVMHost                |
| Hotspot  | `dmrgateway.service`       | DMRGateway (WPSD)                    |
| VPS      | `hblink3`, `parrot.service`| HBLink3 + Parrot server              |

---

## ⚙️ Config File Usage

Each system role can be installed using a `.cfg` file to provide required values non-interactively.

### Supported Keys by Role

#### Repeater (`repeater.cfg`)
```
[DEFAULT]
REPEATER_ID = 314601
BM_PASSWORD = my_secure_password
HBLINK_IP = 192.168.5.100
```

#### Hotspot (`hotspot.cfg`)
```
[DEFAULT]
HOTSPOT_ID = 319280601
BM_PASSWORD = my_secure_password
HBLINK_IP = 192.168.5.100
```

#### VPS (`vps.cfg`)
```
[DEFAULT]
REPEATER_ID = 314601
HOTSPOT_ID = 319280601
BM_PASSWORD = my_secure_password
PARROT_ID = 9999
```

### Command-Line Examples

```bash
sudo python3 install.py --role repeater --config repeater.cfg
sudo python3 install.py --role vps --config vps.cfg
./bootstrap.sh --config repeater.cfg
```

If a `.cfg` file is provided:
- Prompts are skipped
- Template variables are auto-substituted
- Existing config files are backed up with timestamped `.bak` extensions

---

## 🛠 Manual Service Control

### Repeater or Hotspot (DMRGateway)
```bash
sudo systemctl restart dmrgateway.service
sudo systemctl status dmrgateway.service
```

### VPS
```bash
sudo systemctl restart hblink3.service
sudo systemctl restart parrot.service
sudo systemctl status hblink3.service
sudo systemctl status parrot.service
```

---

## 🧪 Log Locations

| Component       | Path                     |
|----------------|--------------------------|
| Bootstrap log  | `/var/log/bootstrap.log` |
| HBLink3 logs   | `/var/log/hblink/`       |
| Parrot logs    | `/var/log/hblink/`       |

---

## 📡 Network Setup (bootstrap.sh)

On Raspberry Pi installations, the script will prompt for network config:
- Wired (DHCP)
- Wired (Static)
- Wi-Fi (SSID + password)

The script writes `/etc/dhcpcd.conf` or `/etc/wpa_supplicant/wpa_supplicant.conf` accordingly.

---

## 🧹 Cleanup & Reinstall

To rerun installation safely:
1. Update your `.cfg` with new settings
2. Rerun either `install.py` or `bootstrap.sh`
3. All modified config files are backed up before overwriting

---

## 📁 Key Directories

| Path                     | Purpose                          |
|--------------------------|----------------------------------|
| `/opt/hblink/`           | HBLink3 installation directory   |
| `/opt/hblink/venv/`      | Python virtual environment       |
| `/usr/local/bin/DMRGateway` | Compiled DMRGateway binary    |

---

## 🧩 Template Rendering

The following templates are filled during install:
- `templates/hblink.cfg.template`
- `templates/parrot.cfg.template`
- `templates/mmdvmhost_*.ini.template`
- `templates/dmrgateway_*.ini.template`

---

## 🗒 Notes

- All system services are managed via systemd
- Existing config files are backed up with timestamps
- Configuration and service start are logged
- Public repo defaults do not include personal credentials

---

For help or questions, visit https://github.com/livitup/n3ocq-dmr-repeater
