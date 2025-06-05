# HBLink3 Configuration & Deployment

This repository contains a hardened, production-grade HBLink3 configuration and deployment files.

---

## Folder Structure

- `config/hblink.cfg` — main HBLink3 configuration
- `systemd/hblink3.service` — systemd unit file for automatic service management
- `logs/` — log files directory (ignored by Git)
- `runtime/` — runtime temporary files (ignored by Git)

---

## Installation

### 1️⃣ Clone repo to your server:

```bash
git clone https://github.com/your-username/hblink3-config.git ~/hblink3-config
cd ~/hblink3-config
chmod +x install-hblink3.sh
./install-hblink3.sh

