#!/usr/bin/env python3
"""
CCC - Collective Context Commander Entry Point for pip/pipx installation
"""

import sys
import os
from pathlib import Path

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent / "lib"))

# Import all necessary modules and functions from ccc script
from ccc_manager import CCCManager
from ccc_commands import Commands
from ccc_ppa_upload import upload_ppa_command
from ccc_command_parser import CommandParser

def is_claude_code_environment():
    """Detect if running in Claude Code environment"""
    # Check for explicit Claude Code markers first
    if os.environ.get('CLAUDE_CODE') == '1':
        return True

    # Check for known terminal environments (these are NOT Claude Code)
    terminal_indicators = [
        os.environ.get('TERM_PROGRAM'),  # tmux, screen, etc.
        os.environ.get('SSH_CLIENT'),     # SSH session
        os.environ.get('SSH_TTY'),        # SSH TTY
    ]
    if any(terminal_indicators):
        return False

    # Check for terminal types that indicate real terminals
    term = os.environ.get('TERM', '')
    if any(term.startswith(prefix) for prefix in ['tmux', 'screen', 'xterm', 'rxvt', 'gnome']):
        return False

    # Check for dumb terminal or completely missing TTY (likely Claude Code)
    if (os.environ.get('TERM') == 'dumb' or
        (not sys.stdout.isatty() and os.environ.get('TERM_PROGRAM') is None)):
        return True

    # Default: assume terminal environment if we have a TTY
    return not sys.stdout.isatty()

def print_compact_usage():
    """Print compact usage information for Claude Code"""
    print("""
CCC - Collective Context Commander Plugin
Usage: ccc <command> [service] [options]

[CORE]: status, config, list, help
[CONTROL]: start, restart, stop, test, exec
[SERVICES]: autoinput, save, dialog
[COMM]: ccc (read), ccc -r, ccc -w

Quick Examples:
  ccc list                   # Show all services
  ccc status save            # Check save status
  ccc start autoinput -t=3   # Start autoinput (3min)
  ccc start save -d          # Start logging + dialog
  ccc                        # Read other Claude messages

Help Options:
  ccc help full              # Detailed help with all sections
  ccc help core              # Core commands only
  ccc help control           # Service control commands
  ccc help services          # Specialized services
  ccc help communication     # Claude communication
  ccc help options           # Command options
  ccc help examples          # Usage examples

TIP: Partial names work! (e.g., 'ccc help comm' for communication)
""")

def main():
    """Entry point for pip/pipx installation - flexible abbreviation system"""
    import sys

    # Initialize CCC manager, commands, and parser
    manager = CCCManager()
    commands = Commands(manager)
    parser = CommandParser()

    # Handle no arguments - show help
    if len(sys.argv) <= 1:
        mode, path = detect_current_mode()
        print(f"CCC Commander (cc/ccc/cccmd) v0.3.2 {mode} - Multi-Agent AI Orchestration")
        print("\nVerfügbare Commands (mit flexiblen Abkürzungen):")
        print("  ve[rsion]        - Zeige Version und Installation")
        print("  he[lp]           - Zeige diese Hilfe")
        print("  co[ntext]        - Context Management")
        print("  se[ssion]        - Session Management")
        print("  gi[t] pu[sh] ho[mepage]     - Update collective-context.org")
        print("  gi[t] pu[sh] cc[c] [te[sts]] - Push to GitHub (optional: with tests)")
        print("  ex[ec] up[load] pp[a]       - Upload packages to Ubuntu PPA")
        print("  co[nfig] sh[ow]             - Show current configuration")
        print("  co[nfig] -- set eMail=...   - Set email configuration")
        print("\n💡 Mindestens 2 Buchstaben pro Befehl. Beispiel: 'cc gi pu ccc te'")
        print("🔗 Für detaillierte Hilfe siehe: https://collective-context.org/ccc/")
        return 0

    # Parse command with flexible abbreviations
    original_args = sys.argv[1:]
    expanded_commands, free_string, success = parser.parse_command(original_args)

    if not success:
        return 1

    # Display expansion if commands were abbreviated
    parser.display_expansion(original_args, expanded_commands, free_string)

    # Validate command chain
    if not parser.validate_command_chain(expanded_commands):
        print(f"❌ Invalid command sequence: {' '.join(expanded_commands)}")
        print("💡 Use 'ccc help' for valid command patterns")
        return 1

    try:
        # Route commands to appropriate handlers
        if expanded_commands[0] in ['help']:
            print("CCC Commander (cccmd) v0.3.2 - Multi-Agent AI Orchestration")
            print("\nVerfügbare Commands (mit flexiblen Abkürzungen):")
            print("  ve[rsion]        - Zeige Version")
            print("  he[lp]           - Zeige diese Hilfe")
            print("  co[ntext]        - Context Management")
            print("  se[ssion]        - Session Management")
            print("  gi[t] pu[sh] ho[mepage]     - Update collective-context.org")
            print("  gi[t] pu[sh] cc[c] [te[sts]] - Push to GitHub (optional: with tests)")
            print("  ex[ec] up[load] pp[a]       - Upload packages to Ubuntu PPA")
            print("  co[nfig] sh[ow]             - Show current configuration")
            print("  co[nfig] -- set eMail=...   - Set email configuration")
            print("\n💡 Mindestens 2 Buchstaben pro Befehl. Beispiel: 'cc gi pu ccc te'")
            print("🔗 Für detaillierte Hilfe siehe: https://collective-context.org/ccc/")
            return 0

        elif expanded_commands[0] == 'version' or (len(expanded_commands) >= 2 and expanded_commands[0] == 'ccc' and expanded_commands[1] == 'version'):
            # Use file-based approach like help full
            return commands.version_write_and_read()

        elif expanded_commands[0] == 'config':
            return handle_config_command(expanded_commands, free_string, manager)

        elif expanded_commands[0] == 'context':
            if len(expanded_commands) > 1:
                commands.handle_context_command(expanded_commands[1:])
            else:
                commands.handle_context_command([])
            return 0

        elif expanded_commands[0] == 'session':
            if len(expanded_commands) > 1:
                commands.handle_session_command(expanded_commands[1:])
            else:
                commands.handle_session_command([])
            return 0

        elif expanded_commands[0] == 'git':
            return handle_git_command(expanded_commands, free_string, commands)

        elif expanded_commands[0] == 'exec':
            return handle_exec_command(expanded_commands, manager)

        else:
            print(f"❌ Unknown command: {expanded_commands[0]}")
            print("Use 'ccc help' for available commands")
            return 1

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

def detect_current_mode():
    """Detect which mode CCC is currently running in"""
    import sys
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

def handle_config_command(expanded_commands, free_string, manager):
    """Handle config commands with free string support"""
    if free_string:
        # Handle config set commands from free string
        if free_string.startswith('set '):
            set_command = free_string[4:]  # Remove 'set '

            if '=' in set_command:
                key, value = set_command.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"\'')

                if key == 'eMail' or key == 'email':
                    manager.config['email'] = value
                    manager.save_config()
                    print(f"✅ Email configured: {value}")
                    return 0
                else:
                    print(f"❌ Unknown config key: {key}")
                    print("Available keys: eMail")
                    return 1
            else:
                print("❌ Invalid set command. Use: config -- set eMail=\"your@email.com\"")
                return 1
        else:
            print("❌ Invalid config command. Use: config -- set key=value")
            return 1
    elif len(expanded_commands) == 1 or (len(expanded_commands) == 2 and expanded_commands[1] == 'show'):
        # Show current configuration
        print("\n📋 CCC Configuration")
        print("=" * 50)

        config_file = manager.config.get('_config_source', 'Unknown')
        print(f"📁 Config file: {config_file}")

        # Show email if configured
        email = manager.config.get('email', 'Not configured')
        print(f"📧 Email: {email}")

        # Show version management
        vm = manager.config.get('version_management', {})
        preferred_mode = vm.get('preferred_mode', 'Unknown')
        print(f"🔧 Preferred mode: {preferred_mode}")

        print("=" * 50)
        return 0
    else:
        print("❌ Config command requires 'show' or '-- set key=value'")
        return 1

def handle_git_command(expanded_commands, free_string, commands):
    """Handle git commands"""
    if len(expanded_commands) >= 3 and expanded_commands[1] == 'push':
        if expanded_commands[2] == 'homepage':
            return commands.git_push_homepage(free_string)
        elif expanded_commands[2] == 'ccc':
            # Check if tests flag is provided
            run_tests = len(expanded_commands) > 3 and expanded_commands[3] in ['test', 'tests', 'full']
            return commands.git_push_ccc(run_tests=run_tests, message=free_string)

    print("❌ Available git commands:")
    print("  gi[t] pu[sh] ho[mepage]     - Update collective-context.org")
    print("  gi[t] pu[sh] cc[c]          - Quick push to GitHub")
    print("  gi[t] pu[sh] cc[c] te[sts]  - Full validation & push")
    return 1

def handle_exec_command(expanded_commands, manager):
    """Handle exec commands"""
    if len(expanded_commands) >= 3:
        if expanded_commands[1] == 'upload' and expanded_commands[2] == 'ppa':
            return upload_ppa_command(manager)
        elif expanded_commands[1] == 'fix' and expanded_commands[2] == 'gpg':
            from ccc_ultimate_gpg_fix import fix_all_packages
            fix_all_packages()
            return 0

    print("❌ Available exec commands:")
    print("  ex[ec] up[load] pp[a]    - Upload packages to PPA")
    print("  ex[ec] fi[x] gp[g]       - ULTIMATE GPG signature fix")
    return 1


if __name__ == "__main__":
    sys.exit(main())