# HBLink3 Deployment Operator Field Guide

---

## 1️⃣ VPS (HBLink3 + Parrot)

| Task | Command |
|------|---------|
| Check service status | `systemctl status hblink3.service parrot.service` |
| Start/stop services | `systemctl start|stop hblink3.service` |
| View real-time logs | `journalctl -u hblink3.service -f` |
| Full log files | `/var/log/hblink/hblink.log` |
| Update HBLink3 code (if desired) | Pull repo + re-run `install-hblink3.sh` |
| Backup config | Commit changes to your GitHub repo |

---

## 2️⃣ Repeater Pi-Star (STM32-DVM)

| Task | Command |
|------|---------|
| Check DMRGateway status | `systemctl status dmrgateway.service` |
| Start/stop DMRGateway | `systemctl start|stop dmrgateway.service` |
| View DMRGateway logs | `journalctl -u dmrgateway.service -f` |
| Do not edit DMRGateway in Pi-Star UI | ✅ Leave this alone |
| Avoid Pi-Star "hostfiles update" | ✅ Don’t use |
| MMDVMHost changes | Update `/etc/mmdvmhost` directly (via repo files) |

---

## 3️⃣ Hotspot WPSD

| Task | Command |
|------|---------|
| Check DMRGateway status | `systemctl status dmrgateway.service` |
| Start/stop DMRGateway | `systemctl start|stop dmrgateway.service` |
| View DMRGateway logs | `journalctl -u dmrgateway.service -f` |
| Config files identical to repeater | ✅ Same repo files used |
| WPSD Web UI | ✅ May still function for other tasks |

---

## 4️⃣ BrandMeister Integration

- BM password is stored in your `dmrgateway_*.ini` files.
- If BM rotates your API password, update both repeater and hotspot configs and commit back to GitHub.
- If BM master IP changes → update `Address=` in config.

---

## 5️⃣ GitOps Rule

- ✅ **All config changes happen in Git.**
- ✅ Clone repo → edit files → commit → deploy using install scripts.
- ✅ Zero risk of config drift across servers.

---

## 6️⃣ Security Checklist (VPS)

| Task | Recommendation |
|------|-----------------|
| Limit SSH to key auth only | ✅ Strongly recommended |
| Use Fail2Ban | ✅ Recommended |
| Use ufw/iptables to limit HBLink3 to known repeater IPs | ✅ Great practice |
| Monitor systemd logs routinely | ✅ journalctl |

---

## Daily Summary:

- **Pi-Star:** Don't touch DMRGateway in dashboard — systemd controls it.
- **WPSD:** Fully systemd native.
- **VPS:** HBLink3 + Parrot fully isolated, controlled, and hardened.

---

## Future-Proof Notes

- This repo design will scale if you add more repeaters or hotspots.
- HBLink3 Master can easily handle multiple peers.
- DMRGateway gives you full multi-network flexibility.
- You can integrate HBMon3 dashboard easily later if you want full visual network monitor.
