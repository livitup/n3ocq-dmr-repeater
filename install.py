#!/usr/bin/env python3

import os
import shutil

# Prompt user for install type
print("==== HBLink3 Unified Installer ====")
print("Select install target:")
print("  1) VPS (HBLink3 + Parrot)")
print("  2) Repeater Pi-Star")
print("  3) Hotspot WPSD")

target = input("Enter 1, 2 or 3: ").strip()

# Common prompts
hblink_ip = input("Enter HBLink3 VPS IP address: ").strip()
bm_password = input("Enter BrandMeister password: ").strip()

# Ask for DMR IDs
repeater_id = input("Enter Repeater DMR ID [314601]: ").strip() or "314601"
hotspot_id = input("Enter Hotspot DMR ID [319280601]: ").strip() or "319280601"
parrot_id = input("Enter Parrot DMR ID [9999]: ").strip() or "9999"

# Template substitutions
subs = {
    "{{HBLINK_IP}}": hblink_ip,
    "{{BM_PASSWORD}}": bm_password,
    "{{REPEATER_ID}}": repeater_id,
    "{{HOTSPOT_ID}}": hotspot_id,
    "{{PARROT_ID}}": parrot_id
}

# Output folder map
if target == "1":
    config_targets = [
        ("hblink.cfg.template", "/opt/hblink/hblink.cfg"),
        ("parrot.cfg.template", "/opt/hblink/parrot.cfg"),
        ("hblink3.service.template", "/etc/systemd/system/hblink3.service"),
        ("parrot.service.template", "/etc/systemd/system/parrot.service")
    ]
elif target == "2":
    config_targets = [
        ("mmdvmhost_repeater.ini.template", "/etc/mmdvmhost"),
        ("dmrgateway_repeater.ini.template", "/etc/dmrgateway"),
        ("dmrgateway.service.template", "/etc/systemd/system/dmrgateway.service")
    ]
elif target == "3":
    config_targets = [
        ("mmdvmhost_hotspot.ini.template", "/etc/mmdvmhost"),
        ("dmrgateway_hotspot.ini.template", "/etc/dmrgateway"),
        ("dmrgateway.service.template", "/etc/systemd/system/dmrgateway.service")
    ]
else:
    print("Invalid option!")
    exit(1)

# Generate configs
for template_file, output_file in config_targets:
    with open(f"templates/{template_file}", "r") as f:
        content = f.read()
        for k, v in subs.items():
            content = content.replace(k, v)
    with open(output_file, "w") as f:
        f.write(content)
    print(f"Deployed {output_file}")

# Reload systemd if needed
os.system("systemctl daemon-reload")

if target == "1":
    os.system("systemctl enable hblink3.service")
    os.system("systemctl enable parrot.service")
elif target in ("2", "3"):
    os.system("systemctl enable dmrgateway.service")

print("==== Install complete ====")
