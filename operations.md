# HBLink3 Deployment Operator Field Guide

---

## 🔧 VPS (HBLink3 + Parrot)

| Task | Command |
|------|---------|
| Check service status | `systemctl status hblink3.service parrot.service` |
| Start/stop services | `systemctl start|stop hblink3.service` |
| View logs | `journalctl -u hblink3.service -f` |
| Full log file | `/var/log/hblink/hblink.log` |
| Reload config | `systemctl restart hblink3.service` |
| Config files | `/opt/hblink/hblink.cfg`, `parrot.cfg` |
| Update config | Edit template → regenerate or push manually |
| Manage repo | Git commit all changes for backup/versioning |

---

## 🔧 Repeater (Pi-Star w/ STM32-DVM)

| Task | Command |
|------|---------|
| Check DMRGateway | `systemctl status dmrgateway.service` |
| View logs | `journalctl -u dmrgateway.service -f` |
| Config files | `/etc/dmrgateway/config.ini`, `/etc/mmdvmhost/config.ini` |
| Restart DMRGateway | `systemctl restart dmrgateway.service` |
| **Don't** use Pi-Star dashboard for DMRGateway | ✅ Prevents config override |
| Update | Use updated templates + re-run installer or deploy manually |

---

## 🔧 Hotspot (WPSD)

| Task | Command |
|------|---------|
| Check DMRGateway | `systemctl status dmrgateway.service` |
| View logs | `journalctl -u dmrgateway.service -f` |
| Config files | `/etc/dmrgateway/config.ini`, `/etc/mmdvmhost/config.ini` |
| Restart DMRGateway | `systemctl restart dmrgateway.service` |
| Web UI | WPSD does not override systemd-controlled DMRGateway |
| Update | Use templates or re-run `install.py` with correct role |

---

## 📡 Talkgroup Routing Notes

- Use **TG 9999** for the Parrot server (or the Parrot ID you specified)
- Routing is handled by:
  - Your **radio codeplug** (where you transmit TG 9999)
  - HBLink3's **peer list** and **TG mapping**
- Repeater/Hotspot only need to pass the traffic to HBLink3; they do **not** need to know the Parrot ID
- Other talkgroups can be routed by TGRewrite and HBLink3 rules

---

## 🔒 Security Tips

| Task | Recommendation |
|------|----------------|
| SSH Access | Use key auth only, disable password login |
| Firewall | Lock HBLink3 UDP port to repeater IPs |
| Fail2Ban | Recommended on VPS |
| Monitor logs | Use `journalctl -u <service>` for real-time logs |
| Backup | Commit to GitHub regularly after config changes |

---

## 🧠 Best Practices

- Keep **template files** as your master configs
- Never manually edit live configs without also updating the repo
- Commit and push changes after any deployment

---

✅ For questions or further automation, run `install.py` again!

