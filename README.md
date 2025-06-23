# DMR Repeater Setup Tools

This repository provides scripts and templates to fully set up a DMR repeater, hotspot, or VPS system with HBLink3 and Parrot, using preconfigured settings via `.cfg` files.

---

## Repository Structure

```
dmr-repeater-setup-tools/
├── bootstrap_pi_repeater.sh    # Raspberry Pi bootstrapper for repeaters
├── install.py                  # Common Python installer for all roles
├── templates/                  # Jinja-style templates for INI and service files
│   ├── dmrgateway_repeater.ini.template
│   ├── dmrgateway_hotspot.ini.template
│   ├── mmdvmhost_repeater.ini.template
│   ├── mmdvmhost_hotspot.ini.template
│   ├── hblink.cfg.template
│   ├── parrot.cfg.template
├── services/                   # systemd unit templates
│   ├── dmrgateway.service
│   ├── hblink3.service
│   ├── parrot.service
├── configs/                    # Sample config files (NOT auto-loaded)
│   ├── repeater.cfg
│   ├── hotspot.cfg
│   ├── vps.cfg
```

---

## Installation (for Pi-based Repeater)

```bash
curl -O https://raw.githubusercontent.com/YOURNAME/dmr-repeater-setup-tools/main/bootstrap_pi_repeater.sh
chmod +x bootstrap_pi_repeater.sh
sudo ./bootstrap_pi_repeater.sh --config /etc/dmr/setup.cfg
```

This will:
- Set up networking
- Install DMRGateway
- Clone the repo
- Run `install.py` with your specified config file

---

## Usage with `install.py`

```bash
sudo python3 install.py --role repeater --config repeater.cfg
sudo python3 install.py --role hotspot --config hotspot.cfg
sudo python3 install.py --role vps --config vps.cfg
```

If no `--config` file is passed, values will be requested interactively.

---

## System Roles & Required Keys

### Repeater (`repeater.cfg`)
```ini
[DEFAULT]
REPEATER_ID = 1234567
BM_PASSWORD = your_bm_password
HBLINK_IP   = 192.168.1.100
```

### Hotspot (`hotspot.cfg`)
```ini
[DEFAULT]
HOTSPOT_ID = 123456789
BM_PASSWORD = your_bm_password
HBLINK_IP   = 192.168.1.100
```

### VPS (`vps.cfg`)
```ini
[DEFAULT]
REPEATER_ID = 1234567
HOTSPOT_ID  = 123456789
BM_PASSWORD = your_bm_password
PARROT_ID   = 9999
```

---

## Debugging

### Check service status:
```bash
sudo systemctl status dmrgateway
sudo systemctl status hblink3
sudo systemctl status parrot
```

### Logs:
- DMRGateway logs to `/var/log/dmrgateway.log` (set via INI file)
- HBLink and Parrot logs to `/var/log/hblink/`

---

## Notes

- Templates are auto-rendered using `.cfg` context
- All overwritten configs are backed up with `.bak_YYYYMMDD_HHMMSS`
- Do **not** store sensitive passwords in public repos
- To re-run setup, just re-use the same `.cfg` file with updated values
