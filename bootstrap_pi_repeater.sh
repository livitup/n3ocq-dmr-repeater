#!/usr/bin/env python3

from pathlib import Path
import os
import shutil
import subprocess
import sys
import configparser
from datetime import datetime
from string import Template

# === Constants ===
TEMPLATE_DIR = "templates"
OUTPUT_DIR = "/etc"
BACKUP_SUFFIX = datetime.now().strftime("%Y%m%d%H%M%S")
CONFIG_KEYS = {
    "repeater": ["REPEATER_ID", "BM_PASSWORD", "HBLINK_IP"],
    "hotspot": ["HOTSPOT_ID", "BM_PASSWORD", "HBLINK_IP"],
    "vps": ["REPEATER_ID", "HOTSPOT_ID", "BM_PASSWORD", "PARROT_ID"],
}

# === Helper Functions ===

def say(msg):
    print(f"\033[1;34m[INSTALL]\033[0m {msg}")

def render_template(template_name, output_path, context):
    with open(Path(TEMPLATE_DIR) / template_name, "r") as f:
        src = Template(f.read())
        result = src.safe_substitute(context)

    # Backup existing file if present
    if os.path.exists(output_path):
        backup_path = f"{output_path}.{BACKUP_SUFFIX}.bak"
        shutil.copy2(output_path, backup_path)
        say(f"Backed up existing {output_path} to {backup_path}")

    with open(output_path, "w") as f:
        f.write(result)
        say(f"Wrote rendered config to {output_path}")

def ensure_root():
    if os.geteuid() != 0:
        say("This script must be run as root.")
        sys.exit(1)

def load_config(config_path):
    config = configparser.ConfigParser()
    config.read(config_path)
    return config["DEFAULT"]

def install_repeater(cfg):
    context = {
        "REPEATER_ID": cfg.get("REPEATER_ID", ""),
        "BM_PASSWORD": cfg.get("BM_PASSWORD", ""),
        "HBLINK_IP": cfg.get("HBLINK_IP", "")
    }

    say("Rendering DMRGateway config...")
    render_template("dmrgateway_repeater.ini.template", "/etc/DMRGateway.ini", context)

    say("Creating systemd service for DMRGateway...")
    shutil.copy2("services/dmrgateway.service", "/etc/systemd/system/dmrgateway.service")
    subprocess.run(["systemctl", "daemon-reexec"], check=True)
    subprocess.run(["systemctl", "enable", "dmrgateway.service"], check=True)
    subprocess.run(["systemctl", "restart", "dmrgateway.service"], check=True)

def install_hotspot(cfg):
    context = {
        "HOTSPOT_ID": cfg.get("HOTSPOT_ID", ""),
        "BM_PASSWORD": cfg.get("BM_PASSWORD", ""),
        "HBLINK_IP": cfg.get("HBLINK_IP", "")
    }

    say("Rendering DMRGateway config...")
    render_template("dmrgateway_hotspot.ini.template", "/etc/DMRGateway.ini", context)

    say("Creating systemd service for DMRGateway...")
    shutil.copy2("services/dmrgateway.service", "/etc/systemd/system/dmrgateway.service")
    subprocess.run(["systemctl", "daemon-reexec"], check=True)
    subprocess.run(["systemctl", "enable", "dmrgateway.service"], check=True)
    subprocess.run(["systemctl", "restart", "dmrgateway.service"], check=True)

def install_vps(cfg):
    context = {
        "REPEATER_ID": cfg.get("REPEATER_ID", ""),
        "HOTSPOT_ID": cfg.get("HOTSPOT_ID", ""),
        "BM_PASSWORD": cfg.get("BM_PASSWORD", ""),
        "PARROT_ID": cfg.get("PARROT_ID", "")
    }

    say("Rendering HBLink and Parrot configs...")
    render_template("hblink.cfg.template", "/opt/hblink/hblink.cfg", context)
    render_template("parrot.cfg.template", "/opt/hblink/parrot.cfg", context)

    say("Installing systemd services for VPS (hblink3/parrot)...")
    shutil.copy2("services/hblink3.service", "/etc/systemd/system/hblink3.service")
    shutil.copy2("services/parrot.service", "/etc/systemd/system/parrot.service")

    subprocess.run(["systemctl", "daemon-reexec"], check=True)
    subprocess.run(["systemctl", "enable", "hblink3.service"], check=True)
    subprocess.run(["systemctl", "enable", "parrot.service"], check=True)
    subprocess.run(["systemctl", "restart", "hblink3.service"], check=True)
    subprocess.run(["systemctl", "restart", "parrot.service"], check=True)

# === Main Entry ===

def main():
    ensure_root()

    # Detect mode
    role = None
    cfg_file = None

    if "--role" in sys.argv:
        role_index = sys.argv.index("--role") + 1
        role = sys.argv[role_index].lower()

    if "--config" in sys.argv:
        config_index = sys.argv.index("--config") + 1
        cfg_file = sys.argv[config_index]

    if not role:
        print("Select system role:\n  1) Repeater\n  2) Hotspot\n  3) VPS")
        choice = input("Enter choice [1-3]: ").strip()
        role = { "1": "repeater", "2": "hotspot", "3": "vps" }.get(choice, "repeater")

    if not cfg_file:
        cfg_file = input(f"Enter path to config file for {role} (leave blank to skip): ").strip() or None

    if cfg_file:
        say(f"Loading config file: {cfg_file}")
        cfg = load_config(cfg_file)
    else:
        cfg = {}

    say(f"Installing for role: {role}")

    if role == "repeater":
        install_repeater(cfg)
    elif role == "hotspot":
        install_hotspot(cfg)
    elif role == "vps":
        install_vps(cfg)
    else:
        say(f"Unknown role: {role}")
        sys.exit(1)

    say("✅ Install complete.")

if __name__ == "__main__":
    main()
