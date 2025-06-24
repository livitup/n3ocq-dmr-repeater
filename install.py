#!/usr/bin/env python3

import os
import sys
import shutil
import configparser
import subprocess
import serial.tools.list_ports
from pathlib import Path
from datetime import datetime
from string import Template

SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = SCRIPT_DIR / "templates"

def autodetect_modem_port():
    # Step 1: Try USB-based devices first (what list_ports finds)
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        desc = port.description.lower()
        if "mmdvm" in desc or "usb" in desc or "ttyacm" in port.device.lower():
            return port.device

    # Step 2: Fallback scan for likely physical UART ports
    common_uart_ports = [
        "/dev/ttyAMA0",
        "/dev/ttyAMA1",
        "/dev/ttyS0",
        "/dev/serial0",
        "/dev/serial1"
    ]

    for dev in common_uart_ports:
        if Path(dev).exists():
            return dev

    # Step 3: Absolute fallback
    return "/dev/ttyAMA0"


def log(msg):
    print(f"\033[1;32m[INSTALL]\033[0m {msg}")

def load_config(path):
    log(f"Loading config file: {path}")
    config = configparser.ConfigParser()
    config.read(path)
    return config['DEFAULT']

def render_template(template_name, output_path, context):
    template_path = TEMPLATE_DIR / template_name
    if not template_path.exists():
        raise FileNotFoundError(f"Missing template: {template_path}")

    with open(template_path, "r") as f:
        content = Template(f.read()).safe_substitute(context)

    output_path = Path(output_path)
    if output_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = output_path.with_suffix(f".bak_{timestamp}")
        shutil.copy(output_path, backup_path)
        log(f"Backed up existing file to {backup_path}")

    with open(output_path, "w") as f:
        f.write(content)

    log(f"Wrote rendered file: {output_path}")

def install_repeater(cfg):
    log("Installing for role: repeater")

    log("Stopping any running services...")
    subprocess.run(["systemctl", "stop", "mmdvmhost.service"], check=False)
    subprocess.run(["systemctl", "stop", "dmrgateway.service"], check=False)

    modem_port = cfg.get("MODEM_PORT", autodetect_modem_port())
    log(f"Autodetected MODEM_PORT: {modem_port}")

    context = {
        "REPEATER_ID": cfg.get("REPEATER_ID", ""),
        "BM_PASSWORD": cfg.get("BM_PASSWORD", ""),
        "HBLINK_IP": cfg.get("HBLINK_IP", ""),
        "MODEM_PORT": modem_port
    }

    log("Rendering systemd services...")
    render_template("dmrgateway.service.template", "/etc/systemd/system/dmrgateway.service", context)
    render_template("mmdvmhost.service.template", "/etc/systemd/system/mmdvmhost.service", context)
    render_template("dmrgateway_repeater.ini.template", "/etc/DMRGateway.ini", context)
    render_template("mmdvmhost_repeater.ini.template", "/etc/MMDVM.ini", context)

    log("Starting services...")
    subprocess.run(["systemctl", "daemon-reload"], check=True)
    subprocess.run(["systemctl", "enable", "mmdvmhost.service"], check=True)
    subprocess.run(["systemctl", "restart", "mmdvmhost.service"], check=True)
    subprocess.run(["systemctl", "enable", "dmrgateway.service"], check=True)
    subprocess.run(["systemctl", "restart", "dmrgateway.service"], check=True)

def install_hotspot(cfg):
    log("Installing for role: hotspot")

    log("Stopping any running services...")
    subprocess.run(["systemctl", "stop", "mmdvmhost.service"], check=False)
    subprocess.run(["systemctl", "stop", "dmrgateway.service"], check=False)

    context = {
        "HOTSPOT_ID": cfg.get("HOTSPOT_ID", ""),
        "BM_PASSWORD": cfg.get("BM_PASSWORD", ""),
        "HBLINK_IP": cfg.get("HBLINK_IP", "")
    }

    log("Rendering DMRGateway config...")
    render_template("dmrgateway_hotspot.ini.template", "/etc/DMRGateway.ini", context)

    log("Rendering MMDVMHost config...")
    render_template("mmdvmhost_hotspot.ini.template", "/etc/MMDVM.ini", context)

    log("Rendering systemd service...")
    render_template("dmrgateway.service.template", "/etc/systemd/system/dmrgateway.service", context)
    render_template("mmdvmhost.service.template", "/etc/systemd/system/mmdvmhost.service", context)

    log("Starting services...")
    subprocess.run(["systemctl", "daemon-reload"], check=True)
    subprocess.run(["systemctl", "enable", "dmrgateway.service"], check=True)
    subprocess.run(["systemctl", "restart", "dmrgateway.service"], check=True)
    subprocess.run(["systemctl", "enable", "mmdvmhost.service"], check=True)
    subprocess.run(["systemctl", "restart", "mmdvmhost.service"], check=True)


def install_vps(cfg):
    log("Installing for role: vps")

    log("Stopping any running services...")
    subprocess.run(["systemctl", "stop", "hblink3.service"], check=False)
    subprocess.run(["systemctl", "stop", "parrot.service"], check=False)

    context = {
        "REPEATER_ID": cfg.get("REPEATER_ID", ""),
        "HOTSPOT_ID": cfg.get("HOTSPOT_ID", ""),
        "BM_PASSWORD": cfg.get("BM_PASSWORD", ""),
        "PARROT_ID": cfg.get("PARROT_ID", "")
    }

    log("Rendering HBLink config...")
    render_template("hblink.cfg.template", "/opt/hblink/hblink.cfg", context)

    log("Rendering Parrot config...")
    render_template("parrot.cfg.template", "/opt/hblink/parrot.cfg", context)

    log("Rendering systemd services...")
    render_template("hblink3.service.template", "/etc/systemd/system/hblink3.service", context)
    render_template("parrot.service.template", "/etc/systemd/system/parrot.service", context)

    log("Starting services...")
    subprocess.run(["systemctl", "daemon-reload"], check=True)
    subprocess.run(["systemctl", "enable", "hblink3.service"], check=True)
    subprocess.run(["systemctl", "restart", "hblink3.service"], check=True)
    subprocess.run(["systemctl", "enable", "parrot.service"], check=True)
    subprocess.run(["systemctl", "restart", "parrot.service"], check=True)

def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: install.py --role [repeater|hotspot|vps] [--config path_to_cfg]")
        sys.exit(0)

    role = None
    cfg_path = None
    if "--role" in sys.argv:
        role_index = sys.argv.index("--role") + 1
        if role_index < len(sys.argv):
            role = sys.argv[role_index].lower()

    if "--config" in sys.argv:
        cfg_index = sys.argv.index("--config") + 1
        if cfg_index < len(sys.argv):
            cfg_path = sys.argv[cfg_index]

    if not role:
        print("Please specify a role: repeater, hotspot, or vps")
        role = input("Enter role: ").strip().lower()

    if not cfg_path:
        cfg_path = input("Enter path to .cfg file (or leave blank): ").strip()
        if not cfg_path:
            cfg_path = None

    cfg = {}
    if cfg_path:
        cfg = load_config(cfg_path)

    if role == "repeater":
        install_repeater(cfg)
    elif role == "hotspot":
        install_hotspot(cfg)
    elif role == "vps":
        install_vps(cfg)
    else:
        log(f"Unknown role: {role}")
        sys.exit(1)

    log("Installation complete.")

if __name__ == "__main__":
    main()
