#!/usr/bin/env python3
"""
CCC Extended Configuration System
=================================
Implements the requested config command structure:
- ccc config show - Detailed configuration display
- ccc config [mode] - Show active mode (2 lines)
- ccc config [mode] dev|pip|apt - Switch mode
- ccc config -- set eMail=... - Set email configuration
"""

import json
from pathlib import Path
from datetime import datetime

class CCCConfigExtended:
    """Extended configuration management for CCC"""

    def __init__(self, config_manager):
        self.manager = config_manager
        self.config_file = Path.home() / ".config" / "ccc" / "config.json"

    def show_detailed_config(self):
        """Show detailed configuration (ccc config show)"""
        config = self.manager.config

        print("📋 CCC DETAILED CONFIGURATION")
        print("=" * 60)

        # Basic Info
        print(f"📁 Config File: {self.config_file}")
        print(f"📧 Email: {config.get('email', 'Not configured')}")
        print(f"🔧 Log Level: {config.get('log_level', 'INFO')}")

        # Mode Management
        version_mgmt = config.get("version_management", {})
        preferred_mode = version_mgmt.get("preferred_mode", "auto")
        print(f"🎯 Preferred Mode: {preferred_mode}")

        print("\n📦 AVAILABLE MODES:")
        available_modes = version_mgmt.get("available_modes", {})
        for mode_name, path in available_modes.items():
            exists = "✅" if Path(path).exists() else "❌"
            active = "🔥" if mode_name == preferred_mode else "  "
            print(f"  {active} {mode_name:8} → {path} {exists}")

        # Services
        print("\n🚀 SERVICES:")
        services = config.get("services", {})
        for service_name, service_config in services.items():
            enabled = "✅" if service_config.get("enabled", False) else "❌"
            print(f"  {enabled} {service_name}")

            if service_name == "autoinput":
                interval = service_config.get("interval", 60)
                text = service_config.get("current_text", "N/A")
                print(f"      Interval: {interval}s, Text: '{text[:30]}...'")

            elif service_name == "save":
                log_file = service_config.get("log_file", "N/A")
                with_dialog = service_config.get("with_dialog", False)
                print(f"      Log: {Path(log_file).name if log_file != 'N/A' else 'N/A'}")
                print(f"      Dialog: {'Yes' if with_dialog else 'No'}")

        # PPA Management (if exists)
        if "ppa_management" in config:
            ppa = config["ppa_management"]
            print(f"\n📦 PPA MANAGEMENT:")
            print(f"  Enabled: {'✅' if ppa.get('enabled', False) else '❌'}")
            print(f"  Target: {ppa.get('target_ppa', 'N/A')}")

            packages = ppa.get("auto_upload_packages", [])
            print(f"  Packages: {len(packages)} configured")

        print("\n" + "=" * 60)
        return 0

    def show_mode_status(self):
        """Show current mode in 2 lines (ccc config or ccc config mode)"""
        preferred_mode = self.manager.get_preferred_ccc_mode()

        # Use preferred mode as the "current" mode
        if preferred_mode:
            mode_path = self.manager.get_mode_executable(preferred_mode)
            print(f"🔧 Current Mode: {preferred_mode.upper()}")
            print(f"📁 Path: {mode_path}")
        else:
            # Fallback to PATH-based detection only if no preference set
            current_path = self.manager.get_current_ccc_path()
            current_mode = self.manager.detect_ccc_mode(current_path)
            print(f"🔧 Current Mode: {current_mode.upper()}")
            print(f"📁 Path: {current_path}")

        # Show available modes briefly (no newline to save space)
        print(f"Verfügbare Modes: DEV, PIP, APT (ccc config dev|pip|apt)")

        return 0

    def set_mode(self, new_mode):
        """Set mode (ccc config mode dev|pip|apt)"""
        valid_modes = ["dev", "pip", "apt", "pipx"]

        if new_mode not in valid_modes:
            print(f"❌ Invalid mode: {new_mode}")
            print(f"Valid modes: {', '.join(valid_modes)}")
            return 1

        try:
            old_mode = self.manager.get_preferred_ccc_mode()

            # Special handling for pipx -> pip conversion
            if new_mode == "pip":
                new_mode = "pipx"  # Internal storage uses pipx

            self.manager.set_preferred_ccc_mode(new_mode)

            print(f"✅ Preferred mode set to: {new_mode.upper()}")
            print(f"💡 Note: This preference will be used for mode detection")

            # Show path info
            mode_path = self.manager.get_mode_executable(new_mode)
            if mode_path and Path(mode_path).exists():
                print(f"📁 Mode path: {mode_path}")
            else:
                print(f"⚠️  Warning: {new_mode} mode not available")

            return 0

        except Exception as e:
            print(f"❌ Failed to set mode: {e}")
            return 1

    def set_email(self, email):
        """Set email configuration (ccc config -- set eMail=...)"""
        try:
            # Load current config
            config = self.manager.config.copy()

            # Set email
            config["email"] = email

            # Save config
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)

            # Update manager's config
            self.manager.config["email"] = email

            print(f"✅ Email set to: {email}")
            print(f"📁 Config saved to: {self.config_file}")

            return 0

        except Exception as e:
            print(f"❌ Failed to set email: {e}")
            return 1

    def handle_config_command(self, args):
        """
        Main handler for config commands

        Args format:
        - [] → show mode status (2 lines)
        - ["show"] → detailed config
        - ["mode"] → show mode status (2 lines)
        - ["mode", "dev"] → set mode to dev
        - ["--", "set", "eMail=user@example.com"] → set email
        """

        if not args:
            # ccc config → show mode status
            return self.show_mode_status()

        if args[0] == "show":
            # ccc config show → detailed config
            return self.show_detailed_config()

        if args[0] == "mode":
            if len(args) == 1:
                # ccc config mode → show mode status
                return self.show_mode_status()
            else:
                # ccc config mode dev → set mode
                return self.set_mode(args[1])

        if args[0] == "--" and len(args) >= 3 and args[1] == "set":
            # ccc config -- set eMail=...
            setting = args[2]
            if "=" in setting:
                key, value = setting.split("=", 1)
                if key.lower() in ["email", "e-mail", "eMail"]:
                    return self.set_email(value)
                else:
                    print(f"❌ Unknown config key: {key}")
                    print("Available keys: eMail")
                    return 1
            else:
                print("❌ Invalid format. Use: ccc config -- set eMail=your@email.com")
                return 1

        # Direct mode setting (ccc config dev)
        if args[0] in ["dev", "pip", "apt", "pipx"]:
            return self.set_mode(args[0])

        print(f"❌ Unknown config command: {' '.join(args)}")
        print("Available commands:")
        print("  ccc config              # Show mode status")
        print("  ccc config show         # Show detailed config")
        print("  ccc config mode         # Show mode status")
        print("  ccc config mode dev     # Set mode")
        print("  ccc config -- set eMail=user@example.com")
        return 1


def extend_config_commands(ccc_commands_instance):
    """Extend CCCCommands with new config functionality"""

    extended = CCCConfigExtended(ccc_commands_instance.manager)

    def new_config_method(self, *args):
        """Enhanced config method with full functionality"""
        return extended.handle_config_command(list(args))

    # Replace the config method
    ccc_commands_instance.config_extended = new_config_method.__get__(ccc_commands_instance)

    return extended

if __name__ == "__main__":
    # Test the config system
    print("CCC Extended Config Test")
    print("=" * 40)

    # This would need a real config manager for full testing
    print("Test commands:")
    print("  ccc config")
    print("  ccc config show")
    print("  ccc config mode")
    print("  ccc config mode dev")
    print("  ccc config -- set eMail=test@example.com")