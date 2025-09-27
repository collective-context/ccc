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
from ccc_config_extended import CCCConfigExtended

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
        print(f"CCC Commander (cc/ccc/cccmd) v0.3.4 {mode} - Multi-Agent AI Orchestration")
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

    # Check if this is a short version command to combine expansion with output
    is_short_version = (expanded_commands[0] == 'version' and len(expanded_commands) == 1) or \
                      (len(expanded_commands) >= 2 and expanded_commands[0] == 'ccc' and expanded_commands[1] == 'version' and len(expanded_commands) == 2)

    # Display expansion if commands were abbreviated (but not for short version)
    if not is_short_version:
        parser.display_expansion(original_args, expanded_commands, free_string)

    # Validate command chain
    if not parser.validate_command_chain(expanded_commands):
        print(f"❌ Invalid command sequence: {' '.join(expanded_commands)}")
        print("💡 Use 'ccc help' for valid command patterns")
        return 1

    try:
        # Route commands to appropriate handlers
        if expanded_commands[0] == 'help' or (len(expanded_commands) >= 2 and expanded_commands[0] == 'ccc' and expanded_commands[1] == 'help'):
            if len(expanded_commands) >= 2 and expanded_commands[-1] == 'full':
                # Help full command - use file-based approach
                return commands.help_write_and_read("full")
            elif len(expanded_commands) >= 2 and expanded_commands[-1] == 'experimental':
                # Help experimental command - use file-based approach
                return commands.help_write_and_read("experimental")
            else:
                # Standard help
                print("CCC Commander (cccmd) v0.3.4 - Multi-Agent AI Orchestration")
                print("\nVerfügbare Commands (mit flexiblen Abkürzungen):")
                print("  ve[rsion]        - Zeige Version")
                print("  he[lp]           - Zeige diese Hilfe")
                print("  he[lp] fu[ll]    - Zeige vollständige Hilfe")
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
            # Check if full version is requested
            is_full = False
            if expanded_commands[0] == 'version' and len(expanded_commands) >= 2 and expanded_commands[1] == 'full':
                is_full = True
            elif len(expanded_commands) >= 3 and expanded_commands[0] == 'ccc' and expanded_commands[1] == 'version' and expanded_commands[2] == 'full':
                is_full = True

            if is_full:
                # Use file-based approach for full version
                return commands.version_write_and_read()
            else:
                # Show short version directly in terminal
                return show_short_version(manager, original_args, expanded_commands)

        elif expanded_commands[0] == 'config' or (len(expanded_commands) >= 2 and expanded_commands[0] == 'ccc' and expanded_commands[1] == 'config'):
            # Handle both 'config' and 'ccc config' patterns
            if expanded_commands[0] == 'ccc':
                # Remove 'ccc' prefix for processing
                config_commands = expanded_commands[1:]
            else:
                config_commands = expanded_commands
            return handle_config_command(config_commands, free_string, manager)

        elif expanded_commands[0] == 'context':
            if len(expanded_commands) > 1:
                commands.handle_context_command(expanded_commands[1:])
            else:
                commands.handle_context_command([])
            return 0

        elif expanded_commands[0] == 'session':
            if len(expanded_commands) > 1:
                return commands.handle_session_command(expanded_commands[1:])
            else:
                return commands.handle_session_command([])

        elif expanded_commands[0] == 'git':
            return handle_git_command(expanded_commands, free_string, commands)

        elif expanded_commands[0] == 'exec':
            return handle_exec_command(expanded_commands, manager, commands)

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

    # Try to load user preference from config first
    try:
        from ccc_manager import CCCManager
        manager = CCCManager()
        preferred_mode = manager.config.get('version_management', {}).get('preferred_mode', '').lower()
        available_modes = manager.config.get('version_management', {}).get('available_modes', {})

        # If user has set a preferred mode and the corresponding path exists, use it
        if preferred_mode and preferred_mode in available_modes:
            import os
            preferred_path = available_modes[preferred_mode]
            if os.path.exists(preferred_path):
                return preferred_mode.upper(), preferred_path
    except:
        # If config loading fails, fall back to path detection
        pass

    # Fallback: Check if running from source (DEV mode)
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

def show_short_version(manager, original_args, expanded_commands):
    """Show compact 3-line version information without expansion noise"""
    mode, path = detect_current_mode()

    # Don't show expansion for short commands - just show the result directly
    print("USER: ccc version =====================================================================")
    print(f"{mode} Mode (v0.3.4)    # Path: {path}")
    print("ccc config mode apt  # Switch to APT/PIP/DEV version")
    return 0

def handle_config_command(expanded_commands, free_string, manager):
    """Handle config commands with extended functionality"""
    # Initialize extended config system
    extended_config = CCCConfigExtended(manager)

    # Build arguments for the extended config handler
    config_args = expanded_commands[1:]  # Remove 'config' from the command

    # Handle free string (-- set eMail=...) by converting to argument format
    if free_string:
        if free_string.startswith('set '):
            # Convert "set eMail=value" to ["--", "set", "eMail=value"]
            setting = free_string[4:].strip()  # Remove 'set '
            config_args = ["--", "set", setting]
        else:
            print("❌ Invalid config command with free string")
            return 1

    # Call the extended config handler
    return extended_config.handle_config_command(config_args)

def handle_git_command(expanded_commands, free_string, commands):
    """Handle git commands"""
    if len(expanded_commands) >= 3 and expanded_commands[1] == 'push':
        if expanded_commands[2] == 'homepage':
            return commands.git_push_homepage(free_string)
        elif expanded_commands[2] == 'ccc':
            # Check if tests flag is provided
            run_tests = len(expanded_commands) > 3 and expanded_commands[3] in ['test', 'tests', 'full']
            return commands.git_push_ccc(run_tests=run_tests, message=free_string)

    elif len(expanded_commands) >= 2:
        # New GitHub Actions integration commands
        if expanded_commands[1] == 'status':
            return commands.git_status()
        elif expanded_commands[1] == 'logs':
            return commands.git_logs()
        elif expanded_commands[1] == 'check':
            return commands.git_check()

    print("❌ Available git commands:")
    print("\n🚀 PUSH COMMANDS:")
    print("  gi[t] pu[sh] cc[c]          - Quick push to GitHub")
    print("  gi[t] pu[sh] cc[c] te[sts]  - Full validation & push")
    print("  gi[t] pu[sh] ho[mepage]     - Update collective-context.org")
    print("\n🔍 CI/CD MONITORING:")
    print("  gi[t] st[atus]              - Git status + GitHub Actions")
    print("  gi[t] lo[gs]                - Show GitHub Actions logs")
    print("  gi[t] ch[eck]               - Check CI status manually")
    print("\n💡 Tip: Use 'ccc git status' for complete repository overview")
    return 1

def handle_exec_command(expanded_commands, manager, commands):
    """Handle exec commands"""
    if len(expanded_commands) >= 3:
        if expanded_commands[1] == 'upload' and expanded_commands[2] == 'ppa':
            # Check if specific target is provided
            if len(expanded_commands) >= 4:
                target = expanded_commands[3]
                if target == 'cccmd':
                    # Upload only meta packages
                    from ccc_ppa_upload import upload_meta_packages
                    return upload_meta_packages(manager)
                elif target == 'ccc':
                    # Upload only base packages
                    return upload_ppa_command(manager)
                else:
                    print(f"❌ Unknown PPA target: {target}")
                    print("Available targets: ccc (base), cccmd (meta)")
                    return 1
            else:
                # No target specified - upload ALL packages (base AND meta) - USE PROFESSIONAL SYSTEM
                from ccc_upload_manager import upload_all_packages_professional
                return upload_all_packages_professional(manager)
        elif expanded_commands[1] == 'fix' and expanded_commands[2] == 'gpg':
            from ccc_ultimate_gpg_fix import fix_all_packages
            fix_all_packages()
            return 0
        elif expanded_commands[1] == 'upload' and expanded_commands[2] == 'meta':
            # Alias for upload meta packages
            from ccc_ppa_upload import upload_meta_packages
            return upload_meta_packages(manager)
        elif expanded_commands[1] == 'show' and expanded_commands[2] == 'ppa':
            # Use file-based approach like "ccc help full"
            return commands.ppa_show_write_and_read()
        elif expanded_commands[1] == 'debian':
            # Handle Debian packaging commands
            if len(expanded_commands) >= 3:
                debian_command = expanded_commands[2]
                return commands.exec_debian_command(debian_command)
            else:
                return commands.exec_debian_command(None)

    print("❌ Available exec commands:")
    print("  ex[ec] up[load] pp[a]         - Upload all (base & meta) packages")
    print("  ex[ec] up[load] pp[a] cc[c]   - Upload base packages only to PPA")
    print("  ex[ec] up[load] pp[a] cccmd   - Upload meta packages only to PPA")
    print("  ex[ec] up[load] me[ta]        - Upload meta packages (alias)")
    print("  ex[ec] sh[ow] pp[a]           - Show PPA configuration")
    print("  ex[ec] fi[x] gp[g]            - ULTIMATE GPG signature fix")
    print("  ex[ec] de[bian] bu[ild]       - Build Debian packages")
    print("  ex[ec] de[bian] up[load]      - Upload to Reprepro repository")
    print("  ex[ec] de[bian] fu[ll]        - Build and upload Debian packages")
    return 1


if __name__ == "__main__":
    sys.exit(main())
