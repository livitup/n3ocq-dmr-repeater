#!/usr/bin/env python3
import os
import socket
import shutil
import datetime

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

print("What are you installing?")
print("  1) VPS (HBLink3 + Parrot)")
print("  2) Repeater (Pi-Star)")
print("  3) Hotspot (WPSD)")

role_map = {
    "1": "vps",
    "2": "repeater",
    "3": "hotspot"
}

role = ""
while role not in role_map:
    role = input("Enter the number for your system type (1-3): ").strip()

role = role_map[role]

hblink_ip = prompt("Enter the VPS HBLink3 server IP address", get_primary_ip())

subs = {
    "{{HBLINK_IP}}": hblink_ip,
    "{{BM_PASSWORD}}": "",
    "{{REPEATER_ID}}": "",
    "{{HOTSPOT_ID}}": "",
    "{{PARROT_ID}}": ""
}

if role == "vps":
    subs["{{PARROT_ID}}"] = prompt("Enter the Parrot Server DMR ID", "9999")
    subs["{{REPEATER_ID}}"] = prompt("Enter the DMR ID of the repeater peer connecting to HBLink3", "314601")

elif role == "repeater":
    subs["{{REPEATER_ID}}"] = prompt("Enter the Repeater DMR ID", "314601")
    subs["{{BM_PASSWORD}}"] = prompt("Enter BrandMeister password", "passw0rd")

elif role == "hotspot":
    subs["{{HOTSPOT_ID}}"] = prompt("Enter the Hotspot DMR ID", "319280601")
    subs["{{BM_PASSWORD}}"] = prompt("Enter BrandMeister password", "passw0rd")

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

for template_file, output_path in config_targets:
    with open(f"templates/{template_file}", "r") as f:
        content = f.read()
        for k, v in subs.items():
            content = content.replace(k, v)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if output_path.endswith("/"):
        output_path = os.path.join(output_path, "config.ini")

    # Backup if file exists
    if os.path.exists(output_path):
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_path = f"{output_path}.bak.{timestamp}"
        shutil.copy2(output_path, backup_path)
        print(f"⚠️  Backed up existing {output_path} → {backup_path}")

    with open(output_path, "w") as f:
        f.write(content)
    print(f"✅ Deployed {output_path}")

# Enable services
os.system("systemctl daemon-reload")
if role == "vps":
    os.system("systemctl enable hblink3.service")
    os.system("systemctl enable parrot.service")
else:
    os.system("systemctl enable dmrgateway.service")

print("\n✅ Installation complete.")
print("🚀 You can now start the services or reboot the device.")

