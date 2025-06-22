#!/usr/bin/env python3
import os
import socket
import shutil
import datetime
import subprocess
import sys
import argparse

# === Parse command-line arguments ===
parser = argparse.ArgumentParser()
parser.add_argument("--role", choices=["vps", "repeater", "hotspot"], help="Set installation role (non-interactive)")
args = parser.parse_args()

print("=== HBLink3 Unified Installer ===")

print("What are you installing?")
print("  1) VPS (HBLink3 + Parrot)")
print("  2) Repeater (Pi-Star)")
print("  3) Hotspot (WPSD)")

hints = {
    "1": "vps",
    "2": "repeater",
    "3": "hotspot"
}

role = args.role
if not role:
    selection = ""
    while selection not in hints:
        selection = input("Enter the number for your system type (1-3): ").strip()
    role = hints[selection]

hints.clear()

print(f"Role selected: {role}")

# ==== BEGIN MAIN INSTALL LOGIC ====

def prompt(label, default=None):
    if default:
        result = input(f"{label} [{default}]: ").strip()
        return result if result else default
    return input(f"{label}: ").strip()

def apt_package_installed(pkg_name):
    try:
        subprocess.run(["dpkg", "-s", pkg_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def install_if_missing(pkg_name):
    if not apt_package_installed(pkg_name):
        print(f"📦 Installing missing dependency: {pkg_name}")
        os.system(f"apt-get update && apt-get install -y {pkg_name}")
    else:
        print(f"✅ {pkg_name} already installed.")

hblink_ip = prompt("Enter the VPS HBLink3 server IP address", socket.gethostbyname(socket.gethostname()))

subs = {
    "{{HBLINK_IP}}": hblink_ip,
    "{{BM_PASSWORD}}": "",
    "{{REPEATER_ID}}": "",
    "{{HOTSPOT_ID}}": "",
    "{{PARROT_ID}}": ""
}

if role == "vps":
    install_if_missing("git")
    install_if_missing("python3-venv")
    install_if_missing("python3-pip")

    if not os.path.exists("/opt/hblink"):
        os.system("git clone https://github.com/n0mjs710/HBlink3.git /opt/hblink")
    if not os.path.exists("/opt/hblink/venv"):
        os.system("python3 -m venv /opt/hblink/venv")
    os.system("/opt/hblink/venv/bin/pip install --upgrade pip")
    os.system("/opt/hblink/venv/bin/pip install -r /opt/hblink/requirements.txt")

    rules_path = "/opt/hblink/rules.py"
    rules_template = "# Minimal rules file\nBRIDGES = {}\nUNIT = 'N3OCQ-HBLINK'\n"
    if os.path.exists(rules_path):
        backup_path = f"{rules_path}.bak.{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
        shutil.copy2(rules_path, backup_path)
    with open(rules_path, "w") as f:
        f.write(rules_template)

    subs["{{PARROT_ID}}"] = prompt("Enter the Parrot Server DMR ID", "9999")
    subs["{{REPEATER_ID}}"] = prompt("Enter the DMR ID of the repeater peer connecting to HBLink3", "314601")

elif role == "repeater":
    subs["{{REPEATER_ID}}"] = prompt("Enter the Repeater DMR ID", "314601")
    subs["{{BM_PASSWORD}}"] = prompt("Enter BrandMeister password", "passw0rd")

elif role == "hotspot":
    subs["{{HOTSPOT_ID}}"] = prompt("Enter the Hotspot DMR ID", "319280601")
    subs["{{BM_PASSWORD}}"] = prompt("Enter BrandMeister password", "passw0rd")

# === CONFIG TEMPLATE DEPLOYMENT ===

from pathlib import Path

TEMPLATE_MAP = {
    "vps": [
        ("hblink.cfg.template", "/opt/hblink/hblink.cfg"),
        ("parrot.cfg.template", "/opt/hblink/parrot.cfg"),
        ("hblink3.service.template", "/etc/systemd/system/hblink3.service"),
        ("parrot.service.template", "/etc/systemd/system/parrot.service"),
    ],
    "repeater": [
        ("mmdvmhost_repeater.ini.template", "/etc/mmdvmhost"),
        ("dmrgateway_repeater.ini.template", "/etc/DMRGateway.ini"),
        ("dmrgateway.service.template", "/etc/systemd/system/dmrgateway.service"),
    ],
    "hotspot": [
        ("mmdvmhost_hotspot.ini.template", "/etc/mmdvmhost"),
        ("dmrgateway_hotspot.ini.template", "/etc/dmrgateway"),
        ("dmrgateway.service.template", "/etc/systemd/system/dmrgateway.service"),
    ]
}

config_targets = TEMPLATE_MAP.get(role, [])

for template_file, output_path in config_targets:
    with open(f"templates/{template_file}", "r") as f:
        content = f.read()
        for k, v in subs.items():
            content = content.replace(k, v)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if os.path.exists(output_path):
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_path = f"{output_path}.bak.{timestamp}"
        shutil.copy2(output_path, backup_path)
        print(f"⚠️  Backed up existing {output_path} → {backup_path}")

    with open(output_path, "w") as f:
        f.write(content)
    print(f"✅ Deployed {output_path}")

os.system("systemctl daemon-reload")

if role == "vps":
    os.system("systemctl enable hblink3.service")
    os.system("systemctl enable parrot.service")
    os.system("systemctl restart hblink3.service")
    os.system("systemctl restart parrot.service")
    print("✅ HBLink3 and Parrot services started.")

elif role in ("repeater", "hotspot"):
    os.system("systemctl enable dmrgateway.service")
    os.system("systemctl restart dmrgateway.service")
    print("✅ DMRGateway service started.")
    if subprocess.run(["systemctl", "is-active", "--quiet", "dmrgateway.service"]).returncode == 0:
        print("✅ DMRGateway service is running.")
    else:
        print("❌ DMRGateway failed to start. Check system logs for details.")

print("✅ Installation complete.")

