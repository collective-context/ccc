"""
CCC Manager - Core management functionality
"""

import json
import os
import subprocess
from pathlib import Path
from datetime import datetime

class CCCManager:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.config_dir = self.base_dir / "config"
        self.logs_dir = self.base_dir / "logs"
        
        # Ensure directories exist
        self.config_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
        # Configuration files
        self.config_file = self.config_dir / "config.json"
        self.state_file = self.config_dir / "state.json"
        self.control_file = self.config_dir / "control.txt"
        self.log_file = self.logs_dir / "ccc.log"
        
        # Load configuration
        self.config = self.load_config()
        self.state = self.load_state()
    
    def load_config(self):
        """Load or create configuration"""
        # Check for user config first
        user_config_dir = Path.home() / ".config" / "ccc"
        user_config_file = user_config_dir / "config.json"

        default_config = {
            "version_management": {
                "preferred_mode": "auto",  # auto, dev, pipx, apt
                "available_modes": {
                    "dev": "/usr/local/bin/ccc",
                    "pipx": str(Path.home() / ".local/bin/ccc"),
                    "apt": "/usr/bin/ccc"
                }
            },
            "services": {
                "autoinput": {
                    "enabled": False,
                    "interval": 300,
                    "default_text": "Alles okay?",
                    "current_text": "Alles okay?",
                    "target_dir": os.environ.get('CCC_PROJECT_DIR', str(Path.home() / 'prog/claude/osCASH.me')),
                    "tmux_session": "claude",
                    "last_run": None
                },
                "dialog": {
                    "enabled": False,
                    "target_dir": os.environ.get('CCC_PROJECT_DIR', str(Path.home() / 'prog/claude/osCASH.me')),
                    "tmux_session": "claude",
                    "log_file": None,
                    "last_run": None,
                    "session_id": None
                }
            },
            "log_level": "INFO"
        }
        
        # Try user config first, then local config
        config_files = [user_config_file, self.config_file]

        for config_file in config_files:
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    for key in default_config:
                        if key not in config:
                            config[key] = default_config[key]
                    # Store which config file was used
                    config['_config_source'] = str(config_file)
                    return config

        # No config found, create user config
        user_config_dir.mkdir(parents=True, exist_ok=True)
        with open(user_config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        default_config['_config_source'] = str(user_config_file)
        return default_config
    
    def save_config(self, config=None):
        """Save configuration"""
        if config:
            self.config = config
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def load_state(self):
        """Load runtime state"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_state(self):
        """Save runtime state"""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def log(self, message, level="INFO"):
        """Log message to file and console"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        
        # Console output with colors
        if level == "ERROR":
            print(f"❌ {message}")
        elif level == "SUCCESS":
            print(f"✅ {message}")
        elif level == "WARNING":
            print(f"⚠️  {message}")
        else:
            print(f"ℹ️  {message}")
        
        # File logging
        with open(self.log_file, 'a') as f:
            f.write(log_entry + "\n")
    
    def get_tmux_sessions(self):
        """Find tmux sessions in target directory"""
        try:
            result = subprocess.run(
                ["tmux", "list-sessions", "-F", "#{session_name}:#{pane_current_path}"],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode != 0:
                return []
            
            sessions = []
            target_dir = self.config["services"]["autoinput"]["target_dir"]
            for line in result.stdout.strip().split('\n'):
                if line and ':' in line:
                    session_name, path = line.split(':', 1)
                    if target_dir in path:
                        sessions.append(session_name)
            return sessions
            
        except FileNotFoundError:
            self.log("tmux not found. Please install tmux.", "ERROR")
            return []
        except Exception as e:
            self.log(f"Failed to find tmux sessions: {e}", "ERROR")
            return []
    
    def send_to_tmux(self, text, session=None):
        """Send text to tmux session"""
        if not session:
            sessions = self.get_tmux_sessions()
            if not sessions:
                self.log("No tmux sessions found", "WARNING")
                return False
        else:
            sessions = [session]
        
        # KRITISCH: Command Interceptor nach dem Lösch-Desaster
        try:
            from ccc_rule_enforcer import CommandInterceptor
            interceptor = CommandInterceptor()

            # Prüfe ob der Befehl sicher ist
            if not interceptor.safe_execute(text, "tmux-send"):
                self.log("⚠️ Command blocked by security interceptor!", "WARNING")
                return False
        except ImportError:
            pass  # Interceptor nicht verfügbar - fahre mit Vorsicht fort

        success = False
        for sess in sessions:
            try:
                # Send text
                subprocess.run(
                    ["tmux", "send-keys", "-t", sess, text],
                    timeout=5, check=True
                )
                # Send Enter
                subprocess.run(
                    ["tmux", "send-keys", "-t", sess, "Enter"],
                    timeout=5, check=True
                )
                self.log(f"Sent '{text}' to tmux session '{sess}'", "SUCCESS")
                success = True
            except subprocess.CalledProcessError as e:
                self.log(f"Failed to send to session '{sess}': {e}", "ERROR")
            except Exception as e:
                self.log(f"Unexpected error sending to '{sess}': {e}", "ERROR")
        
        return success
    
    def write_control_file(self, command):
        """Write command to control file for monitoring script"""
        try:
            with open(self.control_file, 'w') as f:
                f.write(command)
            return True
        except Exception as e:
            self.log(f"Failed to write control file: {e}", "ERROR")
            return False
    
    def read_control_file(self):
        """Read and clear control file"""
        try:
            if not self.control_file.exists():
                return None
            
            with open(self.control_file, 'r') as f:
                command = f.read().strip()
            
            # Clear file after reading
            with open(self.control_file, 'w') as f:
                f.write("")
            
            return command
        except Exception as e:
            self.log(f"Failed to read control file: {e}", "ERROR")
            return None
    
    def is_monitor_running(self):
        """Check if monitoring script is running"""
        try:
            result = subprocess.run(
                ["pgrep", "-f", "ccc_monitor.py"],
                capture_output=True, timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def start_monitor(self):
        """Start monitor script in background"""
        try:
            monitor_script = self.base_dir / "ccc_monitor.py"
            subprocess.Popen(
                ["python3", str(monitor_script)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            # Give it a moment to start
            import time
            time.sleep(1)
            return self.is_monitor_running()
        except Exception as e:
            self.log(f"Failed to start monitor: {e}", "ERROR")
            return False
    
    def stop_monitor(self):
        """Stop monitor script"""
        try:
            # Send EXIT command via control file
            self.write_control_file("EXIT")
            
            # Wait a bit for graceful shutdown
            import time
            time.sleep(2)
            
            # Force kill if still running
            result = subprocess.run(
                ["pkill", "-f", "ccc_monitor.py"],
                capture_output=True, timeout=5
            )
            
            return not self.is_monitor_running()
        except Exception as e:
            self.log(f"Failed to stop monitor: {e}", "ERROR")
            return False

    def get_preferred_ccc_mode(self):
        """Get the preferred CCC mode from config"""
        return self.config.get("version_management", {}).get("preferred_mode", "auto")

    def set_preferred_ccc_mode(self, mode):
        """Set the preferred CCC mode in config"""
        if "version_management" not in self.config:
            self.config["version_management"] = {}

        valid_modes = ["auto", "dev", "pipx", "apt"]
        if mode not in valid_modes:
            raise ValueError(f"Invalid mode: {mode}. Valid modes: {valid_modes}")

        self.config["version_management"]["preferred_mode"] = mode
        self.save_config_to_user()
        return mode

    def get_current_ccc_path(self):
        """Get the current active CCC path"""
        import subprocess
        try:
            result = subprocess.run(["which", "ccc"], capture_output=True, text=True)
            return result.stdout.strip() if result.returncode == 0 else None
        except Exception:
            return None

    def detect_ccc_mode(self, ccc_path=None):
        """Detect which CCC mode is currently active"""
        if ccc_path is None:
            ccc_path = self.get_current_ccc_path()

        if not ccc_path:
            return "none"

        if "/.local/bin/" in ccc_path or "/pipx/" in ccc_path:
            return "pipx"
        elif "/usr/local/bin/" in ccc_path:
            return "dev"
        elif "/usr/bin/" in ccc_path or "/apt/" in ccc_path:
            return "apt"
        else:
            return "unknown"

    def get_mode_executable(self, mode):
        """Get the executable path for a specific mode"""
        available_modes = self.config.get("version_management", {}).get("available_modes", {})
        return available_modes.get(mode)

    def save_config_to_user(self):
        """Save config to user's ~/.config/ccc/config.json"""
        user_config_dir = Path.home() / ".config" / "ccc"
        user_config_file = user_config_dir / "config.json"

        user_config_dir.mkdir(parents=True, exist_ok=True)

        # Remove internal fields before saving
        config_to_save = self.config.copy()
        config_to_save.pop('_config_source', None)

        with open(user_config_file, 'w') as f:
            json.dump(config_to_save, f, indent=2)

        self.log(f"Config saved to {user_config_file}", "INFO")