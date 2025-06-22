# DMR Repeater System Setup

This project automates the installation and configuration of a DMR repeater, hotspot, or HBLink3+Parrot server on a Raspberry Pi or VPS for a system with local talkgroups and a Brandmeister link.

---

## Supported Install Targets

1. **Repeater** – Runs DMRGateway and MMDVMHost (e.g., Pi-Star replacement)
2. **Hotspot** – Uses WPSD + DMRGateway
3. **VPS** – Runs HBLink3 + Parrot server

---

## Quick Start (Repeater Install)

1. Flash Raspberry Pi OS (Lite) to an SD card
2. Boot your Pi and log in via SSH
3. Run the following:

```bash
curl -O https://raw.githubusercontent.com/livitup/n3ocq-dmr-repeater/main/bootstrap_pi_repeater.sh
chmod +x bootstrap.sh
./bootstrap.sh
```

This will:
- Prompt for networking setup (DHCP, Static, Wi-Fi)
- Install dependencies and DMRGateway
- Clone the GitHub repo
- Run `install.py` with role = repeater

## Automated Installation
You can bypass prompts by providing a config file: /etc/dmr/setup.cfg  No additional command line arguments are required, this file will be used if it exists, otherwise the script will prompt for inputs.

### Example `setup.cfg`
```ini
[DEFAULT]
REPEATER_ID = <Your Brandmeister Assigned Repeater ID>
BM_PASSWORD = <Your Brandmeister Password>
HBLINK_IP = <IP Address of your HBLINK server>
```
---

## ⚙️ Using Config Files

You can bypass prompts by providing a config file using the `--config` flag.




### Run with Config:
```bash
python3 install.py --role hotspot --config hotspot.cfg
```

If a config file is passed in, the script:
- Suppresses prompts
- Substitutes values into templates automatically
- Backs up existing system files
---

## 🖥 VPS Install

On a fresh VPS:
```bash
git clone https://github.com/livitup/n3ocq-dmr-repeater.git
cd n3ocq-dmr-repeater
sudo python3 install.py --role vps
```

This will:
- Clone and install HBLink3
- Set up virtual environment
- Deploy config files and systemd services
- Start HBLink3 and Parrot

## Automated Installation
You can bypass prompts by providing a config file.
To use a config file:
```bash
sudo python3 install.py --role vps --config vps.cfg
```
### `vps.cfg`
```ini
[DEFAULT]
REPEATER_ID = <Your Brandmeister Assigned Repeater ID>
HOTSPOT_ID = <Your assigned Brandmeister Hotspot ID>
BM_PASSWORD = <Your Brandmeister Password>
PARROT_ID = <Talkgroup for the local Parrot Server>
```


---

## 📶 Hotspot (WPSD)

On a device running WPSD:
```bash
git clone https://github.com/livitup/n3ocq-dmr-repeater.git
cd n3ocq-dmr-repeater
sudo python3 install.py --role hotspot
```

This installs DMRGateway and applies appropriate config templates.

To use a config file:
```bash
sudo python3 install.py --role hotspot --config hotspot.cfg
```
### `hotspot.cfg`
```ini
[DEFAULT]
HOTSPOT_ID = <Your Brandmeister Hotspot ID>
BM_PASSWORD = <Your Brandmeister Password>
HBLINK_IP = <IP/Hostname of your HBLink Server>
```
---

## Tips

- All generated config files are backed up with timestamps before overwrite
- Logs are stored in `/var/log/bootstrap.log`
- You can safely rerun the script with an updated config file to redeploy
- `.cfg` files allow non-interactive automated installs (see example above)

---

## 🔎 Operational Notes

- `.cfg` files can be used for non-interactive installs
- `install.py` and `bootstrap.sh` both accept `--config filename.cfg`
- `install.py` also accepts `--role` via CLI with values:
  - `repeater`
  - `hotspot`
  - `vps`
- Systemd services installed and started:
  - **Repeater**: `dmrgateway`
  - **Hotspot**: `dmrgateway`
  - **VPS**: `hblink3`, `parrot`
- Config file overwrites create a `.bak.YYYYMMDD-HHMMSS` backup
- Networking setup is selectable during bootstrap:
  - Wired (DHCP or static)
  - Wi-Fi (SSID + password)

---

## 📁 Repo Structure

```
.
├── bootstrap.sh
├── install.py
├── templates/
│   ├── hblink.cfg.template
│   ├── parrot.cfg.template
│   ├── dmrgateway.service.template
│   └── ...
├── operations.md
├── README.md
└── *.cfg  # Example config files for each install type
```

---

For issues or contributions, visit: https://github.com/livitup/n3ocq-dmr-repeater
