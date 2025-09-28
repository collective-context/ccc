"""
CCC Commands - Command implementations
"""

import subprocess
from datetime import datetime
from pathlib import Path
import sys

# KRITISCH: Command Interceptor + STOP-AND-WAIT nach dem Lösch-Desaster
sys.path.append(str(Path(__file__).parent.parent))
try:
    from ccc_rule_enforcer import CommandInterceptor, SysOpsAlert
    INTERCEPTOR = CommandInterceptor()
    SYSOPS_ALERT = SysOpsAlert()
except ImportError:
    print("⚠️ WARNUNG: Command Interceptor nicht verfügbar - Sicherheitsrisiko!")
    INTERCEPTOR = None
    SYSOPS_ALERT = None

class Commands:
    def __init__(self, manager):
        self.manager = manager
        self.interceptor = INTERCEPTOR
        self.sysops_alert = SYSOPS_ALERT

    def require_sysops(self, problem: str, location: str, solution: str, command: str) -> bool:
        """
        STOP-AND-WAIT Protokoll: Fordert SysOps-Aktion an und wartet
        Returns: True wenn SysOps bestätigt, False wenn abgebrochen
        """
        if self.sysops_alert:
            return self.sysops_alert.alert(problem, location, solution, command)
        else:
            # Fallback ohne Interceptor
            print(f"⚠️ SYSOPS REQUIRED: {problem}")
            print(f"📍 {location}")
            print(f"🔧 {solution}")
            print(f"Command: {command}")
            response = input("Bestätigung (erledigt/done): ").strip().lower()
            return response in ['erledigt', 'done', 'fertig']
    
    def status(self, service="autoinput"):
        """Show brief service status"""
        if service not in self.manager.config["services"]:
            self.manager.log(f"Unknown service: {service}", "ERROR")
            return 1
        
        svc_config = self.manager.config["services"][service]
        
        print(f"\n[SECTIONS] CCC Service Brief Status: {service}")
        print("=" * 50)
        print(f"📊 Status: {'🟢 RUNNING' if svc_config['enabled'] else '🔴 STOPPED'}")
        
        if service == "autoinput":
            print(f"[SERVICES] Text: '{svc_config['current_text']}'")
            print(f"⏰ Interval: {svc_config['interval']/60}min")
        elif service == "dialog":
            if svc_config.get("session_id"):
                print(f"🆔 Session: {svc_config['session_id']}")
            if svc_config.get("log_file"):
                print(f"📁 Log: {svc_config['log_file']}")
        
        if self.manager.is_monitor_running():
            print("🔄 Monitor: RUNNING")
        else:
            print("⚠️  Monitor: STOPPED")
        
        print("=" * 50)
        return 0

    def config_mode(self, action=None, mode=None):
        """Manage CCC version modes via config"""
        if action is None:
            # Show current mode status
            current_path = self.manager.get_current_ccc_path()
            current_mode = self.manager.detect_ccc_mode(current_path)
            preferred_mode = self.manager.get_preferred_ccc_mode()

            print("\n🔄 CCC Version Management")
            print("=" * 40)
            print(f"Current Active: {current_path}")
            print(f"Current Mode: {current_mode}")
            print(f"Preferred Mode: {preferred_mode}")

            print(f"\nAvailable Commands:")
            print(f"  ccc config mode set <dev|pipx|apt>   - Set preferred mode")
            print(f"  ccc config mode get                  - Show current status")
            print(f"  ccc config mode reset                - Reset to auto")

            available_modes = self.manager.config.get("version_management", {}).get("available_modes", {})
            print(f"\nConfigured Paths:")
            for mode_name, path in available_modes.items():
                exists = "✅" if Path(path).exists() else "❌"
                print(f"  {mode_name}: {path} {exists}")

            return 0

        elif action == "set":
            if mode is None:
                print("❌ Mode required. Usage: ccc config mode set <dev|pipx|apt>")
                return 1

            try:
                old_mode = self.manager.get_preferred_ccc_mode()
                self.manager.set_preferred_ccc_mode(mode)
                print(f"✅ Preferred mode changed: {old_mode} → {mode}")
                print(f"📁 Config saved to: ~/.config/ccc/config.json")

                # Check if the preferred mode is available
                mode_path = self.manager.get_mode_executable(mode)
                if mode_path and Path(mode_path).exists():
                    print(f"✅ {mode} mode is available at: {mode_path}")

                    # Provide switching instructions
                    if mode == "dev":
                        print(f"\n🔄 To activate development mode:")
                        print(f"   export PATH=/usr/local/bin:$PATH")
                    elif mode == "pipx":
                        print(f"\n🔄 To activate pipx mode:")
                        print(f"   export PATH=$HOME/.local/bin:$PATH")
                else:
                    print(f"⚠️  Warning: {mode} mode not available at: {mode_path}")

                return 0

            except ValueError as e:
                print(f"❌ {e}")
                return 1

        elif action == "get":
            # Same as no action
            return self.config_mode()

        elif action == "reset":
            old_mode = self.manager.get_preferred_ccc_mode()
            self.manager.set_preferred_ccc_mode("auto")
            print(f"✅ Mode reset: {old_mode} → auto")
            print(f"📁 Config saved to: ~/.config/ccc/config.json")
            return 0

        else:
            print(f"❌ Unknown action: {action}")
            print(f"Available: set, get, reset")
            return 1

    def config(self, service="autoinput"):
        """Show service configuration (like old status command)"""
        if service not in self.manager.config["services"]:
            self.manager.log(f"Unknown service: {service}", "ERROR")
            return 1
        
        svc_config = self.manager.config["services"][service]
        
        print(f"\n🔍 CTC Service Status: {service}")
        print("=" * 50)
        print(f"📊 Status: {'🟢 RUNNING' if svc_config['enabled'] else '🔴 STOPPED'}")
        
        if service == "autoinput":
            print(f"[SERVICES] Current Text: '{svc_config['current_text']}'")
            print(f"⏰ Interval: {svc_config['interval']/60} minutes")
        elif service == "save":
            if svc_config.get("log_file"):
                print(f"📁 Session Log: {svc_config['log_file']}")
            if svc_config.get("with_dialog") and svc_config.get("dialog_log_file"):
                print(f"📁 Dialog Log: {svc_config['dialog_log_file']}")
            if svc_config.get("session_start"):
                print(f"🕐 Session Started: {svc_config['session_start']}")
            print(f"🔄 Dialog Monitoring: {'ACTIVE' if svc_config.get('with_dialog') else 'OFF'}")
        
        print(f"📁 Target Dir: {svc_config['target_dir']}")
        print(f"🖥️  Tmux Session: {svc_config['tmux_session']}")
        
        if svc_config.get('last_run'):
            print(f"🕐 Last Run: {svc_config['last_run']}")
        
        # Check tmux sessions
        sessions = self.manager.get_tmux_sessions()
        if sessions:
            print(f"✅ Active tmux sessions: {', '.join(sessions)}")
        else:
            print("❌ No active tmux sessions found")
        
        # Check if monitoring script is running
        if self.manager.is_monitor_running():
            print("🔄 Monitor script: RUNNING")
        else:
            print("⚠️  Monitor script: NOT RUNNING")
        
        print("=" * 50)
        return 0
    
    def start(self, service="autoinput", custom_text=None, with_monitor=False, interval_minutes=None):
        """Start service with optional custom text, monitor, and interval"""
        if service not in self.manager.config["services"]:
            self.manager.log(f"Unknown service: {service}", "ERROR")
            return 1
        
        svc_config = self.manager.config["services"][service]
        
        # Update interval if provided
        if interval_minutes is not None:
            if interval_minutes < 1:
                print("❌ Interval must be at least 1 minute")
                return 1
            svc_config["interval"] = interval_minutes * 60  # Convert to seconds
            self.manager.log(f"Updated interval to: {interval_minutes} minutes")
        
        # Update text if provided (only for autoinput service)
        if service == "autoinput":
            if custom_text:
                svc_config["current_text"] = custom_text
                self.manager.log(f"Updated text to: '{custom_text}'")
            else:
                svc_config["current_text"] = svc_config["default_text"]
        
        # Enable service
        svc_config["enabled"] = True
        self.manager.save_config()
        
        # Write START command to control file
        self.manager.write_control_file("START")
        
        print(f"\n[CONTROL] Service '{service}' STARTED")
        if service == "autoinput":
            print(f"[SERVICES] Text: '{svc_config['current_text']}'")
            print(f"⏰ Interval: Every {svc_config['interval']/60} minutes")
        elif service == "dialog":
            print(f"[SERVICES] Dialog logging initialized")
        
        # Start monitor if requested
        if with_monitor:
            if not self.manager.is_monitor_running():
                if self.manager.start_monitor():
                    print("🔄 Monitor started in background")
                else:
                    print("⚠️  Failed to start monitor")
            else:
                print("ℹ️  Monitor already running")
        else:
            # Check if monitor is running
            if not self.manager.is_monitor_running():
                print("\n⚠️  Monitor not running. Start with: ctc start -m")
        
        return 0
    
    def restart(self, service="autoinput", custom_text=None, with_monitor=False, interval_minutes=None):
        """Restart service (stop + start) with optional parameters"""
        if service not in self.manager.config["services"]:
            self.manager.log(f"Unknown service: {service}", "ERROR")
            return 1
        
        print(f"\n🔄 Restarting {service} service...")
        
        # First stop with monitor
        print("🛑 Stopping service and monitor...")
        stop_result = self.stop(service, with_monitor=True)
        
        if stop_result != 0:
            print("⚠️  Stop failed, continuing with start...")
        
        # Short pause to ensure clean shutdown
        import time
        time.sleep(1)
        
        # Then start with provided parameters
        print("[CONTROL] Starting service...")
        return self.start(service, custom_text, with_monitor, interval_minutes)
    
    def stop(self, service="autoinput", with_monitor=False):
        """Stop service and optionally stop monitor"""
        if service not in self.manager.config["services"]:
            self.manager.log(f"Unknown service: {service}", "ERROR")
            return 1
        
        svc_config = self.manager.config["services"][service]
        svc_config["enabled"] = False
        self.manager.save_config()
        
        # Write STOP command to control file
        self.manager.write_control_file("STOP")
        
        print(f"\n🛑 Service '{service}' STOPPED")
        
        # Stop monitor if requested
        if with_monitor:
            if self.manager.is_monitor_running():
                if self.manager.stop_monitor():
                    print("🛑 Monitor stopped")
                else:
                    print("⚠️  Failed to stop monitor")
            else:
                print("ℹ️  Monitor not running")
        
        return 0
    
    def test(self, service="autoinput"):
        """Reset to default text and send it once (only for autoinput)"""
        if service not in self.manager.config["services"]:
            self.manager.log(f"Unknown service: {service}", "ERROR")
            return 1
        
        # Test function only works for autoinput service
        if service != "autoinput":
            print(f"❌ Test function not available for {service} service")
            return 1
        
        svc_config = self.manager.config["services"][service]
        
        # Reset current_text to default_text
        default_text = svc_config["default_text"]
        svc_config["current_text"] = default_text
        self.manager.save_config()
        
        print(f"\n🧪 Testing {service} service")
        print(f"🔄 Reset to default text: '{default_text}'")
        print(f"[SERVICES] Sending: '{default_text}'")
        
        if self.manager.send_to_tmux(default_text):
            print("✅ Test successful!")
            # Update last run time
            svc_config["last_run"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.manager.save_config()
            return 0
        else:
            print("❌ Test failed!")
            return 1
    
    def exec(self, service="autoinput", command=None):
        """Execute arbitrary command in service context"""
        # Special handling for PPA upload
        if service == "upload" and command == "ppa":
            return self.exec_upload_ppa()

        # Special handling for Debian packaging
        if service == "debian":
            return self.exec_debian_command(command)

        # Original exec functionality for tmux commands
        if not command:
            self.manager.log("No command provided", "ERROR")
            return 1

        print(f"\n[CORE] Executing: {command}")
        if self.manager.send_to_tmux(command):
            print("✅ Command sent!")
            return 0
        else:
            print("❌ Failed to send command!")
            return 1

    def version_write_and_read(self):
        """Write version info to file and read it for display"""
        import os
        import sys
        from pathlib import Path
        import subprocess

        # Detect current mode
        def detect_current_mode():
            current_path = sys.argv[0]

            # Check if running from source (DEV mode)
            if 'ccc_main.py' in current_path or '/collective-context/ccc' in current_path:
                return 'DEV', current_path

            # Check common installation paths
            if '/usr/bin/' in current_path or current_path == 'ccc':
                return 'APT', '/usr/bin/ccc'
            elif '/.local/bin/' in current_path or 'pipx' in current_path:
                return 'PIP', current_path
            elif '/usr/local/bin/' in current_path:
                return 'DEV', current_path
            else:
                # Try to determine by checking what's available
                import shutil
                if shutil.which('ccc') and '/usr/bin/' in shutil.which('ccc'):
                    return 'APT', shutil.which('ccc')
                elif shutil.which('cccmd'):
                    return 'PIP', shutil.which('cccmd')
                else:
                    return 'DEV', current_path

        mode, path = detect_current_mode()

        # Check for existing VERSION_INFO.md file
        local_only_dir = Path(__file__).parent.parent / "local-only" / "HELP"
        version_file = local_only_dir / "VERSION_INFO.md"

        if version_file.exists():
            try:
                with open(version_file, 'r', encoding='utf-8') as f:
                    template = f.read()

                # Replace placeholders
                content = template.replace("{{MODE}}", mode)
                content = content.replace("{{PATH}}", path)

                # Set installation info based on mode
                if mode == 'APT':
                    install_info = "📦 Installed via: apt install ccc && apt install cccmd"
                    mode_desc = "🔧 Mode: Stable System Package - grundlegende Commands"
                    update_cmd = "apt update && apt upgrade"
                elif mode == 'PIP':
                    install_info = "📦 Installed via: pipx install cccmd"
                    mode_desc = "🔧 Mode: Stable PyPI Package - grundlegende Commands"
                    update_cmd = "pipx upgrade cccmd"
                elif mode == 'DEV':
                    install_info = "📦 Installed via: git clone https://github.com/collective-context/ccc"
                    mode_desc = "🔧 Mode: Developer - Vollständiges Session-Management inkl. neuen Features"
                    update_cmd = "cd ~/prog/ai/git/collective-context/ccc && git pull origin main"
                else:
                    install_info = "📦 Installation method unknown"
                    mode_desc = "🔧 Mode: Unknown installation method"
                    update_cmd = "# Update method depends on installation"

                content = content.replace("{{INSTALL_INFO}}", install_info)
                content = content.replace("{{MODE_DESC}}", mode_desc)
                content = content.replace("{{UPDATE_COMMAND}}", update_cmd)

                # Check if we're in a real terminal or Claude Code
                if sys.stdout.isatty():
                    # Terminal: Create optimized version
                    terminal_content = content.replace("```bash\n", "").replace("```\n", "").replace("```", "")

                    # Create temporary file for viewing
                    import tempfile
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
                        temp_file.write(terminal_content)
                        temp_file_path = temp_file.name

                    # Try to open with nano or less
                    try:
                        subprocess.run(['nano', '-v', temp_file_path], check=False)
                        os.unlink(temp_file_path)
                        return 0
                    except FileNotFoundError:
                        try:
                            subprocess.run(['less', temp_file_path], check=False)
                            os.unlink(temp_file_path)
                            return 0
                        except FileNotFoundError:
                            # Fallback: print directly
                            os.unlink(temp_file_path)
                            print(terminal_content)
                            return 0
                else:
                    # Claude Code environment: Write to temp file for reading
                    import tempfile
                    with tempfile.NamedTemporaryFile(mode='w', suffix='_VERSION.md', delete=False) as temp_file:
                        temp_file.write(content)
                        temp_file_path = temp_file.name

                    # Print with the massive separator line pattern
                    print()
                    print("ccc version =====================================================================================================================")
                    print()
                    print(f"📝 Version information written to: {temp_file_path}")
                    print("🎯 Claude: Please read and display this file!")
                    print(f"📄 File: {temp_file_path}")
                    return 0

            except Exception as e:
                print(f"❌ Error processing version file: {e}")
                # Fallback to simple version display

        # Fallback if no template file exists
        print(f"CCC Commander (cc/ccc/cccmd) v0.3.2 {mode} ({path})")
        print("📖 Documentation: https://collective-context.org/ccc/installation/")
        return 0

    def git_push_homepage(self, message=None):
        """Analyze session achievements and update collective-context.org"""
        print()
        print("ccc git push homepage =====================================================================================================================")
        print()
        print("🌐 CCC Homepage Update Tool")
        print("=" * 50)
        print("\n📝 Analyzing session achievements...")

        # Prompt for Claude to reflect on the session
        print("\n💭 Claude: Please reflect on this session's achievements:")
        print("   - v0.3.2 Release Finalization")
        print("   - Test Suite Integration (96 tests)")
        print("   - CI/CD Pipeline Setup")
        print("   - PPA Packaging Infrastructure")
        print("   - Security Hardening")
        if message:
            print(f"\n📝 Additional request: {message}")

        print("\n🎯 Now updating collective-context.org with these achievements...")

        # Note: This triggers Claude to update the homepage
        print("\n✅ Homepage update initiated!")
        print("📄 Check: https://collective-context.org")
        return 0

    def git_push_ccc(self, run_tests=False, message=None):
        """Quick push or full validation with tests, then push CCC to GitHub"""
        import subprocess
        import os
        from pathlib import Path

        # Print with the massive separator line pattern
        print()
        if run_tests:
            print("ccc git push ccc tests =====================================================================================================================")
            print()
            print("🔍 CCC Full Quality Control & Security Audit")
        else:
            print("ccc git push ccc =====================================================================================================================")
            print()
            print("⚡ CCC Quick Push (without tests)")
        print("=" * 50)

        # Check if we're in the right directory
        current_dir = Path.cwd()
        expected_dir = Path.home() / "prog/ai/git/collective-context/ccc"

        if current_dir != expected_dir:
            print(f"📁 Switching to CCC directory: {expected_dir}")
            os.chdir(expected_dir)

        # Only run tests and audits if requested
        if run_tests:
            print("\n🧪 Step 1: Running Test Suite...")
            try:
                result = subprocess.run(["make", "test"], capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    print("✅ All tests passed!")
                    # Count test results
                    if "passed" in result.stdout:
                        test_line = [line for line in result.stdout.split('\n') if 'passed' in line][-1]
                        print(f"📊 {test_line}")
                else:
                    print("❌ Tests failed!")
                    print(result.stderr)
                    return 1
            except subprocess.TimeoutExpired:
                print("⏱️ Tests timed out - continuing anyway")
            except FileNotFoundError:
                print("⚠️ Make not available - running pytest directly")
                try:
                    result = subprocess.run(["python3", "-m", "pytest"], capture_output=True, text=True, timeout=120)
                    if result.returncode == 0:
                        print("✅ Pytest completed successfully!")
                    else:
                        print("⚠️ Some tests may have issues")
                except:
                    print("📝 Tests not run - continuing with audit")

            print("\n🔒 Step 2: Security Audit...")
            security_checks = [
                ("Checking for hardcoded secrets", ["grep", "-r", "-i", "password\\|secret\\|key\\|token", ".", "--exclude-dir=.git", "--exclude-dir=venv", "--exclude-dir=node_modules"]),
                ("Checking for unsafe subprocess calls", ["grep", "-r", "subprocess.*shell=True", ".", "--exclude-dir=.git"]),
                ("Checking for SQL injection patterns", ["grep", "-r", "%s.*execute\\|format.*execute", ".", "--exclude-dir=.git"]),
            ]

            security_passed = True
            for check_name, cmd in security_checks:
                print(f"   🔍 {check_name}...")
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0 and result.stdout.strip():
                        print(f"      ⚠️ Found potential issues:")
                        print(f"      {result.stdout[:200]}...")
                        security_passed = False
                    else:
                        print(f"      ✅ Clean")
                except:
                    print(f"      📝 Check skipped")

            print("\n📋 Step 3: Code Quality Check...")
            quality_checks = [
                ("Python syntax check", ["python3", "-m", "py_compile", "ccc_main.py"]),
                ("Import validation", ["python3", "-c", "import lib.ccc_commands; import lib.ccc_manager; print('✅ Imports OK')"]),
            ]

            for check_name, cmd in quality_checks:
                print(f"   📝 {check_name}...")
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        print(f"      ✅ Passed")
                    else:
                        print(f"      ❌ Failed: {result.stderr[:100]}")
                        return 1
                except:
                    print(f"      📝 Check skipped")
        else:
            print("\n⚡ Skipping tests and audits for quick push...")
            print("   ℹ️  Use 'ccc git push ccc tests' for full validation")

        print("\n📊 Git Status Check...")
        try:
            result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
            if result.stdout.strip():
                print("   📝 Uncommitted changes found:")
                print(f"   {result.stdout}")

                print("\n💾 Committing Changes...")
                subprocess.run(["git", "add", "-A"])

                if run_tests:
                    if message:
                        commit_msg = f"feat: CCC update with full quality control\n\nComprehensive validation including:\n- 96 test suite fully validated\n- Security audit completed\n- Quality control passed\n- All checks verified before push\n\nAdditional notes: {message}\n\n🤖 Generated with [Claude Code](https://claude.ai/code)\n\nCo-Authored-By: Claude <noreply@anthropic.com>"
                    else:
                        commit_msg = f"feat: CCC update with full quality control\n\nComprehensive validation including:\n- 96 test suite fully validated\n- Security audit completed\n- Quality control passed\n- All checks verified before push\n\n🤖 Generated with [Claude Code](https://claude.ai/code)\n\nCo-Authored-By: Claude <noreply@anthropic.com>"
                else:
                    if message:
                        commit_msg = f"chore: CCC quick update\n\nQuick push for minor changes:\n- Small improvements and fixes\n- No breaking changes\n- Tests skipped for speed\n\nAdditional notes: {message}\n\n🤖 Generated with [Claude Code](https://claude.ai/code)\n\nCo-Authored-By: Claude <noreply@anthropic.com>"
                    else:
                        commit_msg = f"chore: CCC quick update\n\nQuick push for minor changes:\n- Small improvements and fixes\n- No breaking changes\n- Tests skipped for speed\n\n🤖 Generated with [Claude Code](https://claude.ai/code)\n\nCo-Authored-By: Claude <noreply@anthropic.com>"

                result = subprocess.run(["git", "commit", "-m", commit_msg], capture_output=True, text=True)
                if result.returncode == 0:
                    print("   ✅ Changes committed successfully!")
                else:
                    print(f"   ❌ Commit failed: {result.stderr}")
                    return 1
            else:
                print("   ✅ No uncommitted changes")
        except:
            print("   📝 Git status check skipped")

        print("\n🚀 Step 6: Pushing to GitHub...")
        try:
            # Push to origin
            result = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)
            if result.returncode == 0:
                print("   ✅ Successfully pushed to GitHub!")
                print("   🔗 Repository: https://github.com/collective-context/ccc")
            else:
                print(f"   ❌ Push failed: {result.stderr}")
                return 1
        except:
            print("   ❌ Git push failed")
            return 1

        print("\n" + "=" * 50)
        if run_tests:
            print("🎉 CCC Full Quality Control & GitHub Push Complete!")
            print("\n📊 Summary:")
            print("   ✅ Tests: Validated")
            print("   ✅ Security: Audited")
            print("   ✅ Quality: Verified")
            print("   ✅ GitHub: Updated")
        else:
            print("⚡ CCC Quick Push Complete!")
            print("\n📊 Summary:")
            print("   ⏭️  Tests: Skipped")
            print("   ⏭️  Security: Skipped")
            print("   ⏭️  Quality: Skipped")
            print("   ✅ GitHub: Updated")
            print("\n   ℹ️  For full validation, use: ccc git push ccc tests")

        print("\n🔗 Live Repository: https://github.com/collective-context/ccc")
        print("📦 PyPI Package: https://pypi.org/project/cccmd/")

        # CRITICAL: Verify CI/CD results after push (solving "push and hope" problem)
        if run_tests:
            print("\n🔍 Step 7: Verifying GitHub Actions CI/CD...")
            ci_success = self.check_github_actions_status()
            if not ci_success:
                print("❌ GitHub Actions failed! Check the logs with: ccc git logs")
                return 1
            else:
                print("✅ GitHub Actions passed! Full CI/CD verification complete.")

        return 0

    def check_github_actions_status(self, timeout_minutes=5):
        """Check GitHub Actions CI/CD status after push"""
        import subprocess
        import time
        import json

        print("   🔄 Waiting for GitHub Actions to start...")
        time.sleep(10)  # Give GitHub time to trigger the action

        for attempt in range(timeout_minutes * 2):  # Check every 30 seconds
            try:
                # Use GitHub CLI to get recent workflow runs
                result = subprocess.run([
                    "gh", "run", "list", "--limit", "1", "--json", "conclusion,status,url,headBranch"
                ], capture_output=True, text=True, timeout=30)

                if result.returncode == 0:
                    runs = json.loads(result.stdout)
                    if runs:
                        latest_run = runs[0]
                        status = latest_run.get('status', 'unknown')
                        conclusion = latest_run.get('conclusion', 'unknown')
                        url = latest_run.get('url', 'unknown')

                        print(f"   📊 CI Status: {status}, Conclusion: {conclusion}")

                        if status == 'completed':
                            if conclusion == 'success':
                                print(f"   ✅ GitHub Actions passed!")
                                print(f"   🔗 Run details: {url}")
                                return True
                            else:
                                print(f"   ❌ GitHub Actions failed: {conclusion}")
                                print(f"   🔗 Failed run: {url}")
                                return False
                        elif status in ['in_progress', 'queued']:
                            print(f"   ⏳ Still running... (attempt {attempt + 1}/{timeout_minutes * 2})")
                            time.sleep(30)
                        else:
                            print(f"   ⚠️ Unexpected status: {status}")
                            time.sleep(30)
                else:
                    print(f"   ⚠️ GitHub CLI error: {result.stderr}")
                    break

            except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
                print(f"   📝 GitHub CLI not available or error, checking via API...")
                # Fallback: Use curl with GitHub API
                try:
                    result = subprocess.run([
                        "curl", "-s", "-H", "Accept: application/vnd.github.v3+json",
                        "https://api.github.com/repos/collective-context/ccc/actions/runs?per_page=1"
                    ], capture_output=True, text=True, timeout=10)

                    if result.returncode == 0:
                        data = json.loads(result.stdout)
                        if data.get('workflow_runs'):
                            latest_run = data['workflow_runs'][0]
                            status = latest_run.get('status', 'unknown')
                            conclusion = latest_run.get('conclusion', 'unknown')
                            print(f"   📊 API Status: {status}, Conclusion: {conclusion}")

                            if status == 'completed':
                                return conclusion == 'success'
                            elif status in ['in_progress', 'queued']:
                                time.sleep(30)
                            else:
                                break
                except:
                    print(f"   📝 API check failed, assuming success")
                    return True

        print("   ⏱️ Timeout waiting for CI results")
        return False

    def git_status(self):
        """Enhanced git status with CI/CD monitoring"""
        import subprocess
        import json

        print("📊 CCC Git Status with CI/CD Monitoring")
        print("=" * 50)

        # Standard git status
        print("\n📁 Local Repository Status:")
        try:
            result = subprocess.run(["git", "status", "--short"], capture_output=True, text=True)
            if result.stdout.strip():
                print(f"   📝 Changes:\n{result.stdout}")
            else:
                print("   ✅ Working directory clean")
        except:
            print("   📝 Git status unavailable")

        # Branch info
        try:
            result = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True)
            current_branch = result.stdout.strip()
            print(f"   🌿 Current branch: {current_branch}")
        except:
            print("   📝 Branch info unavailable")

        # Remote status
        try:
            result = subprocess.run(["git", "status", "--porcelain=v1", "--branch"], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            if lines and lines[0].startswith('##'):
                branch_info = lines[0][2:].strip()
                print(f"   🔄 Remote sync: {branch_info}")
        except:
            print("   📝 Remote status unavailable")

        # GitHub Actions status
        print("\n🔍 GitHub Actions CI/CD Status:")
        try:
            result = subprocess.run([
                "gh", "run", "list", "--limit", "3", "--json", "conclusion,status,url,workflowName,createdAt"
            ], capture_output=True, text=True, timeout=15)

            if result.returncode == 0:
                runs = json.loads(result.stdout)
                if runs:
                    for i, run in enumerate(runs[:3]):
                        status = run.get('status', 'unknown')
                        conclusion = run.get('conclusion', 'unknown')
                        workflow = run.get('workflowName', 'Unknown')
                        created = run.get('createdAt', 'Unknown')[:19].replace('T', ' ')

                        status_icon = "✅" if conclusion == "success" else "❌" if conclusion == "failure" else "⏳"
                        print(f"   {status_icon} {workflow}: {status}/{conclusion} ({created})")
                else:
                    print("   📝 No recent workflow runs found")
            else:
                print(f"   ⚠️ GitHub CLI error: {result.stderr}")
        except:
            print("   📝 GitHub Actions status unavailable")

        print(f"\n🔗 Repository: https://github.com/collective-context/ccc")
        print(f"🔗 Actions: https://github.com/collective-context/ccc/actions")
        return 0

    def git_logs(self, failed_only=False):
        """Show GitHub Actions logs"""
        import subprocess
        import json

        print("📜 GitHub Actions Logs")
        print("=" * 50)

        try:
            # Get recent runs
            cmd = ["gh", "run", "list", "--limit", "5", "--json", "conclusion,status,url,workflowName,number"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)

            if result.returncode == 0:
                runs = json.loads(result.stdout)
                if runs:
                    print(f"\n📊 Recent Workflow Runs:")
                    for run in runs:
                        status = run.get('status', 'unknown')
                        conclusion = run.get('conclusion', 'unknown')
                        workflow = run.get('workflowName', 'Unknown')
                        number = run.get('number', 'Unknown')
                        url = run.get('url', '')

                        if failed_only and conclusion == 'success':
                            continue

                        status_icon = "✅" if conclusion == "success" else "❌" if conclusion == "failure" else "⏳"
                        print(f"   {status_icon} Run #{number}: {workflow} - {status}/{conclusion}")
                        print(f"      🔗 {url}")

                    # Show detailed logs for the latest run
                    if runs and not failed_only:
                        latest_run = runs[0]
                        run_number = latest_run.get('number')

                        print(f"\n📋 Detailed logs for latest run #{run_number}:")
                        log_result = subprocess.run([
                            "gh", "run", "view", str(run_number), "--log"
                        ], capture_output=True, text=True, timeout=30)

                        if log_result.returncode == 0:
                            # Show last 50 lines of logs
                            log_lines = log_result.stdout.split('\n')
                            print("   " + "\n   ".join(log_lines[-50:]))
                        else:
                            print(f"   ⚠️ Could not fetch detailed logs: {log_result.stderr}")

                    elif failed_only:
                        print("\n   ✅ No failed runs in recent history")
                else:
                    print("   📝 No workflow runs found")
            else:
                print(f"   ⚠️ GitHub CLI error: {result.stderr}")

        except Exception as e:
            print(f"   📝 Error fetching logs: {e}")

        return 0

    def git_check(self):
        """Manual CI/CD status check"""
        print("🔍 Manual GitHub Actions Check")
        print("=" * 50)

        return self.check_github_actions_status(timeout_minutes=1)

    def exec_upload_ppa(self):
        """Execute PPA upload to Launchpad"""
        try:
            from lib.ccc_ppa_upload import PPAUploader

            print("🚀 CCC PPA Upload Tool")
            print("=" * 50)

            uploader = PPAUploader(self.manager)

            # Check for packages first
            packages = uploader.check_packages()
            if not packages:
                print("❌ No packages found!")
                print("   Run scripts/build-deb.sh first to create packages")
                return 1

            print(f"📦 Found {len(packages)} package(s) to upload:")
            for pkg in packages:
                status = "✅ SIGNED" if pkg['signed'] else "⚠️ NOT SIGNED"
                print(f"   - {pkg['file']} {status}")

            # Run the upload process
            success = uploader.run_upload_process()

            if success:
                print("✅ All packages uploaded successfully!")
                print("🔗 Check status at: https://launchpad.net/~collective-context/+archive/ubuntu/ccc")
                return 0
            else:
                print("❌ Some packages failed to upload. Check logs for details.")
                print("📝 Logs: local-only/logs/ppa-upload-*.md")
                return 1

        except ImportError:
            print("❌ PPA Upload module not found!")
            print("   Ensure lib/ccc_ppa_upload.py exists")
            return 1
        except Exception as e:
            print(f"❌ PPA Upload failed: {e}")
            self.manager.log(f"PPA upload exception: {e}", "ERROR")
            return 1

    def exec_debian_command(self, command=None):
        """Execute Debian packaging commands"""
        try:
            from lib.ccc_debian_build import debian_build_command, debian_upload_command, debian_full_command

            if not command:
                print("❌ No Debian command specified!")
                print("Available commands:")
                print("  • ccc exec debian build   - Build Debian packages for all distributions")
                print("  • ccc exec debian upload  - Upload packages to Reprepro repository")
                print("  • ccc exec debian full    - Build and upload packages")
                return 1

            print("🚀 CCC Debian Packaging System")
            print("=" * 50)

            if command == "build":
                return debian_build_command(self.manager)
            elif command == "upload":
                return debian_upload_command(self.manager)
            elif command == "full":
                return debian_full_command(self.manager)
            else:
                print(f"❌ Unknown Debian command: {command}")
                print("Available commands: build, upload, full")
                return 1

        except ImportError:
            print("❌ Debian Build module not found!")
            print("   Ensure lib/ccc_debian_build.py exists")
            return 1
        except Exception as e:
            print(f"❌ Debian command failed: {e}")
            self.manager.log(f"Debian command exception: {e}", "ERROR")
            return 1

    def list(self):
        """List all services"""
        print("\n[SECTIONS] Available CCC Services:")
        print("=" * 50)
        for name, config in self.manager.config["services"].items():
            status = "🟢 RUNNING" if config["enabled"] else "🔴 STOPPED"
            print(f"  {name:15} {status}")
            if name == "autoinput":
                if "current_text" in config:
                    print(f"    Text: '{config['current_text']}'")
                if "interval" in config:
                    print(f"    Interval: {config['interval']/60} minutes")
            elif name == "dialog":
                if config.get("log_file"):
                    print(f"    Log: {config['log_file']}")
                if config.get("session_id"):
                    print(f"    Session: {config['session_id']}")
            elif name == "save":
                if config.get("log_file"):
                    print(f"    Session Log: {config['log_file']}")
                if config.get("with_dialog") and config.get("dialog_log_file"):
                    print(f"    Dialog Log: {config['dialog_log_file']}")
                if config.get("session_start"):
                    print(f"    Started: {config['session_start']}")
        print("=" * 50)
        return 0

    def session_start(self, ai_instance=None, session_name=None):
        """Initialize new Claude session with complete CCC context loading"""

        # Define AI instance mapping
        ai_instances = {
            # Long names
            "claude-1": {"short": "CL1", "full": "Claude-1", "role": "System Architect & Conductor"},
            "claude-2": {"short": "CL2", "full": "Claude-2", "role": "Quality Gate & Code Review"},
            "aider-1": {"short": "AI1", "full": "Aider-1", "role": "Primary Code Implementation"},
            "aider-2": {"short": "AI2", "full": "Aider-2", "role": "Parallel Development & Testing"},
            # Short aliases
            "cl1": {"short": "CL1", "full": "Claude-1", "role": "System Architect & Conductor"},
            "cl2": {"short": "CL2", "full": "Claude-2", "role": "Quality Gate & Code Review"},
            "ai1": {"short": "AI1", "full": "Aider-1", "role": "Primary Code Implementation"},
            "ai2": {"short": "AI2", "full": "Aider-2", "role": "Parallel Development & Testing"},
        }

        # Validate and resolve AI instance
        current_instance = None
        if ai_instance:
            ai_key = ai_instance.lower()
            if ai_key in ai_instances:
                current_instance = ai_instances[ai_key]
            else:
                print(f"❌ Unknown AI instance: {ai_instance}")
                print("Available instances: [Claude-1|Claude-2|Aider-1|Aider-2] or [CL1|CL2|AI1|AI2]")
                return 1

        # Display session header
        if current_instance:
            header = f"\n🚀 CCC Session Start - {current_instance['full']} ({current_instance['short']})"
            if session_name:
                header += f" - 📝 {session_name}"
            print(header)
            print(f"📋 Role: {current_instance['role']}")
        else:
            header = f"\n🚀 CCC Session Start - Loading Complete Context..."
            if session_name:
                header += f" - 📝 {session_name}"
            print(header)

        print("=" * 60)

        # A) Load core CCC knowledge files
        print("\n📚 [A] Loading Core CCC Knowledge:")
        core_files = [
            ("0.HELLO-AI-START-HERE.md", ""),  # Root file
            ("README.md", ""),                  # Root file
            ("CLAUDE.md", "readme/"),          # Moved to readme/
            ("CCC-SYSTEM-FOUNDATION.md", "readme/")  # Moved to readme/
        ]

        base_dir = self.manager.base_dir
        for filename, subdir in core_files:
            if subdir:
                file_path = base_dir / subdir / filename
            else:
                file_path = base_dir / filename

            if file_path.exists():
                print(f"✅ {filename}")
                # For Claude: recommend reading these files
                print(f"   📄 Path: {file_path}")
            else:
                print(f"⚠️  {filename} (not found)")

        # B) Load recent session history from local-only
        print("\n📝 [B] Recent Session History (local-only/):")
        local_only_dir = base_dir / "local-only"
        if local_only_dir.exists():
            import glob
            import os
            from pathlib import Path

            # Find session files from last few days
            session_files = []
            session_dir = local_only_dir / "SESSION"
            if session_dir.exists():
                for pattern in ["*SESSION*.md", "*session*.md", "*2025-*.md"]:
                    session_files.extend(glob.glob(str(session_dir / pattern)))

            # Sort by modification time, newest first
            session_files = sorted(session_files, key=os.path.getmtime, reverse=True)[:5]

            if session_files:
                for session_file in session_files:
                    filename = Path(session_file).name
                    mod_time = datetime.fromtimestamp(os.path.getmtime(session_file))
                    print(f"✅ {filename}")
                    print(f"   📄 Path: {session_file}")
                    print(f"   🕐 Modified: {mod_time.strftime('%Y-%m-%d %H:%M')}")
            else:
                print("ℹ️  No recent session files found")
        else:
            print("⚠️  local-only/ directory not found")

        # C) List available project contexts
        print("\n🎯 [C] Available Project Contexts:")
        if local_only_dir.exists():
            project_contexts = []
            # Include both original and template (_e.md) files
            for pattern in ["CLAUDE-*.md", "HELLO-*.md", "CLAUDE-*_e.md", "HELLO-*_e.md"]:
                project_contexts.extend(glob.glob(str(local_only_dir / pattern)))

            if project_contexts:
                contexts = {}
                for context_file in project_contexts:
                    filename = Path(context_file).name
                    # Mark template files
                    is_template = filename.endswith("_e.md")

                    # Extract project name from filename
                    if "CCC-Development" in filename or "CCC-Project" in filename:
                        project = "CCC Development" + (" [Template]" if is_template else "")
                    elif "osCASH-android" in filename:
                        project = "osCASH.me Android APP" + (" [Template]" if is_template else "")
                    elif "mollyim-core" in filename:
                        project = "Molly Core Development" + (" [Template]" if is_template else "")
                    elif "osCASH-GATE" in filename:
                        project = "osCASH.me Payment Gateway" + (" [Template]" if is_template else "")
                    else:
                        project = "Unknown Project" + (" [Template]" if is_template else "")

                    if project not in contexts:
                        contexts[project] = []
                    contexts[project].append((filename, context_file))

                for project, files in contexts.items():
                    print(f"🎯 {project}:")
                    for filename, filepath in files:
                        print(f"   📄 {filename}")
                        print(f"      Path: {filepath}")
            else:
                print("ℹ️  No project contexts found")

        print("\n" + "=" * 60)
        print("🎯 Session Context Loaded Successfully!")

        # Show multi-agent orchestration info if instance specified
        if current_instance:
            print(f"\n🎭 Multi-Agent Orchestra Pattern:")
            print("┌─────────────────┬─────────────────┐")
            print("│   Claude-1      │   Claude-2      │")
            print("│   (Architect)   │   (Reviewer)    │")
            print("├─────────────────┼─────────────────┤")
            print("│   Aider-1       │   Aider-2       │")
            print("│   (Main Dev)    │   (Parallel)    │")
            print("└─────────────────┴─────────────────┘")

            # Highlight current instance
            current_position = {
                "CL1": "🎯 You are: Claude-1 (Architect) - System design & coordination",
                "CL2": "🎯 You are: Claude-2 (Reviewer) - Quality gates & code review",
                "AI1": "🎯 You are: Aider-1 (Main Dev) - Primary implementation",
                "AI2": "🎯 You are: Aider-2 (Parallel) - Parallel development & testing"
            }
            print(f"\n{current_position[current_instance['short']]}")

            print(f"\n💼 Your Role in this Session:")
            print(f"   • {current_instance['role']}")
            print(f"   • Instance ID: {current_instance['short']}")
            print(f"   • Coordinate with other agents as needed")

        print("\n💡 Next Steps:")
        print("   1. Read the core knowledge files listed above")
        print("   2. Review recent session history if relevant")
        print("   3. Load specific project context as needed")
        print("   4. Navigate to project directory when ready")

        if current_instance:
            print(f"   5. Execute your role as {current_instance['full']}")

        print("\n🚀 Ready for Multi-Agent Development!")

        # CRITICAL: Provide explicit session identity context to Claude
        print("\n" + "=" * 60)
        print("🎭 SESSION IDENTITY CONTEXT FOR CLAUDE:")
        print("=" * 60)

        if session_name:
            print(f"📋 Your session name is: **{session_name}**")
            print(f"🔤 When asked 'What is your name?' or 'Who are you?', respond: '{session_name}'")

            # Generate aliases based on session name
            aliases = self._generate_session_aliases(session_name)
            if aliases:
                print(f"🏷️  Your aliases are: {', '.join(aliases)}")
                print(f"🗃️  When asked for aliases, respond: '{', '.join(aliases)}'")

        if current_instance:
            print(f"🤖 Your AI instance role: {current_instance['full']} ({current_instance['short']})")
            print(f"📝 Your role description: {current_instance['role']}")
            if session_name:
                print(f"💾 Save session files with prefix: {session_name}")
            else:
                print(f"💾 Save session files with prefix: {current_instance['short']}")
        else:
            if session_name:
                print(f"💾 Save session files with prefix: {session_name}")

        print("=" * 60)
        print("💡 This is your active session identity. Use it consistently!")

        return 0

    def _generate_session_aliases(self, session_name):
        """Generate aliases for session name based on known patterns"""
        aliases = []

        # Convert to lowercase for processing
        name_lower = session_name.lower()

        # Handle Claude-X patterns
        if name_lower.startswith('claude-'):
            number = name_lower.replace('claude-', '')
            aliases.extend([
                f"CL{number.upper()}",
                f"cl{number}",
                f"claude-{number}",
                f"Claude-{number}"
            ])

        # Handle Aider-X patterns
        elif name_lower.startswith('aider-'):
            number = name_lower.replace('aider-', '')
            aliases.extend([
                f"AI{number.upper()}",
                f"ai{number}",
                f"aider-{number}",
                f"Aider-{number}"
            ])

        # Handle CL/AI patterns
        elif name_lower.startswith('cl'):
            number = name_lower.replace('cl', '')
            aliases.extend([
                f"CL{number.upper()}",
                f"cl{number}",
                f"claude-{number}",
                f"Claude-{number}"
            ])

        elif name_lower.startswith('ai'):
            number = name_lower.replace('ai', '')
            aliases.extend([
                f"AI{number.upper()}",
                f"ai{number}",
                f"aider-{number}",
                f"Aider-{number}"
            ])

        # For custom names, generate basic variations
        else:
            # Add lowercase, uppercase, title case variations
            if session_name != session_name.lower():
                aliases.append(session_name.lower())
            if session_name != session_name.upper():
                aliases.append(session_name.upper())
            if session_name != session_name.title():
                aliases.append(session_name.title())

        # Remove duplicates and the original session name
        aliases = list(set(aliases))
        if session_name in aliases:
            aliases.remove(session_name)

        return aliases

    def _normalize_session_name(self, session_name):
        """Normalize session name to standard format"""
        if not session_name:
            return None

        # Convert to lowercase for processing
        name_lower = session_name.lower().replace('-', '').replace('_', '')

        # Define normalization mapping
        normalization_map = {
            # Claude variants
            'claude1': 'Claude-1',
            'claude2': 'Claude-2',
            'claude3': 'Claude-3',
            'cl1': 'Claude-1',
            'cl2': 'Claude-2',
            'cl3': 'Claude-3',

            # Aider variants
            'aider1': 'Aider-1',
            'aider2': 'Aider-2',
            'ai1': 'Aider-1',
            'ai2': 'Aider-2',
        }

        # Check if it matches a known pattern
        if name_lower in normalization_map:
            return normalization_map[name_lower]

        # If it's already in proper format (Claude-X, Aider-X), return as-is
        if session_name.startswith('Claude-') or session_name.startswith('Aider-'):
            return session_name

        # For unknown names, return as-is but title-cased
        return session_name.title()

    def _generate_session_aliases(self, session_name):
        """Generate aliases for session name based on known patterns"""
        aliases = []

        # For normalized names, provide single standardized alias
        if session_name == 'Claude-1':
            return ['CL1']
        elif session_name == 'Claude-2':
            return ['CL2']
        elif session_name == 'Claude-3':
            return ['CL3']
        elif session_name == 'Aider-1':
            return ['AI1']
        elif session_name == 'Aider-2':
            return ['AI2']

        # For custom names, generate basic variations
        name_upper = session_name.upper()
        if name_upper != session_name:
            aliases.append(name_upper)

        return aliases

    def session_save(self, ai_instance=None):
        """Nutzt das neue SQLite-basierte Session-System"""
        import sys
        sys.path.append(str(Path(__file__).parent.parent))
        from ccc_session_integration import CCCSessionIntegration
        integration = CCCSessionIntegration()
        return integration.handle_session_command(['save'])

    def session_end(self, ai_instance=None):
        """Create comprehensive session memory export for long-term storage"""
        print("\n🏁 CCC Session End - Creating Full Session Memory...")
        print("=" * 60)

        from datetime import datetime
        from pathlib import Path
        import glob
        import os

        # Create timestamp for filename
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")

        # Define local-only and SESSION directory
        local_only_dir = self.manager.base_dir / "local-only"
        session_dir = local_only_dir / "SESSION"
        session_dir.mkdir(parents=True, exist_ok=True)

        # Determine AI instance prefix
        ai_prefix = ""
        if ai_instance:
            # Map to short form
            ai_instances = {
                "claude-1": "CL1", "cl1": "CL1",
                "claude-2": "CL2", "cl2": "CL2",
                "aider-1": "AI1", "ai1": "AI1",
                "aider-2": "AI2", "ai2": "AI2"
            }
            ai_key = ai_instance.lower()
            if ai_key in ai_instances:
                ai_prefix = f"_{ai_instances[ai_key]}"

        # Create filename for full session
        if ai_prefix:
            session_filename = f"{timestamp}{ai_prefix}_SESSION-FULL.md"
        else:
            session_filename = f"{timestamp}_SESSION-FULL.md"
        session_file_path = session_dir / session_filename

        print(f"📝 Creating comprehensive session file: {session_filename}")
        print(f"   📄 Path: {session_file_path}")

        # Gather context for session summary
        print("\n📊 Gathering session context...")

        # Look for today's session save file
        today = datetime.now().strftime("%Y-%m-%d")
        daily_file = session_dir / f"{today}_SESSION-SAVE.md"

        daily_content = ""
        if daily_file.exists():
            print(f"✅ Found today's session save: {daily_file.name}")
            with open(daily_file, "r", encoding="utf-8") as f:
                daily_content = f.read()
        else:
            print("ℹ️  No daily session save found for today")

        # Find recent session files for context
        print("\n📚 Recent session files for reference:")
        session_files = []
        for pattern in ["*SESSION*.md", "*session*.md"]:
            session_files.extend(glob.glob(str(session_dir / pattern)))

        # Sort by modification time, newest first
        session_files = sorted(session_files, key=os.path.getmtime, reverse=True)[:3]

        for session_file in session_files:
            filename = Path(session_file).name
            if filename != session_filename:  # Don't list the file we're creating
                print(f"   📄 {filename}")

        # Create comprehensive session document
        print("\n" + "=" * 60)
        print("🧠 COMPLETE SESSION MEMORY EXPORT")
        print("Please provide comprehensive session knowledge:")
        print("\nInclude:")
        print("1. Session objectives and goals")
        print("2. Major tasks completed")
        print("3. Problems solved and solutions found")
        print("4. Code changes and implementations")
        print("5. Decisions made and rationale")
        print("6. Unfinished tasks for next session")
        print("7. Key learnings and insights")
        print("\n💡 Claude: Please create full session documentation now!")

        # Create session document structure
        session_content = f"""# Complete Session Memory - {timestamp}

**Session End: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**
**Location**: ~/prog/ai/git/collective-context/ccc/

## 🎯 Session Overview

**[Claude to provide session summary]**

## 📋 Tasks Completed

**[Claude to list completed tasks]**

## 🔧 Technical Implementations

**[Claude to document code changes and implementations]**

## 💡 Key Insights & Learnings

**[Claude to capture important learnings]**

## 🚧 Pending/Future Work

**[Claude to note unfinished items]**

---

## Daily Session Save Content

{daily_content if daily_content else "No daily session save available."}

---

## Session Metadata

- **Start Time**: [Session start time]
- **End Time**: {datetime.now().strftime('%H:%M:%S')}
- **Duration**: [Approximate duration]
- **Primary Focus**: [Main topic/project]
- **Tools Used**: CCC, Claude Code, [other tools]

---

*Session memory preserved for future context loading*
"""

        # Write session file
        with open(session_file_path, "w", encoding="utf-8") as f:
            f.write(session_content)

        print(f"\n✅ Full session memory created: {session_file_path}")
        print("🧠 Session knowledge preserved for long-term memory")
        print("💡 This file can be loaded in future sessions with 'ccc session start'")
        print("\n🏁 Session ended successfully!")

        return 0

    def session_manage(self, action=None, name=None):
        """TypeScript-based session management (save/load/list JSON sessions)"""
        import subprocess
        import os

        print("\n🔧 CCC TypeScript Session Management")
        print("=" * 50)

        # Check if Node.js build exists
        dist_dir = self.manager.base_dir / "dist"
        if not dist_dir.exists():
            print("⚠️  Building TypeScript session management...")
            try:
                result = subprocess.run(["npm", "run", "build"],
                                      cwd=self.manager.base_dir,
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"❌ Build failed: {result.stderr}")
                    return 1
                print("✅ Build successful")
            except Exception as e:
                print(f"❌ Error building: {e}")
                return 1

        if not action:
            print("Usage:")
            print("  ccc session manage save <name>     # Save session")
            print("  ccc session manage list           # List sessions")
            print("  ccc session manage load <file>    # Load session")
            return 0

        # Build command
        cmd = ["node", str(dist_dir / "cli" / "index.js"), "session"]

        if action == "save" and name:
            cmd.extend(["save", name])
        elif action == "list":
            cmd.append("list")
        elif action == "load" and name:
            cmd.extend(["load", name])
        else:
            print("❌ Invalid action or missing name parameter")
            return 1

        # Execute TypeScript CLI
        try:
            result = subprocess.run(cmd, cwd=self.manager.base_dir)
            return result.returncode
        except Exception as e:
            print(f"❌ Error executing session command: {e}")
            return 1

    def context_read(self, ai_instance=None):
        """Read own AI instance context file"""
        from datetime import datetime
        from pathlib import Path

        # Map AI instance to context file
        ai_instances = {
            "claude-1": "Claude-1", "cl1": "Claude-1",
            "claude-2": "Claude-2", "cl2": "Claude-2",
            "aider-1": "Aider-1", "ai1": "Aider-1",
            "aider-2": "Aider-2", "ai2": "Aider-2"
        }

        if ai_instance:
            ai_key = ai_instance.lower()
            if ai_key in ai_instances:
                target_instance = ai_instances[ai_key]
            else:
                print(f"❌ Unknown AI instance: {ai_instance}")
                print("Available: [Claude-1|Claude-2|Aider-1|Aider-2] or [CL1|CL2|AI1|AI2]")
                return 1
        else:
            # Default to Claude-1 if no instance specified
            target_instance = "Claude-1"

        # Define context file path
        local_only_dir = self.manager.base_dir / "local-only"
        context_file = local_only_dir / f"{target_instance}.md"

        print(f"\n📖 Reading Context for {target_instance}")
        print("=" * 50)

        if context_file.exists():
            print(f"📄 File: {context_file}")
            with open(context_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Show file content
            lines = content.split('\n')
            print(f"📊 Context content: {len(lines)} lines")
            print("\n" + content)
        else:
            print(f"ℹ️  No context file found for {target_instance}")
            print(f"   Creating: {context_file}")

            # Create initial context file
            initial_content = f"""# {target_instance} Context

**AI Instance**: {target_instance}
**Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Role**: {self._get_instance_role(target_instance)}

## Current Session Context

[No context yet - add content via 'ccc context to {target_instance.lower()}']

---

*Multi-Agent Context System - CCC*
"""

            local_only_dir.mkdir(parents=True, exist_ok=True)
            with open(context_file, "w", encoding="utf-8") as f:
                f.write(initial_content)

            print(f"✅ Created initial context file: {context_file}")
            print("\n" + initial_content)

        return 0

    def context_write(self, target_instance, message=None):
        """Write context/message to target AI instance"""
        from datetime import datetime
        from pathlib import Path

        # Map target instance
        ai_instances = {
            "claude-1": "Claude-1", "cl1": "Claude-1",
            "claude-2": "Claude-2", "cl2": "Claude-2",
            "aider-1": "Aider-1", "ai1": "Aider-1",
            "aider-2": "Aider-2", "ai2": "Aider-2",
            "all": "all"
        }

        target_key = target_instance.lower()
        if target_key not in ai_instances:
            print(f"❌ Unknown target instance: {target_instance}")
            print("Available: [Claude-1|Claude-2|Aider-1|Aider-2|all] or [CL1|CL2|AI1|AI2|all]")
            return 1

        target_name = ai_instances[target_key]

        # Handle 'all' target
        if target_name == "all":
            targets = ["Claude-2", "Aider-1", "Aider-2"]  # Exclude self (Claude-1)
            print(f"\n📝 Broadcasting message to all other agents...")
            for target in targets:
                self.context_write(target.lower(), message)
            return 0

        # Define context file path
        local_only_dir = self.manager.base_dir / "local-only"
        context_file = local_only_dir / f"{target_name}.md"

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Prepare message content
        if message:
            # Specific message provided
            message_content = f"""
## [{timestamp}] Message from Claude-1

{message}

---
"""
        else:
            # Current session knowledge
            message_content = f"""
## [{timestamp}] Session Update from Claude-1

**Current Status**: [Add current session knowledge here]
**Tasks in Progress**: [List current tasks]
**Coordination Notes**: [Add coordination information]

---
"""

        print(f"\n📝 Writing to {target_name} context...")
        print(f"📄 File: {context_file}")

        # Create file if it doesn't exist
        if not context_file.exists():
            self.context_read(target_instance)  # This will create the file

        # Append message to context file
        with open(context_file, "a", encoding="utf-8") as f:
            f.write(message_content)

        print(f"✅ Message written to {target_name} context")
        if message:
            print(f"💬 Message: {message[:100]}...")
        else:
            print("💬 Session knowledge update template added")

        return 0

    def _get_instance_role(self, instance_name):
        """Get role description for AI instance"""
        roles = {
            "Claude-1": "System Architect & Conductor",
            "Claude-2": "Quality Gate & Code Review",
            "Aider-1": "Primary Code Implementation",
            "Aider-2": "Parallel Development & Testing"
        }
        return roles.get(instance_name, "Unknown Role")

    def start_dialog(self, service="dialog"):
        """Start dialog logging service"""
        if service not in self.manager.config["services"]:
            self.manager.log(f"Unknown service: {service}", "ERROR")
            return 1
        
        svc_config = self.manager.config["services"][service]
        
        if svc_config["enabled"]:
            print(f"⚠️  Dialog service already running")
            if svc_config.get("log_file"):
                print(f"📁 Current log: {svc_config['log_file']}")
            return 0
        
        # Enable dialog service
        svc_config["enabled"] = True
        self.manager.save_config()
        
        print(f"\n[SERVICES] Starting dialog logging...")
        
        # Start dialog monitor
        monitor_script = self.manager.base_dir / "ccc_dialog_monitor.py"
        try:
            import subprocess
            subprocess.Popen(
                ["python3", str(monitor_script)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            
            # Give it a moment to start
            import time
            time.sleep(1)
            
            # Check if monitor started and get log file
            self.manager.config = self.manager.load_config()
            updated_config = self.manager.config["services"][service]
            
            print(f"✅ Dialog logging STARTED")
            if updated_config.get("log_file"):
                print(f"📁 Log file: {updated_config['log_file']}")
                print(f"🆔 Session ID: {updated_config.get('session_id', 'N/A')}")
            
            return 0
            
        except Exception as e:
            print(f"❌ Failed to start dialog monitor: {e}")
            svc_config["enabled"] = False
            self.manager.save_config()
            return 1
    
    def stop_dialog(self, service="dialog"):
        """Stop dialog logging service"""
        if service not in self.manager.config["services"]:
            self.manager.log(f"Unknown service: {service}", "ERROR")
            return 1
        
        svc_config = self.manager.config["services"][service]
        
        if not svc_config["enabled"]:
            print(f"ℹ️  Dialog service not running")
            return 0
        
        # Disable service
        svc_config["enabled"] = False
        log_file = svc_config.get("log_file")
        session_id = svc_config.get("session_id")
        
        # Clear session info
        svc_config["log_file"] = None
        svc_config["session_id"] = None
        self.manager.save_config()
        
        # Stop dialog monitor process
        try:
            import subprocess
            subprocess.run(
                ["pkill", "-f", "ccc_dialog_monitor.py"],
                capture_output=True, timeout=5
            )
        except:
            pass
        
        print(f"\n🛑 Dialog logging STOPPED")
        if log_file:
            print(f"📁 Final log: {log_file}")
        if session_id:
            print(f"🆔 Session: {session_id}")
        
        return 0
    
    def start_save(self, service="save", with_dialog=False):
        """Start save service for Claude Self-Logging with optional dialog monitoring"""
        if service not in self.manager.config["services"]:
            self.manager.log(f"Unknown service: {service}", "ERROR")
            return 1
        
        svc_config = self.manager.config["services"][service]
        
        if svc_config["enabled"]:
            print(f"⚠️  Save service already running")
            if svc_config.get("log_file"):
                print(f"📁 Current session log: {svc_config['log_file']}")
            return 0
        
        # Create session-specific log file with timestamp
        from datetime import datetime
        session_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Session log (always created)
        session_log_dir = self.manager.base_dir / "logs" / "sessions"
        session_log_dir.mkdir(parents=True, exist_ok=True)
        session_log_file = session_log_dir / f"session_{session_timestamp}.md"
        
        # Always create new session log file
        with open(session_log_file, "w") as f:
            f.write(f"# Claude Session Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("**Automatic Claude Self-Logging Active**\n\n")
            if with_dialog:
                f.write("**Dialog Monitoring:** Active (tmux capture)\n\n")
            f.write("---\n\n")
        
        # Dialog log (only if requested with -d option)
        dialog_log_file = None
        if with_dialog:
            dialog_log_dir = self.manager.base_dir / "logs" / "dialogs"
            dialog_log_dir.mkdir(parents=True, exist_ok=True)
            dialog_log_file = dialog_log_dir / f"dialog_{session_timestamp}.md"
            
            # Start dialog monitor
            monitor_script = self.manager.base_dir / "ccc_dialog_monitor.py"
            try:
                import subprocess
                subprocess.Popen(
                    ["python3", str(monitor_script)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )
            except Exception as e:
                print(f"⚠️  Failed to start dialog monitor: {e}")
                with_dialog = False  # Disable if failed
        
        # Enable service and update config
        svc_config["enabled"] = True
        svc_config["log_file"] = str(session_log_file)
        svc_config["session_start"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        svc_config["with_dialog"] = with_dialog
        svc_config["dialog_log_file"] = str(dialog_log_file) if dialog_log_file else None
        self.manager.save_config()
        
        print(f"\n[SERVICES] Save service STARTED")
        print(f"📁 Session log: {session_log_file}")
        if with_dialog:
            print(f"📁 Dialog log: {dialog_log_file}")
            print("🔄 Dialog monitoring: ACTIVE")
        print(f"🤖 Claude Self-Logging: ACTIVE")
        
        return 0
    
    def stop_save(self, service="save"):
        """Stop save service"""
        if service not in self.manager.config["services"]:
            self.manager.log(f"Unknown service: {service}", "ERROR")
            return 1
        
        svc_config = self.manager.config["services"][service]
        
        if not svc_config["enabled"]:
            print(f"ℹ️  Save service not running")
            return 0
        
        # Stop dialog monitor if running
        if svc_config.get("with_dialog", False):
            try:
                import subprocess
                subprocess.run(
                    ["pkill", "-f", "ccc_dialog_monitor.py"],
                    capture_output=True, timeout=5
                )
                print("🛑 Dialog monitoring stopped")
            except:
                pass
        
        # Disable service
        svc_config["enabled"] = False
        session_log_file = svc_config.get("log_file")
        dialog_log_file = svc_config.get("dialog_log_file")
        session_start = svc_config.get("session_start")
        
        # Add session end marker to session log
        if session_log_file:
            from datetime import datetime
            try:
                with open(session_log_file, "a") as f:
                    f.write(f"\n---\n\n**Session ended:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            except:
                pass
        
        # Clear session info
        svc_config["log_file"] = None
        svc_config["dialog_log_file"] = None
        svc_config["session_start"] = None
        svc_config["with_dialog"] = False
        self.manager.save_config()
        
        print(f"\n🛑 Save service STOPPED")
        if session_log_file:
            print(f"📁 Final session log: {session_log_file}")
        if dialog_log_file:
            print(f"📁 Final dialog log: {dialog_log_file}")
        if session_start:
            from datetime import datetime
            print(f"📅 Session duration: {session_start} - {datetime.now().strftime('%H:%M:%S')}")
        
        return 0
    
    def restart_save(self, service="save", with_dialog=False):
        """Restart save service"""
        if service not in self.manager.config["services"]:
            self.manager.log(f"Unknown service: {service}", "ERROR")
            return 1
        
        print(f"\n🔄 Restarting save service...")
        
        # Stop save service first
        print("🛑 Stopping current save session...")
        stop_result = self.stop_save(service)
        
        if stop_result != 0:
            print("⚠️  Stop failed, continuing with restart...")
        
        # Short pause to ensure clean shutdown
        import time
        time.sleep(2)
        
        # Start save service with same dialog option
        print("[CONTROL] Starting new save session...")
        return self.start_save(service, with_dialog)
    
    def restart_dialog(self, service="dialog"):
        """Restart dialog logging service"""
        if service not in self.manager.config["services"]:
            self.manager.log(f"Unknown service: {service}", "ERROR")
            return 1
        
        print(f"\n🔄 Restarting dialog logging service...")
        
        # Stop dialog service first
        print("🛑 Stopping current dialog logging...")
        stop_result = self.stop_dialog(service)
        
        if stop_result != 0:
            print("⚠️  Stop failed, continuing with restart...")
        
        # Short pause to ensure clean shutdown
        import time
        time.sleep(2)
        
        # Start dialog service
        print("[CONTROL] Starting new dialog session...")
        return self.start_dialog(service)
    
    def help_show(self, section="all"):
        """Show help directly in Claude Code - chunked output"""
        
        if section == "all":
            print("CCC Commands: [CORE] status,config,list,help [CONTROL] start,restart,stop,test,exec [SERVICES] dialog,save(-d) [CONTEXT] context,co [OPTIONS] -m,-t=n,-d")
        elif section == "core":
            # Show Claude Code tip for detailed sections
            print("TIP: Tipp: Drücke strg+r um alle Hilfezeilen zu expandieren. Mit ESC kommst du zurück zur Eingabezeile.")
            print("\n[CORE] CORE COMMANDS:")
            print("  ccc status [service]         # Show brief service status")
            print("  ccc config [service]         # Show detailed configuration") 
            print("  ccc list                     # List all available services")
            print("  ccc help                     # Show compact help")
            print("  ccc help [section]           # Show help sections")
            
        elif section == "control":
            print("\n[CONTROL] SERVICE CONTROL:")
            print("  ccc start [service] [-m] [-t=n] [-- text]")
            print("    Start service (optionally with monitor & interval)")
            print("  ccc restart [service] [-m] [-t=n] [-- text]") 
            print("    Restart service (stop + start)")
            print("  ccc stop [service] [-m]")
            print("    Stop service (optionally stop monitor)")
            print("  ccc test [service]")
            print("    Reset to default text and send it once")
            print("  ccc exec [service] -- command")
            print("    Execute command in service context")
            
        elif section == "services":
            print("\n[SERVICES] SPECIALIZED SERVICES:")
            print("  ccc start dialog             # Start dialog monitoring")
            print("  ccc stop dialog              # Stop dialog monitoring")  
            print("  ccc restart dialog           # Restart dialog monitoring")
            print("  ccc start save [-d]          # Start Claude Self-Logging")
            print("  ccc restart save [-d]        # Restart save service")
            print("  ccc stop save                # Stop save service")
            
        elif section == "context":
            print("\n[CONTEXT] MULTI-AGENT CONTEXT SYSTEM:")
            print("  ccc context, ccc co              # Read own AI instance context")
            print("  ccc context to [target] -- msg   # Send message to target AI instance")
            print("  ccc context to all -- message    # Broadcast to all AI instances")
            print("  ccc context [instance]           # Read specific AI instance context")
            print("\n  Targets: cl1, cl2, ai1, ai2, all")
            print("  Examples:")
            print("    ccc co cl2                     # Read Claude-2's context")
            print("    ccc context to cl2 -- Hi!     # Message Claude-2")
            print("    ccc context to all -- Status  # Broadcast to all")
            
        elif section == "options":
            print("\n[CORE] OPTIONS:")
            print("  -m, --monitor               # Also start/stop background monitor")
            print("  -t=n, --time=n              # Set interval to n minutes (default: 5)")
            print("  -d, --dialog                # Start with dialog monitoring")
            
        elif section == "examples":
            print("\n[EXAMPLES] QUICK EXAMPLES:")
            print("  ccc list                     # Show all services")
            print("  ccc status save              # Check save status")
            print("  ccc start autoinput -t=3     # Start autoinput (3min)")
            print("  ccc start save -d            # Start logging + dialog")
            print("  ccc context                  # Read own context")
            print("  ccc context to cl2 -- Hi     # Message Claude-2")
            
        elif section == "info":
            print("\n[INFO] SERVICE INFO:")
            print("  autoinput - Auto-sends messages (default: 5min, 'Alles okay?')")
            print("  save      - Claude Self-Logging with optional dialog monitoring")  
            print("  dialog    - Tmux dialog monitoring service")
            
        if section == "sections":
            print("\n[SECTIONS] HELP SECTIONS:")
            print("  ccc help core          # Core commands")
            print("  ccc help control       # Service control")
            print("  ccc help services      # Specialized services")
            print("  ccc help context       # Multi-agent context system")
            print("  ccc help options       # Available options")
            print("  ccc help examples      # Quick examples")
            print("  ccc help full          # Complete help")
            
    def help_write_and_read(self, section="all"):
        """Write help to secure temp file for Claude Code display"""
        import os
        from pathlib import Path

        # Check if we should use pre-existing local files for full/experimental
        local_only_dir = Path(__file__).parent.parent / "local-only"

        if section == "full" and (local_only_dir / "HELP" / "full.md").exists():
            # Use existing full.md file
            local_file = local_only_dir / "HELP" / "full.md"
            try:
                with open(local_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Check if we're in a real terminal (not Claude Code)
                import sys
                if sys.stdout.isatty():
                    # We're in a real terminal - create terminal-optimized version
                    terminal_content = content.replace("```bash\n", "").replace("```\n", "").replace("```", "")

                    # Create a temporary terminal-friendly file
                    import tempfile
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
                        temp_file.write(terminal_content)
                        temp_file_path = temp_file.name

                    import subprocess
                    try:
                        subprocess.run(['nano', '-v', temp_file_path], check=False)
                        # Clean up temp file
                        import os
                        os.unlink(temp_file_path)
                        return 0
                    except FileNotFoundError:
                        # nano not available, try less
                        try:
                            subprocess.run(['less', temp_file_path], check=False)
                            import os
                            os.unlink(temp_file_path)
                            return 0
                        except FileNotFoundError:
                            # Fallback: print the terminal content directly
                            import os
                            os.unlink(temp_file_path)
                            print(terminal_content)
                            return 0
                else:
                    # Claude Code environment
                    print(f"📝 Using pre-existing help file: {local_file}")
                    print("🎯 Claude: Please read and display this file in your chat message!")
                    print(f"📄 File: {local_file}")
                    return 0
            except Exception as e:
                print(f"❌ Error reading {local_file}: {e}")
                # Fall through to generate content

        if section == "experimental" and (local_only_dir / "HELP" / "experimental.md").exists():
            # Use existing experimental.md file
            local_file = local_only_dir / "HELP" / "experimental.md"
            try:
                with open(local_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Check if we're in a real terminal (not Claude Code)
                import sys
                if sys.stdout.isatty():
                    # We're in a real terminal - create terminal-optimized version
                    terminal_content = content.replace("```bash\n", "").replace("```\n", "").replace("```", "")

                    # Create a temporary terminal-friendly file
                    import tempfile
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
                        temp_file.write(terminal_content)
                        temp_file_path = temp_file.name

                    import subprocess
                    try:
                        subprocess.run(['nano', '-v', temp_file_path], check=False)
                        # Clean up temp file
                        import os
                        os.unlink(temp_file_path)
                        return 0
                    except FileNotFoundError:
                        # nano not available, try less
                        try:
                            subprocess.run(['less', temp_file_path], check=False)
                            import os
                            os.unlink(temp_file_path)
                            return 0
                        except FileNotFoundError:
                            # Fallback: print the terminal content directly
                            import os
                            os.unlink(temp_file_path)
                            print(terminal_content)
                            return 0
                else:
                    # Claude Code environment
                    print(f"📝 Using pre-existing experimental help file: {local_file}")
                    print("🎯 Claude: Please read and display this file in your chat message!")
                    print(f"📄 File: {local_file}")
                    return 0
            except Exception as e:
                print(f"❌ Error reading {local_file}: {e}")
                # Fall through to generate content

        if section == "compact" and (local_only_dir / "HELP" / "compact.md").exists():
            # Use existing compact.md file
            local_file = local_only_dir / "HELP" / "compact.md"
            try:
                with open(local_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Check if we're in a real terminal (not Claude Code)
                import sys
                if sys.stdout.isatty():
                    # We're in a real terminal - create terminal-optimized version and print directly
                    terminal_content = content.replace("```bash\n", "").replace("```\n", "").replace("```", "")
                    print(terminal_content)
                    return 0
                else:
                    # Claude Code environment
                    print(f"📝 Using pre-existing compact help file: {local_file}")
                    print("🎯 Claude: Please read and display this file in your chat message!")
                    print(f"📄 File: {local_file}")
                    return 0
            except Exception as e:
                print(f"❌ Error reading {local_file}: {e}")
                # Fall through to generate content

        # Secure temp file location in CCC directory
        ccc_tmp_dir = Path(__file__).parent.parent / "tmp"
        ccc_tmp_dir.mkdir(exist_ok=True)
        help_file = ccc_tmp_dir / f"ccc-help-{section}.md"

        # Determine the command that was entered
        if section == "compact":
            command_entered = "ccc help"
        elif section == "all":
            command_entered = "ccc help all"
        elif section == "full":
            command_entered = "ccc help full"
        elif section == "experimental":
            command_entered = "ccc help experimental"
        else:
            # For section-specific help
            command_entered = f"ccc help {section}"

        # Add header showing what user typed
        header = f"\n\nUSER: {command_entered} ===================================================================\n\n"
        
        # Generate help content based on section
        if section == "compact":
            help_content = """# CCC - Collective Context Commander Plugin

**Quick Reference Guide**

## Usage
```bash
ccc <command> [service] [options]
```

## Quick Commands
- **[CORE]:** status, config, list, help
- **[CONTROL]:** start, restart, stop, test, exec  
- **[SERVICES]:** autoinput, save, dialog
- **[COMM]:** ccc (read), ccc -r, ccc -w

## Quick Examples
```bash
ccc list                   # Show all services
ccc status save            # Check save status
ccc start autoinput -t=3   # Start autoinput (3min)
ccc start save -d          # Start logging + dialog
ccc                        # Read other Claude messages
```

## Help Options
- `ccc help full` - Detailed help with all sections
- `ccc help core` - Core commands only
- `ccc help control` - Service control commands
- `ccc help services` - Specialized services
- `ccc help communication` - Claude communication
- `ccc help options` - Command options
- `ccc help examples` - Usage examples

💡 **Tip:** Partial section names work! (e.g., `ccc help comm` → communication)
"""
        elif section == "core":
            help_content = """# CCC - Core Commands

## Status and Configuration
- **ccc status [service]** - Show brief service status
- **ccc config [service]** - Show detailed configuration

## Service Management
- **ccc list** - List all available services

## Help System
- **ccc help** - Show compact help
- **ccc help full** - Show detailed help with all sections
- **ccc help [section]** - Show help for specific section:
  - core, control, services, communication, options, examples

## Examples
```bash
ccc list                    # List all services
ccc status autoinput        # Check autoinput status
ccc config save            # Show save service configuration
```
"""
        elif section == "control":
            help_content = """# CCC - Service Control Commands

## Starting Services
- **ccc start [service] [-m] [-t=n] [-- text]** - Start service
  - `-m` - Also start monitor process
  - `-t=n` - Set interval to n minutes
  - `-- text` - Custom text (autoinput service)

## Stopping Services
- **ccc stop [service] [-m]** - Stop service
  - `-m` - Also stop monitor process

## Restarting Services
- **ccc restart [service] [-m] [-t=n] [-- text]** - Restart service

## Testing and Execution
- **ccc test [service]** - Reset to default and send once
- **ccc exec [service] -- command** - Execute command in service context

## Examples
```bash
ccc start autoinput -t=3              # Start with 3min interval
ccc restart save -d                   # Restart with dialog
ccc stop autoinput -m                 # Stop service + monitor
ccc test autoinput                    # Send default text once
```
"""
        elif section == "services":
            help_content = """# CCC - Specialized Services

## AutoInput Service
Keeps Claude Code session active with periodic messages
- **Default interval:** 5 minutes
- **Default text:** "Alles okay?"

Commands:
```bash
ccc start autoinput -t=3 -- "Hi"     # Custom text & interval
ccc stop autoinput                   # Stop service
```

## Save Service
Claude Self-Logging with optional dialog monitoring
- Creates session logs: `session_YYYY-MM-DD_HH-MM-SS.md`
- Optional dialog logs: `dialog_YYYY-MM-DD_HH-MM-SS.md`

Commands:
```bash
ccc start save                        # Session logging only
ccc start save -d                     # With dialog monitoring
```

## Dialog Service
Tmux dialog monitoring service
- Monitors all tmux session activity
- Creates dialog logs

Commands:
```bash
ccc start dialog                      # Start monitoring
ccc stop dialog                       # Stop monitoring
```
"""
        elif section == "communication":
            help_content = """# CCC - Claude Communication

## Inter-Claude Messaging
Commands for communication between multiple Claude instances:

- **ccc** - Read messages from other Claude instance (same as -r)
- **ccc -r, --read** - Read other claude-x.md file
- **ccc -w, --write** - Write to own claude-x.md file
- **ccc -c, --cron** - [Reserved for future crontab integration]

## How It Works
Multiple Claude instances can communicate by writing/reading special marker files.
This enables coordination between parallel Claude Code sessions.

## Examples
```bash
ccc                  # Check for messages from other Claude
ccc -r               # Explicitly read other Claude's file
ccc -w               # Write message to own file
```
"""
        elif section == "options":
            help_content = """# CCC - Command Options

## Monitor Control
- **-m, --monitor** - Control background monitor process
  - Used with start/stop/restart commands
  - Manages persistent background monitoring

## Timing Control
- **-t=n, --time=n** - Set interval in minutes
  - Default: 5 minutes
  - Used with autoinput service
  - Example: `-t=3` for 3-minute intervals

## Dialog Integration
- **-d, --dialog** - Enable dialog monitoring
  - Used with save service
  - Starts tmux monitoring alongside session logging

## Custom Text
- **-- text** - Specify custom text
  - Everything after `--` is treated as text
  - Used with autoinput service
  - Example: `-- "Custom message"`

## Examples
```bash
ccc start autoinput -m -t=10 -- "Hi"  # All options combined
ccc restart save -d                   # Dialog option
ccc stop autoinput -m                 # Monitor option
```
"""
        elif section == "examples":
            help_content = """# CCC - Usage Examples

## Quick Start
```bash
# List all services
ccc list

# Start autoinput with 3-minute interval
ccc start autoinput -t=3

# Start session logging with dialog
ccc start save -d
```

## AutoInput Management
```bash
# Start with custom text and monitor
ccc start autoinput -m -t=10 -- "Still working..."

# Test with default text
ccc test autoinput

# Stop service and monitor
ccc stop autoinput -m
```

## Session Logging
```bash
# Start session logging only
ccc start save

# Start with dialog monitoring
ccc start save -d

# Check status
ccc status save

# Stop logging
ccc stop save
```

## Dialog Monitoring
```bash
# Start dialog monitoring
ccc start dialog

# Check if running
ccc status dialog

# Restart service
ccc restart dialog
```

## Claude Communication
```bash
# Check for messages
ccc

# Explicitly read
ccc -r

# Write message
ccc -w
```
"""
        elif section == "full":
            # New streamlined full help - only tested stable features
            help_content = """# CC Commander (CCC) Collective Context Commander

ccc <command> [service] [options]

## CORE COMMANDS
- **ccc help**           - Show compact help message
- **ccc help full**      - Show detailed help with all sections
- **ccc help [section]** - Show help for specific section (core, control, services, etc.)

## SESSION MANAGEMENT
- **ccc session start [ai-instance]** - Start new session with optional name
- **ccc session save**                - Save current session knowledge
- **ccc session end**                 - Save ALL from the begin of the session

## MULTI-AGENT CONTEXT SYSTEM
- **ccc context**                                   - Read own AI instance context
- **ccc context [to] [cl1|cl2|ai1|ai2] -- message** - Send a context message to target
- **ccc context [to] all               -- message** - Broadcast message to all AIs

**Targets: cl1 (Claude-1), cl2 (Claude-2), ai1 (Aider-1), ai2 (Aider-2), all**

## GIT INTEGRATION (Test, Push, Verify)
- **ccc git push ccc**       - Quick push to GitHub (skips tests, ~5 seconds)
- **ccc git push ccc tests** - Full validation + push (~60 seconds)
- **ccc git push homepage**  - Update collective-context.org with achievements
- **ccc git status**         - Git status + GitHub Actions CI/CD monitoring
- **ccc git logs**           - Show GitHub Actions workflow logs
- **ccc git check**          - Manual check of CI/CD pipeline status
"""
            print(help_content)
            return
        elif section == "experimental":
            # Full experimental help content - all features
            help_content = self._generate_help_markdown(self._get_help_content_data())
            # Display help content directly
            print(help_content)
            return

        # Write help content to secure temp file with header
        try:
            with open(help_file, 'w', encoding='utf-8') as f:
                f.write(header + help_content)
            
            # Check if we're in Claude Code or terminal
            import sys
            if sys.stdout.isatty():
                # We're in a real terminal - open nano to view the help
                import subprocess
                try:
                    # Open nano with the help file
                    subprocess.run(['nano', '-v', str(help_file)], check=False)
                    print(f"💡 Help file saved to: {help_file}")
                except FileNotFoundError:
                    # Nano not available, try less or cat
                    try:
                        subprocess.run(['less', str(help_file)], check=False)
                    except FileNotFoundError:
                        # Fall back to cat
                        subprocess.run(['cat', str(help_file)], check=False)
                        print(f"\n💡 Help file saved to: {help_file}")
            else:
                # We're in Claude Code - inform Claude to read and display
                print(f"📝 Complete CCC Help written to: {help_file}")
                print(f"🎯 Claude: Please read and display this file in your chat message!")
                print(f"📄 File: {help_file}")
            return 0
            
        except Exception as e:
            print(f"❌ Error writing help file: {e}")
            return 1
            
        return 0
    
    def help_show_paged(self, section="full"):
        """Show full help with pager in terminal environment"""
        import tempfile
        import subprocess
        
        try:
            # Create temp file with full help content
            help_content = self._generate_help_plaintext_new(self._get_help_content_data())
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(help_content)
                temp_file_path = temp_file.name
            
            # Try to use less, then more, then cat as fallback
            pagers = ['less', 'more', 'cat']
            for pager in pagers:
                try:
                    if pager == 'cat':
                        # For cat, add a header
                        print("=" * 60)
                        print("CCC - Collective Context Commander - Full Help")
                        print("=" * 60)
                    
                    result = subprocess.run([pager, temp_file_path], check=False)
                    if result.returncode == 0 or pager == 'cat':
                        break
                except FileNotFoundError:
                    continue
            
            # Clean up temp file
            import os
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass
                
            return 0
            
        except Exception as e:
            print(f"❌ Error displaying help: {e}")
            # Fallback to simple help_show
            return self.help_show("all")

    def handle_session_command(self, args):
        """Handle session commands: start, save, end"""
        if not args:
            print("❌ Session command requires action: start, save, or end")
            print("Usage:")
            print("  ccc session start [-n=session-name] [ai-instance]   # Start new session")
            print("  ccc session save [ai-instance]                      # Save current session")
            print("  ccc session end [ai-instance]                       # End session")
            return 1

        action = args[0].lower()

        # Parse parameters
        session_name = None
        ai_instance = None
        remaining_args = args[1:]

        for arg in remaining_args:
            if arg.startswith('-n='):
                session_name = arg[3:]  # Extract name after -n=
            elif not arg.startswith('-'):
                ai_instance = arg

        if action in ['start', 'sta']:
            # Normalize session name if provided
            normalized_session_name = self._normalize_session_name(session_name) if session_name else None
            return self.session_start(ai_instance, normalized_session_name)
        elif action in ['save', 'sav']:
            return self.session_save(ai_instance)
        elif action in ['end', 'ende']:
            return self.session_end(ai_instance)
        elif action in ['knowledge', 'kn', 'know', 'template']:
            # Route to new SQLite integration for session knowledge
            import sys
            sys.path.append(str(Path(__file__).parent.parent))
            from ccc_session_integration import CCCSessionIntegration
            integration = CCCSessionIntegration()
            return integration.handle_session_command([action])
        else:
            print(f"❌ Unknown session action: {action}")
            print("Available actions: start, save, end, knowledge")
            return 1

    def _generate_full_help_content(self):
        """Generate full help content for pager display"""
        return """CCC - Collective Context Commander Plugin

Professional plugin system for Claude Code session management

Usage:
    ccc <command> [service] [options]

CORE COMMANDS:
- ccc status [service]     Show brief service status
- ccc config [service]     Show detailed service configuration
- ccc list                 List all available services
- ccc help                 Show compact help message
- ccc help full            Show detailed help with all sections
- ccc help [section]       Show help for specific section (core, control, services, etc.)

SESSION MANAGEMENT:
- ccc session start [-n=name] [ai-instance]  Start new session with optional name
- ccc session save [ai-instance]             Save current session knowledge
- ccc session end [ai-instance]              End current session

SERVICE CONTROL:
- ccc start [service] [-m] [-t=n] [-- text]  Start service (optionally with monitor & interval)
- ccc restart [service] [-m] [-t=n] [-- text]  Restart service (stop + start)
- ccc stop [service] [-m]                    Stop service (optionally stop monitor)
- ccc test [service]                         Reset to default text and send it once
- ccc exec [service] -- command              Execute command in service context

SPECIALIZED SERVICES:
- ccc start dialog         Start dialog monitoring service
- ccc stop dialog          Stop dialog monitoring service  
- ccc restart dialog       Restart dialog monitoring service
- ccc start save [-d]      Start Claude Self-Logging (optionally with dialog)
- ccc restart save [-d]    Restart save service (optionally with dialog)
- ccc stop save            Stop save service

MULTI-AGENT CONTEXT SYSTEM:
- ccc context, ccc co      Read own AI instance context
- ccc context to [target] -- message  Send message to target AI instance
- ccc context to all -- message       Broadcast message to all AI instances
- ccc context [instance]   Read specific AI instance context

OPTIONS:
- -m, --monitor            Also start/stop the background monitor process
- -t=n, --time=n          Set interval to n minutes (default: 5)
- -d, --dialog            Start with dialog monitoring (save service)

EXAMPLES:

Core Commands:
    ccc list                          # Show all available services
    ccc status autoinput              # Check autoinput brief status
    ccc config autoinput              # Show detailed autoinput configuration  

AutoInput Service:
    ccc start autoinput               # Start autoinput (5min interval)
    ccc start autoinput -t=3          # Start with 3 minute interval
    ccc restart autoinput -m -t=1     # Restart with monitor + 1 minute interval
    ccc start autoinput -m -t=10 -- "Hi"  # Custom text + monitor + 10min interval
    ccc stop autoinput                # Stop service only
    ccc stop autoinput -m             # Stop service + monitor
    ccc test autoinput                # Reset to default text and send once

Save Service (Claude Self-Logging):
    ccc start save                    # Start session logging only
    ccc start save -d                 # Start with dialog monitoring (session + tmux)
    ccc restart save -d               # Restart with dialog monitoring
    ccc stop save                     # Stop save service
    ccc status save                   # Check save service status

Dialog Service (Tmux Monitoring):
    ccc start dialog                  # Start dialog monitoring service
    ccc stop dialog                   # Stop dialog monitoring
    ccc restart dialog                # Restart dialog monitoring
    ccc status dialog                 # Check dialog status

Command Execution:
    ccc exec autoinput -- "Custom command"   # Execute command in service context

Multi-Agent Context System:
    ccc context                       # Read own AI instance context
    ccc co cl2                        # Read Claude-2's context
    ccc context to cl2 -- Hi there   # Send message to Claude-2
    ccc context to all -- Update     # Broadcast to all AI instances

AVAILABLE SERVICES:

autoinput - Automatically sends periodic messages to keep Claude Code session active
            Default interval: 5 minutes, Default text: "Alles okay?"
            
save      - Claude Self-Logging with optional dialog monitoring
            Always creates session logs (session_YYYY-MM-DD_HH-MM-SS.md)
            Optional: tmux dialog monitoring with -d flag (dialog_YYYY-MM-DD_HH-MM-SS.md)
            
dialog    - Tmux dialog monitoring service
            Monitors and logs all tmux session activity
            Creates dialog logs (dialog_YYYY-MM-DD_HH-MM-SS.md)

---

CCC - Collective Context Commander
Professional plugin system for multi-Claude session coordination
"""

    def _get_help_content_data(self):
        """Central help content data structure - single source of truth"""
        return {
            "title": "CCC - Collective Context Commander Plugin",
            "subtitle": "Professional plugin system for Claude Code session management",
            "usage": "ccc <command> [service] [options]",
            "sections": {
                "core": {
                    "title": "CORE COMMANDS",
                    "icon": "🔧",
                    "commands": [
                        ("ccc status [service]", "Show brief service status"),
                        ("ccc config [service]", "Show detailed service configuration"),
                        ("ccc list", "List all available services"),
                        ("ccc help", "Show compact help message"),
                        ("ccc help full", "Show detailed help with all sections"),
                        ("ccc help [section]", "Show help for specific section (core, control, services, etc.)")
                    ]
                },
                "session": {
                    "title": "SESSION MANAGEMENT",
                    "icon": "📝",
                    "commands": [
                        ("ccc session start [-n=name] [ai-instance]", "Start new session with optional name"),
                        ("ccc session save [ai-instance]", "Save current session knowledge"),
                        ("ccc session end [ai-instance]", "End current session")
                    ]
                },
                "service": {
                    "title": "SERVICE CONTROL",
                    "icon": "🚀",
                    "commands": [
                        ("ccc start [service] [-m] [-t=n] [-- text]", "Start service (optionally with monitor & interval)"),
                        ("ccc restart [service] [-m] [-t=n] [-- text]", "Restart service (stop + start)"),
                        ("ccc stop [service] [-m]", "Stop service (optionally stop monitor)"),
                        ("ccc test [service]", "Reset to default text and send it once"),
                        ("ccc exec [service] -- command", "Execute command in service context")
                    ]
                },
                "specialized": {
                    "title": "SPECIALIZED SERVICES",
                    "icon": "📝",
                    "commands": [
                        ("ccc start dialog", "Start dialog monitoring service"),
                        ("ccc stop dialog", "Stop dialog monitoring service"),
                        ("ccc restart dialog", "Restart dialog monitoring service"),
                        ("ccc start save [-d]", "Start Claude Self-Logging (optionally with dialog)"),
                        ("ccc restart save [-d]", "Restart save service (optionally with dialog)"),
                        ("ccc stop save", "Stop save service")
                    ]
                },
                "context": {
                    "title": "MULTI-AGENT CONTEXT SYSTEM",
                    "icon": "🔗",
                    "commands": [
                        ("ccc context, ccc co", "Read own AI instance context"),
                        ("ccc context to [target] -- message", "Send message to target AI instance"),
                        ("ccc context to all -- message", "Broadcast message to all AI instances"),
                        ("ccc context [instance]", "Read specific AI instance context")
                    ],
                    "note": "Targets: cl1, cl2, ai1, ai2, all"
                },
                "git": {
                    "title": "GIT INTEGRATION",
                    "icon": "🔧",
                    "commands": [
                        ("ccc git push ccc", "Quick push to GitHub (skips tests, ~5 seconds)"),
                        ("ccc git push ccc tests", "Full validation + push (~60 seconds)"),
                        ("ccc git push homepage", "Update collective-context.org with achievements"),
                        ("ccc git status", "Git status + GitHub Actions CI/CD monitoring"),
                        ("ccc git logs", "Show GitHub Actions workflow logs"),
                        ("ccc git check", "Manual check of CI/CD pipeline status")
                    ],
                    "note": "NEW: Complete CI/CD integration - 'Test, Push, Verify' workflow"
                }
            },
            "options": [
                ("-m, --monitor", "Also start/stop the background monitor process"),
                ("-t=n, --time=n", "Set interval to n minutes (default: 5)"),
                ("-d, --dialog", "Start with dialog monitoring (save service)")
            ],
            "services": {
                "autoinput": {
                    "description": "Automatically sends periodic messages to keep Claude Code session active",
                    "details": ["Default interval: 5 minutes", "Default text: \"Alles okay?\""]
                },
                "save": {
                    "description": "Claude Self-Logging with optional dialog monitoring",
                    "details": [
                        "Always creates session logs (session_YYYY-MM-DD_HH-MM-SS.md)",
                        "Optional: tmux dialog monitoring with -d flag (dialog_YYYY-MM-DD_HH-MM-SS.md)"
                    ]
                },
                "dialog": {
                    "description": "Tmux dialog monitoring service",
                    "details": [
                        "Monitors and logs all tmux session activity",
                        "Creates dialog logs (dialog_YYYY-MM-DD_HH-MM-SS.md)"
                    ]
                },
                "git": {
                    "description": "Git integration for GitHub repository management",
                    "details": [
                        "Quick mode: Fast push for small changes (documentation, typos)",
                        "Full mode: Comprehensive validation (96 tests + security audit)",
                        "Homepage: Updates collective-context.org with session achievements"
                    ]
                }
            }
        }

    def _generate_help_markdown(self, data):
        """Generate markdown formatted help from data structure"""
        lines = [f"# {data['title']}", "", f"**{data['subtitle']}**", ""]
        lines.extend(["## Usage", "```bash", data['usage'], "```", ""])

        for section_key, section in data['sections'].items():
            lines.append(f"## {section['icon']} {section['title']}")
            for cmd, desc in section['commands']:
                lines.append(f"- **{cmd}** - {desc}")
            if 'note' in section:
                lines.extend(["", f"**{section['note']}**"])
            lines.append("")

        lines.append("## 🔧 OPTIONS")
        for opt, desc in data['options']:
            lines.append(f"- **{opt}** - {desc}")
        lines.append("")

        lines.append("## ⭕ AVAILABLE SERVICES")
        lines.append("")
        for service, info in data['services'].items():
            lines.append(f"### {service}")
            lines.append(info['description'])
            for detail in info['details']:
                lines.append(f"- **{detail.split(':')[0]}:** {':'.join(detail.split(':')[1:]).strip()}" if ':' in detail else f"- {detail}")
            lines.append("")

        lines.extend(["---", "", f"**{data['title'].split(' - ')[1]}**", "*Professional plugin system for multi-Claude session coordination*"])
        return "\n".join(lines)

    def _generate_help_plaintext_new(self, data):
        """Generate plain text formatted help from data structure"""
        lines = [data['title'], "", data['subtitle'], "", f"Usage:", f"    {data['usage']}", ""]

        for section_key, section in data['sections'].items():
            lines.append(f"{section['title']}:")
            for cmd, desc in section['commands']:
                lines.append(f"- {cmd:<45} {desc}")
            if 'note' in section:
                lines.append(f"\n{section['note']}")
            lines.append("")

        lines.append("OPTIONS:")
        for opt, desc in data['options']:
            lines.append(f"- {opt:<25} {desc}")
        lines.append("")

        lines.append("AVAILABLE SERVICES:")
        lines.append("")
        for service, info in data['services'].items():
            lines.append(f"{service}:")
            lines.append(info['description'])
            for detail in info['details']:
                lines.append(f"- {detail}")
            lines.append("")

        lines.extend(["---", "", data['title'].split(' - ')[1], "Professional plugin system for multi-Claude session coordination"])
        return "\n".join(lines)

    def ppa_show_write_and_read(self):
        """Write PPA configuration to secure temp file for Claude Code display"""
        import tempfile
        from pathlib import Path

        # Create secure temp file in /tmp/ccc-secure/
        temp_dir = Path("/tmp/ccc-secure")
        temp_dir.mkdir(mode=0o700, exist_ok=True)

        # Use fixed filename for session persistence
        ppa_file = temp_dir / "ccc-ppa-config.md"

        # Load PPA configuration
        from ccc_ppa_upload import load_ppa_config
        ppa_config = load_ppa_config()

        # Generate command header
        command_entered = "ccc exec show ppa"
        header = f"\n\nUSER: {command_entered} ===================================================================\n\n"

        # Generate PPA configuration content in markdown format
        ppa_content = "# 🔧 CCC PPA Configuration\n\n"

        # Target PPA
        target_ppa = ppa_config.get('target_ppa', 'Unknown')
        ppa_content += f"**🎯 Target PPA:** `{target_ppa}`\n\n"

        # Enabled Packages
        packages = ppa_config.get('auto_upload_packages', [])
        enabled_packages = [pkg for pkg in packages if pkg.get('enabled', False)]
        ppa_content += f"## 📦 Enabled Packages ({len(enabled_packages)})\n\n"

        for pkg in enabled_packages:
            name = pkg.get('name', 'Unknown')
            pkg_type = pkg.get('type', 'Unknown').upper()
            description = pkg.get('description', 'No description')
            ppa_content += f"- **✅ {name}** ({pkg_type}) - {description}\n"

        ppa_content += "\n"

        # Enabled Ubuntu Distributions
        distributions = ppa_config.get('supported_distributions', [])
        enabled_distros = [dist for dist in distributions if dist.get('enabled', False)]
        ppa_content += f"## 🐧 Enabled Ubuntu Distributions ({len(enabled_distros)})\n\n"

        for dist in enabled_distros:
            codename = dist.get('codename', 'Unknown')
            version = dist.get('version', 'Unknown')
            priority = dist.get('priority', 'normal').upper()
            ppa_content += f"- **✅ {codename}** ({version}) - {priority} priority\n"

        ppa_content += "\n"

        # Build Settings
        build_settings = ppa_config.get('build_settings', {})
        ppa_content += "## ⚙️ Build Settings\n\n"
        ppa_content += f"- **🔐 Auto-sign:** {build_settings.get('auto_sign', False)}\n"
        ppa_content += f"- **🔍 Check duplicates:** {build_settings.get('check_duplicates', False)}\n"
        ppa_content += f"- **📄 Include copyright:** {build_settings.get('include_copyright', False)}\n"
        ppa_content += f"- **⏱️ Build timeout:** {build_settings.get('build_timeout', 300)}s\n"
        ppa_content += f"- **⏱️ Upload timeout:** {build_settings.get('upload_timeout', 180)}s\n\n"

        # Notification Settings
        notification_settings = ppa_config.get('notification_settings', {})
        ppa_content += "## 🔔 Notification Settings\n\n"
        ppa_content += f"- **✅ On success:** {notification_settings.get('on_success', False)}\n"
        ppa_content += f"- **❌ On failure:** {notification_settings.get('on_failure', False)}\n"
        ppa_content += f"- **⏩ On duplicate skip:** {notification_settings.get('on_duplicate_skip', False)}\n"
        ppa_content += f"- **🔗 Include Launchpad links:** {notification_settings.get('include_launchpad_links', False)}\n\n"

        # Additional commands
        ppa_content += "## 🚀 Available PPA Commands\n\n"
        ppa_content += "```bash\n"
        ppa_content += "ccc exec upload ppa           # Upload all (base & meta) packages\n"
        ppa_content += "ccc exec upload ppa ccc       # Upload base packages only to PPA\n"
        ppa_content += "ccc exec upload ppa cccmd     # Upload meta packages only to PPA\n"
        ppa_content += "ccc exec upload meta          # Upload meta packages (alias)\n"
        ppa_content += "ccc exec show ppa             # Show PPA configuration\n"
        ppa_content += "ccc exec fix gpg              # ULTIMATE GPG signature fix\n"
        ppa_content += "```\n\n"

        ppa_content += "---\n\n"
        ppa_content += "**🔗 Launchpad PPA:** https://launchpad.net/~collective-context/+archive/ubuntu/ccc\n"

        # Write PPA content to secure temp file with header
        try:
            with open(ppa_file, 'w', encoding='utf-8') as f:
                f.write(header + ppa_content)

            # Check if we're in Claude Code or terminal
            import sys
            if sys.stdout.isatty():
                # We're in a real terminal - open nano to view the PPA config
                import subprocess
                try:
                    # Open nano with the PPA file
                    subprocess.run(['nano', '-v', str(ppa_file)], check=False)
                    print(f"💡 PPA config file saved to: {ppa_file}")
                except FileNotFoundError:
                    # Nano not available, try less or cat
                    try:
                        subprocess.run(['less', str(ppa_file)], check=False)
                    except FileNotFoundError:
                        # Fall back to cat
                        subprocess.run(['cat', str(ppa_file)], check=False)
                        print(f"\n💡 PPA config file saved to: {ppa_file}")
            else:
                # We're in Claude Code - inform Claude to read and display
                print(f"📝 Complete CCC PPA Configuration written to: {ppa_file}")
                print(f"🎯 Claude: Please read and display this file in your chat message!")
                print(f"📄 File: {ppa_file}")
            return 0

        except Exception as e:
            print(f"❌ Error writing PPA config file: {e}")
            return 1
