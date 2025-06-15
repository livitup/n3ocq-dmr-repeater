#!/usr/bin/env python3
import os
import socket
import shutil
import datetime
import subprocess

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
    print("\n🔧 Checking system dependencies for HBLink3...")
    install_if_missing("git")
    install_if_missing("python3-venv")
    install_if_missing("python3-pip")

    print("\n🔧 Installing HBLink3 environment at /opt/hblink")

    if not os.path.exists("/opt/hblink"):
        os.system("git clone https://github.com/n0mjs710/HBlink3.git /opt/hblink")
    else:
        print("📁 /opt/hblink already exists. Skipping clone.")

    if not os.path.exists("/opt/hblink/venv"):
        print("📦 Creating virtualenv and installing Python requirements...")
        os.system("python3 -m venv /opt/hblink/venv")
        os.system("/opt/hblink/venv/bin/pip install --upgrade pip")
        os.system("/opt/hblink/venv/bin/pip install -r /opt/hblink/requirements.txt")
    else:
        print("✅ Virtualenv already exists. Skipping dependency install.")

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

    start_now = input("Restart HBLink3 and Parrot services now? [Y/n]: ").strip().lower()
    if start_now in ("", "y", "yes"):
        os.system("systemctl restart hblink3.service")
        os.system("systemctl restart parrot.service")
        print("✅ HBLink3 and Parrot services restarted.")
    else:
        print("⏸️ Services were not restarted. You can do it manually with:")
        print("   systemctl restart hblink3.service")
        print("   systemctl restart parrot.service")

else:
    os.system("systemctl enable dmrgateway.service")

    start_now = input("Restart DMRGateway service now? [Y/n]: ").strip().lower()
    if start_now in ("", "y", "yes"):
        os.system("systemctl restart dmrgateway.service")
        print("✅ DMRGateway service restarted.")
    else:
        print("⏸️ Service was not restarted. You can do it manually with:")
        print("   systemctl restart dmrgateway.service")

print("\n✅ Installation complete.")

