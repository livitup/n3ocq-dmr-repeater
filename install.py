#!/usr/bin/env python3
import os
import shutil
import socket

def get_primary_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def prompt(label, default=None):
    if default:
        result = input(f"{label} [{default}]: ").strip()
        return result if result else default
    return input(f"{label}: ").strip()

print("=== HBLink3 Unified Installer ===")

role = ""
while role not in ["vps", "repeater", "hotspot"]:
    role = input("Are you setting up a VPS, Repeater, or Hotspot? ").lower().strip()

hblink_ip = prompt("Enter the VPS HBLink3 server IP address", get_primary_ip())
repeater_id = prompt("Enter the Repeater DMR ID", "314601")
hotspot_id = prompt("Enter the Hotspot DMR ID", "319280601")
parrot_id = prompt("Enter the Parrot Server DMR ID", "9999")
bm_pass = prompt("Enter BrandMeister password", "passw0rd")

subs = {
    "{{REPEATER_ID}}": repeater_id,
    "{{HOTSPOT_ID}}": hotspot_id,
    "{{PARROT_ID}}": parrot_id,
    "{{BM_PASSWORD}}": bm_pass,
    "{{HBLINK_IP}}": hblink_ip,
}

# Template mapping
template_map = {
    "vps": [
        ("hblink.cfg.template", "/opt/hblink/hblink.cfg"),
        ("parrot.cfg.template", "/opt/hblink/parrot.cfg"),
        ("hblink3.service.template", "/etc/systemd/system/hblink3.service"),
        ("parrot.service.template", "/etc/systemd/system/parrot.service"),
    ],
    "repeater": [
        ("mmdvmhost_repeater.ini.template", "/etc/mmdvmhost"),
        ("dmrgateway_repeater.ini.template", "/etc/dmrgateway"),
        ("dmrgateway.service.template", "/etc/systemd/system/dmrgateway.service"),
    ],
    "hotspot": [
        ("mmdvmhost_hotspot.ini.template", "/etc/mmdvmhost"),
        ("dmrgateway_hotspot.ini.template", "/etc/dmrgateway"),
        ("dmrgateway.service.template", "/etc/systemd/system/dmrgateway.service"),
    ]
}

config_targets = template_map.get(role, [])

for template_file, output_file in config_targets:
    with open(f"templates/{template_file}", "r") as f:
        content = f.read()
        for k, v in subs.items():
            content = content.replace(k, v)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    if output_file.endswith("/"):
        # Write as 'config.ini' if it's just a folder path (e.g., /etc/mmdvmhost)
        output_file = os.path.join(output_file, "config.ini")
        
    with open(output_file, "w") as f:
        f.write(content)
    print(f"Deployed {output_file}")

# Reload and enable systemd services
os.system("systemctl daemon-reload")
if role == "vps":
    os.system("systemctl enable hblink3.service")
    os.system("systemctl enable parrot.service")
elif role in ["repeater", "hotspot"]:
    os.system("systemctl enable dmrgateway.service")

print("\n✅ Installation complete.")
print("🚀 You can now start the services or reboot the device.")

