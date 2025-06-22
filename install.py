#!/usr/bin/env python3

import os
import sys
import shutil
import configparser
from datetime import datetime

TEMPLATES_DIR = "templates"
RUNTIME_DIR = "runtime"

def say(msg):
    print(f"\033[92m[INSTALL]\033[0m {msg}")

def backup_file(filepath):
    if os.path.exists(filepath):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = f"{filepath}.{timestamp}.bak"
        shutil.copy2(filepath, backup)
        say(f"Backed up existing file to {backup}")

def render_template(template_name, output_path, substitutions):
    with open(os.path.join(TEMPLATES_DIR, template_name), "r") as f:
        content = f.read()

    for key, value in substitutions.items():
        content = content.replace(f"{{{{ {key} }}}}", value)

    backup_file(output_path)

    with open(output_path, "w") as f:
        f.write(content)
    say(f"Rendered {output_path}")

def load_config(config_path):
    config = configparser.ConfigParser()
    config.read(config_path)
    return config["DEFAULT"]

def prompt_input(prompt, key, config=None):
    if config and key in config:
        return config[key]
    return input(prompt)

def get_subs(role, config):
    subs = {}

    if role == "repeater":
        subs["REPEATER_ID"] = prompt_input("Enter Repeater DMR ID: ", "REPEATER_ID", config)
        subs["BM_PASSWORD"] = prompt_input("Enter Brandmeister Password: ", "BM_PASSWORD", config)
        subs["HBLINK_IP"] = prompt_input("Enter HBLink Server IP: ", "HBLINK_IP", config)

    elif role == "hotspot":
        subs["HOTSPOT_ID"] = prompt_input("Enter Hotspot DMR ID: ", "HOTSPOT_ID", config)
        subs["BM_PASSWORD"] = prompt_input("Enter Brandmeister Password: ", "BM_PASSWORD", config)
        subs["HBLINK_IP"] = prompt_input("Enter HBLink Server IP: ", "HBLINK_IP", config)

    elif role == "vps":
        subs["REPEATER_ID"] = prompt_input("Enter Repeater DMR ID: ", "REPEATER_ID", config)
        subs["HOTSPOT_ID"] = prompt_input("Enter Hotspot DMR ID: ", "HOTSPOT_ID", config)
        subs["BM_PASSWORD"] = prompt_input("Enter Brandmeister Password: ", "BM_PASSWORD", config)
        subs["PARROT_ID"] = prompt_input("Enter Parrot Talkgroup ID: ", "PARROT_ID", config)
    return subs

def render_files(role, subs):
    os.makedirs(RUNTIME_DIR, exist_ok=True)

    if role == "repeater":
        render_template("dmrgateway_repeater.ini.template", "/etc/DMRGateway.ini", subs)
        render_template("mmdvmhost_repeater.ini.template", "/etc/MMDVM.ini", subs)
        render_template("dmrgateway.service.template", "/etc/systemd/system/dmrgateway.service", subs)

    elif role == "hotspot":
        render_template("dmrgateway_hotspot.ini.template", "/etc/DMRGateway.ini", subs)
        render_template("mmdvmhost_hotspot.ini.template", "/etc/MMDVM.ini", subs)
        render_template("dmrgateway.service.template", "/etc/systemd/system/dmrgateway.service", subs)

    elif role == "vps":
        render_template("hblink.cfg.template", "/opt/hblink/hblink.cfg", subs)
        render_template("parrot.config.template", "/opt/hblink/parrot.cfg", subs)
        render_template("hblink3.service.template", "/etc/systemd/system/hblink3.service", subs)
        render_template("parrot.service.template", "/etc/systemd/system/parrot.service", subs)

def main():
    role = None
    config_file = None

    # Parse CLI args
    args = sys.argv[1:]
    if "--role" in args:
        role = args[args.index("--role") + 1].lower()
    if "--config" in args:
        config_file = args[args.index("--config") + 1]

    if not role:
        print("What type of system are you setting up?")
        print("  1) Repeater")
        print("  2) Hotspot")
        print("  3) VPS (HBLink3 + Parrot)")
        choice = input("Enter number [1-3]: ")
        role = {"1": "repeater", "2": "hotspot", "3": "vps"}.get(choice, None)

    if role not in ("repeater", "hotspot", "vps"):
        say("❌ Invalid role selected. Exiting.")
        sys.exit(1)

    config = load_config(config_file) if config_file else None
    subs = get_subs(role, config)
    render_files(role, subs)

    if role == "vps":
        os.makedirs("/var/log/hblink", exist_ok=True)
        os.chdir("/opt/hblink")

        os.system("systemctl stop hblink3.service || true")
        os.system("systemctl stop parrot.service || true")
        os.system("systemctl enable hblink3.service")
        os.system("systemctl enable parrot.service")
        os.system("systemctl restart hblink3.service")
        os.system("systemctl restart parrot.service")

        if os.system("systemctl is-active --quiet hblink3.service") == 0:
            say("✅ hblink3.service is running.")
        else:
            say("❌ hblink3.service failed. Check /var/log/hblink/ for details.")

    else:
        os.system("systemctl stop dmrgateway.service || true")
        os.system("systemctl enable dmrgateway.service")
        os.system("systemctl restart dmrgateway.service")

        if os.system("systemctl is-active --quiet dmrgateway.service") == 0:
            say("✅ dmrgateway.service is running.")
        else:
            say("❌ dmrgateway.service failed. Check logs for details.")

    say("✅ Install complete.")

if __name__ == "__main__":
    main()
