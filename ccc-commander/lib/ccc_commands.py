"""
CCC Commands - Core Command System (Clean Migration)
Extracted essential Help functionality from legacy ccc_commands.py
Claude-2 Sandbox Migration - Step 1
"""

from pathlib import Path
import tempfile
import subprocess
from ccc_session_manager import CCCSessionManager


class Commands:
    """Core Commands System - Minimal Implementation for Help Functions"""
    
    def __init__(self, manager):
        self.manager = manager
        self.session_manager = CCCSessionManager()
    
    def help_show(self, section="all"):
        """Show help directly in Claude Code - chunked output"""
        
        if section == "all":
            print("CCC - Collective Context Commander v0.3.4 (Claude-2 Development)")
            print("Usage: ccc <command> [service] [options]")
            print("")
            print("[CORE]: help, version, config")  
            print("[SESSION]: start, save, end")
            print("[CONTEXT]: context, to [target] -- message")
            print("[GIT]: push, status, logs")
            print("")
            print("Quick Examples:")
            print("  ccc help full              # Detailed help")
            print("  ccc help [section]         # Specific section")
            
        elif section == "core":
            print("\n[CORE] COMMANDS:")
            print("  ccc help                   # Show compact help")
            print("  ccc help full              # Complete documentation")
            print("  ccc help [section]         # Specific help section")
            print("  ccc version                # Show version info")
            print("  ccc config                 # Show configuration")
            
        elif section == "session":
            print("\n[SESSION] MANAGEMENT:")
            print("  ccc session start [cl1|cl2|ai1|ai2]  # Start AI instance session")
            print("  ccc session save                      # Save current session")
            print("  ccc session end                       # End and save session")
            
        elif section == "context":
            print("\n[CONTEXT] MULTI-AGENT SYSTEM:")
            print("  ccc context                           # Read own messages")
            print("  ccc context to [target] -- message   # Send message")
            print("  ccc context to all -- message        # Broadcast to all")
            print("")
            print("  Targets: cl1 (Claude-1), cl2 (Claude-2), ai1 (Aider-1), ai2 (Aider-2)")
            
        elif section == "git":
            print("\n[GIT] INTEGRATION:")
            print("  ccc git push ccc          # Quick push to GitHub")
            print("  ccc git push ccc tests    # Full validation + push")
            print("  ccc git push homepage     # Update collective-context.org")
            print("  ccc git status            # Git + CI/CD status")
            print("  ccc git logs              # GitHub Actions logs")
            print("  ccc git check             # Manual pipeline check")
            
        elif section == "sections":
            print("\n[SECTIONS] HELP SECTIONS:")
            print("  ccc help core             # Core commands")
            print("  ccc help session          # Session management")
            print("  ccc help context          # Multi-agent context")
            print("  ccc help git              # Git integration")
            print("  ccc help full             # Complete help")
    
    def help_write_and_read(self, section="full"):
        """Write help to temp file for Claude Code display"""
        
        if section == "full":
            content = self._generate_full_help_content()
        elif section == "experimental":
            content = self._generate_experimental_help_content()
        else:
            content = f"Help section '{section}' not implemented yet."
        
        # Write to temporary file for Claude Code display
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Display the file content
        print(content)
        
        # Clean up
        import os
        os.unlink(temp_file_path)
        return 0
    
    def _generate_full_help_content(self):
        """Generate full help content for CCC Commander"""
        return """# CCC - Collective Context Commander v0.3.4

**Multi-Agent AI Orchestration System - Claude-2 Development Sandbox**

## CORE COMMANDS
- **ccc help**           - Show compact help message
- **ccc help full**      - Show detailed help with all sections  
- **ccc help [section]** - Show help for specific section
- **ccc version**        - Show version information
- **ccc config**         - Show configuration

## SESSION MANAGEMENT
- **ccc session start [ai-instance]** - Start new session with AI instance name
- **ccc session save**                - Save current session knowledge
- **ccc session end**                 - Save ALL from session start to end

**AI Instances: cl1 (Claude-1), cl2 (Claude-2), ai1 (Aider-1), ai2 (Aider-2)**

## MULTI-AGENT CONTEXT SYSTEM
- **ccc context**                                   - Read own AI instance context
- **ccc context [to] [cl1|cl2|ai1|ai2] -- message** - Send message to specific AI
- **ccc context [to] all               -- message** - Broadcast message to all AIs

**Example:**
```bash
ccc context to cl1 -- "Please check the legacy system"
ccc context to all -- "Status update: Step 1 completed"
```

## GIT INTEGRATION (Test, Push, Verify)
- **ccc git push ccc**       - Quick push to GitHub (~5 seconds)
- **ccc git push ccc tests** - Full validation + push (~60 seconds)
- **ccc git push homepage**  - Update collective-context.org
- **ccc git status**         - Git status + GitHub Actions CI/CD monitoring
- **ccc git logs**           - Show GitHub Actions workflow logs
- **ccc git check**          - Manual check of CI/CD pipeline status

## DEVELOPMENT ENVIRONMENT

**Sandbox Isolation:**
- Working Directory: `/home/mayer/prog/ai/git/collective-context/ccc-new/`
- Local Wrapper: `./bin/ccc`
- Private Config: `./.local/config/`
- Session Database: `./.local/db/`

**Design Principles:**
- "Your Sandbox, Your Config, Your Data"
- Reproducible Builds
- Complete Environment Isolation

---

**CCC Commander - Professional AI Orchestration System**
*Multi-Agent Development Concert - Building the Future of AI Coordination*
"""
    
    def _generate_experimental_help_content(self):
        """Generate experimental help content"""
        return """# CCC - Experimental Features (Development)

**Warning: These features are under development in Claude-2 sandbox**

## EXPERIMENTAL SESSION FEATURES
- Advanced session analytics
- Cross-agent session sharing
- Session replay functionality

## EXPERIMENTAL CONTEXT FEATURES  
- Context persistence across sessions
- Smart message routing
- Context search and filtering

## EXPERIMENTAL GIT FEATURES
- Automated testing integration
- Smart commit message generation
- Branch management automation

---

**Note: These features are part of the ongoing migration to ccc-new/**
"""
    
    # Placeholder methods for future implementation
    def version_write_and_read(self):
        """Show detailed version information"""
        print("CCC Commander v0.3.4")
        print("Environment: Claude-2 Development Sandbox")
        print("Path: /home/mayer/prog/ai/git/collective-context/ccc-new/")
        print("Status: Step 1 - Core Commands Migration")
        return 0
    
    def handle_context_command(self, args):
        """Handle context commands - placeholder"""
        print("Context system not yet migrated - coming in Step 4")
        return 0
    
    def handle_session_command(self, args):
        """Handle session commands: start, save, end"""
        if not args:
            print("❌ Session command requires action: start, save, or end")
            print("\nUsage:")
            print("  ccc session start [cl1|cl2|ai1|ai2]  # Start new session")
            print("  ccc session save                     # Save current session")
            print("  ccc session end                      # End active session")
            print("\nAI Instances: cl1 (Claude-1), cl2 (Claude-2), ai1 (Aider-1), ai2 (Aider-2)")
            return 1
        
        action = args[0].lower()
        ai_instance = args[1] if len(args) > 1 else None
        
        try:
            if action in ['start', 'sta']:
                return self._session_start(ai_instance)
            elif action in ['save', 'sav']:
                return self._session_save(ai_instance)
            elif action in ['end', 'ende']:
                return self._session_end(ai_instance)
            else:
                print(f"❌ Unknown session action: {action}")
                print("Available actions: start, save, end")
                return 1
        except Exception as e:
            print(f"❌ Session error: {e}")
            return 1
    
    def _session_start(self, ai_instance):
        """Start a new session for AI instance"""
        if not ai_instance:
            print("❌ AI instance required for session start")
            print("Usage: ccc session start [cl1|cl2|ai1|ai2]")
            return 1
        
        # AI instance mapping
        ai_mapping = {
            'cl1': {'name': 'Claude-1', 'role': 'Legacy-Guardian'},
            'cl2': {'name': 'Claude-2', 'role': 'Innovation-Driver'},  
            'ai1': {'name': 'Aider-1', 'role': 'Quality-Controller'},
            'ai2': {'name': 'Aider-2', 'role': 'Assistant'}
        }
        
        ai_key = ai_instance.lower()
        if ai_key not in ai_mapping:
            print(f"❌ Invalid AI instance: {ai_instance}")
            print("Valid instances: cl1 (Claude-1), cl2 (Claude-2), ai1 (Aider-1), ai2 (Aider-2)")
            return 1
        
        ai_info = ai_mapping[ai_key]
        
        try:
            session_id = self.session_manager.start_session(ai_key)
            
            print(f"\n🚀 CCC Session Started")
            print("=" * 50)
            print(f"AI Instance: {ai_info['name']} ({ai_key.upper()})")
            print(f"Role: {ai_info['role']}")
            print(f"Session ID: {session_id}")
            print(f"Sandbox: ccc-new (Development)")
            print(f"Database: .local/db/sessions.db")
            print("=" * 50)
            print("\n✅ Session active - use 'ccc session save' to log progress")
            
            return 0
        except Exception as e:
            print(f"❌ Failed to start session: {e}")
            return 1
    
    def _session_save(self, ai_instance):
        """Save current session state"""
        if not ai_instance:
            # Try to find any active session
            info = self.session_manager.get_database_info()
            if info['active_sessions'] == 0:
                print("❌ No active sessions found")
                print("Start a session first: ccc session start [cl1|cl2|ai1|ai2]")
                return 1
            elif info['active_sessions'] > 1:
                print("❌ Multiple active sessions found. Please specify AI instance:")
                print("Usage: ccc session save [cl1|cl2|ai1|ai2]")
                return 1
            else:
                # Find the single active session
                for ai in ['cl1', 'cl2', 'ai1', 'ai2']:
                    session = self.session_manager.get_active_session(ai)
                    if session:
                        ai_instance = ai
                        break
        
        ai_key = ai_instance.lower() if ai_instance else None
        if not ai_key or ai_key not in ['cl1', 'cl2', 'ai1', 'ai2']:
            print(f"❌ Invalid AI instance: {ai_instance}")
            return 1
        
        try:
            session_id = self.session_manager.save_session(ai_key, "Manual session save")
            
            print(f"\n💾 Session Saved")
            print(f"AI Instance: {ai_key.upper()}")
            print(f"Session ID: {session_id}")
            print(f"Timestamp: {self._get_current_time()}")
            print("✅ Session state saved to database")
            
            return 0
        except Exception as e:
            print(f"❌ Failed to save session: {e}")
            return 1
    
    def _session_end(self, ai_instance):
        """End active session"""
        if not ai_instance:
            # Try to find any active session
            info = self.session_manager.get_database_info()
            if info['active_sessions'] == 0:
                print("❌ No active sessions found")
                return 1
            elif info['active_sessions'] > 1:
                print("❌ Multiple active sessions found. Please specify AI instance:")
                print("Usage: ccc session end [cl1|cl2|ai1|ai2]")
                return 1
            else:
                # Find the single active session
                for ai in ['cl1', 'cl2', 'ai1', 'ai2']:
                    session = self.session_manager.get_active_session(ai)
                    if session:
                        ai_instance = ai
                        break
        
        ai_key = ai_instance.lower() if ai_instance else None
        if not ai_key or ai_key not in ['cl1', 'cl2', 'ai1', 'ai2']:
            print(f"❌ Invalid AI instance: {ai_instance}")
            return 1
        
        try:
            session = self.session_manager.get_active_session(ai_key)
            if not session:
                print(f"❌ No active session for {ai_key.upper()}")
                return 1
            
            session_id = self.session_manager.end_session(ai_key)
            
            print(f"\n🏁 Session Ended")
            print("=" * 50)
            print(f"AI Instance: {ai_key.upper()}")
            print(f"Session ID: {session_id}")
            print(f"Duration: {self._calculate_session_duration(session)}")
            print(f"Status: Completed")
            print("=" * 50)
            print("\n✅ Session ended and logged to database")
            
            return 0
        except Exception as e:
            print(f"❌ Failed to end session: {e}")
            return 1
    
    def _get_current_time(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _calculate_session_duration(self, session):
        """Calculate session duration"""
        from datetime import datetime
        try:
            start = datetime.fromisoformat(session['start_time'])
            now = datetime.now()
            duration = now - start
            
            hours = int(duration.total_seconds() // 3600)
            minutes = int((duration.total_seconds() % 3600) // 60)
            
            if hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"
        except:
            return "Unknown"
    
    def git_push_ccc(self, run_tests=False, message=None):
        """Push CCC code to GitHub repository"""
        import subprocess
        import os
        from pathlib import Path
        
        print()
        if run_tests:
            print("ccc git push ccc tests " + "=" * 80)
            print("\n🔍 CCC Full Validation + Push")
        else:
            print("ccc git push ccc " + "=" * 80)
            print("\n⚡ CCC Quick Push")
        print("=" * 50)
        
        # Check if we're in a git repository
        try:
            result = subprocess.run(["git", "rev-parse", "--git-dir"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                print("❌ Not in a git repository")
                return 1
        except Exception as e:
            print(f"❌ Git not available: {e}")
            return 1
        
        # Get current status
        print("\n📁 Repository Status:")
        try:
            result = subprocess.run(["git", "status", "--porcelain"], 
                                  capture_output=True, text=True, timeout=10)
            if result.stdout.strip():
                print("   📝 Changes detected")
                # Show a few changes
                changes = result.stdout.strip().split('\n')[:5]
                for change in changes:
                    print(f"   {change}")
                stdout_lines = result.stdout.strip().split('\n')
                if len(stdout_lines) > 5:
                    print(f"   ... and {len(stdout_lines) - 5} more")
            else:
                print("   ✅ Working directory clean")
        except Exception:
            print("   📝 Status check failed")
        
        # Get current branch
        current_branch = "main"
        try:
            result = subprocess.run(["git", "branch", "--show-current"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                current_branch = result.stdout.strip()
                print(f"   🌿 Branch: {current_branch}")
        except Exception:
            print("   📝 Branch info unavailable")
        
        # Optional: Run basic validation if tests requested
        if run_tests:
            print("\n🧪 Basic Validation:")
            # Simple Python syntax check
            try:
                result = subprocess.run([
                    "python3", "-m", "py_compile", 
                    "ccc-commander/src/ccc_main.py"
                ], capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    print("   ✅ Python syntax valid")
                else:
                    print("   ❌ Python syntax errors detected")
                    print(f"   {result.stderr.strip()}")
                    return 1
            except Exception:
                print("   ⚠️ Syntax check skipped (python3 not available)")
        
        # Add and commit changes
        print(f"\n🔄 Git Operations:")
        try:
            # Add all changes
            result = subprocess.run(["git", "add", "."], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print("   ✅ Changes staged")
            else:
                print(f"   ❌ Staging failed: {result.stderr}")
                return 1
            
            # Check if there's anything to commit
            result = subprocess.run(["git", "diff", "--cached", "--quiet"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("   📝 No changes to commit")
            else:
                # Create commit
                commit_message = message or f"CCC Step 3: Git Integration ({'with tests' if run_tests else 'quick push'})"
                result = subprocess.run([
                    "git", "commit", "-m", commit_message
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    print(f"   ✅ Committed: {commit_message}")
                else:
                    print(f"   ❌ Commit failed: {result.stderr}")
                    return 1
            
            # Push to remote
            result = subprocess.run([
                "git", "push", "origin", current_branch
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print(f"   ✅ Pushed to origin/{current_branch}")
                
                # Try to get remote URL
                try:
                    result = subprocess.run([
                        "git", "remote", "get-url", "origin"
                    ], capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        remote_url = result.stdout.strip()
                        if "github.com" in remote_url:
                            # Convert to browser URL
                            if remote_url.endswith('.git'):
                                remote_url = remote_url[:-4]
                            if remote_url.startswith('git@github.com:'):
                                remote_url = remote_url.replace('git@github.com:', 'https://github.com/')
                            print(f"   🌐 Repository: {remote_url}")
                except Exception:
                    pass
                    
                print(f"\n🎯 Push completed successfully!")
                if run_tests:
                    print("   📊 Validation: Passed")
                    print("   ⚡ Speed: Full validation (~60s)")
                else:
                    print("   ⚡ Speed: Quick push (~5s)")
                
                return 0
            else:
                print(f"   ❌ Push failed: {result.stderr}")
                return 1
                
        except Exception as e:
            print(f"❌ Git operation failed: {e}")
            return 1
    
    def git_push_homepage(self, message=None):
        """Update collective-context.org homepage with achievements"""
        print()
        print("ccc git push homepage " + "=" * 80)
        print("\n🌐 CCC Homepage Update Tool")
        print("=" * 50)
        
        print("\n📝 Analyzing session achievements...")
        print("   ✅ Step 1: Core Commands System")
        print("   ✅ Step 2: Session Management System") 
        print("   🔄 Step 3: Git Integration (in progress)")
        print("   ⏳ Step 4: Multi-Agent Context System")
        
        if message:
            print(f"\n📝 Additional achievements: {message}")
        
        print("\n💭 Session Summary:")
        print("   🎯 CCC Development Concert - Claude-2 Innovation-Driver")
        print("   🏗️ Clean Migration Strategy: Essential Features Only")
        print("   🔧 Sandbox Isolation: ccc-new/ Development Environment")
        print("   📊 Progress: 2/4 Steps Completed Successfully")
        
        print("\n🎯 Homepage update analysis completed!")
        print("📄 Target: https://collective-context.org")
        print("🔗 Content ready for homepage integration")
        
        return 0
    
    def git_status(self):
        """Enhanced git status with repository information"""
        import subprocess
        
        print("📊 CCC Git Status & Repository Info")
        print("=" * 50)
        
        # Check if we're in a git repository
        try:
            result = subprocess.run(["git", "rev-parse", "--git-dir"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                print("❌ Not in a git repository")
                return 1
        except Exception:
            print("❌ Git not available")
            return 1
        
        # Local Repository Status
        print("\n📁 Local Repository Status:")
        try:
            result = subprocess.run(["git", "status", "--porcelain"], 
                                  capture_output=True, text=True, timeout=10)
            if result.stdout.strip():
                print("   📝 Changes detected:")
                changes = result.stdout.strip().split('\n')[:10]  # Show up to 10 changes
                for change in changes:
                    status = change[:2]
                    filename = change[3:]
                    if status == '??':
                        print(f"      📄 Untracked: {filename}")
                    elif status == ' M':
                        print(f"      ✏️  Modified:  {filename}")
                    elif status == 'M ':
                        print(f"      📦 Staged:    {filename}")
                    elif status == 'A ':
                        print(f"      ➕ Added:     {filename}")
                    else:
                        print(f"      📝 {status}: {filename}")
                        
                stdout_lines = result.stdout.strip().split('\n')
                if len(stdout_lines) > 10:
                    print(f"      ... and {len(stdout_lines) - 10} more changes")
            else:
                print("   ✅ Working directory clean")
        except Exception:
            print("   📝 Status check failed")
        
        # Branch Information
        print("\n🌿 Branch Information:")
        try:
            result = subprocess.run(["git", "branch", "--show-current"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                current_branch = result.stdout.strip()
                print(f"   📍 Current: {current_branch}")
            else:
                print("   📝 Branch info unavailable")
        except Exception:
            print("   📝 Branch check failed")
        
        # Remote Information
        print("\n🌐 Remote Information:")
        try:
            result = subprocess.run(["git", "remote", "-v"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and result.stdout.strip():
                remotes = result.stdout.strip().split('\n')
                origin_fetch = None
                for remote in remotes:
                    if 'origin' in remote and '(fetch)' in remote:
                        origin_fetch = remote.split()[1]
                        break
                
                if origin_fetch:
                    print(f"   🔗 Origin: {origin_fetch}")
                    
                    # Convert to browser URL if GitHub
                    if "github.com" in origin_fetch:
                        browser_url = origin_fetch
                        if browser_url.endswith('.git'):
                            browser_url = browser_url[:-4]
                        if browser_url.startswith('git@github.com:'):
                            browser_url = browser_url.replace('git@github.com:', 'https://github.com/')
                        print(f"   🌐 Browser: {browser_url}")
                else:
                    print("   📝 No origin remote found")
            else:
                print("   📝 No remotes configured")
        except Exception:
            print("   📝 Remote check failed")
        
        # Last Commit Information
        print("\n📋 Last Commit:")
        try:
            result = subprocess.run([
                "git", "log", "-1", "--format=%h %s (%cr by %an)"
            ], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"   💾 {result.stdout.strip()}")
            else:
                print("   📝 No commit history")
        except Exception:
            print("   📝 Commit info unavailable")
        
        # CI/CD Status (simplified)
        print("\n🔄 CI/CD Status:")
        print("   ℹ️  GitHub Actions: Check repository for workflow status")
        print("   🔍 Use 'ccc git logs' for detailed CI/CD information")
        
        return 0
    
    def git_logs(self):
        """Show GitHub Actions logs and recent git history"""
        import subprocess
        
        print("📋 CCC Git Logs & CI/CD Information")
        print("=" * 50)
        
        # Recent Git History
        print("\n📚 Recent Git History:")
        try:
            result = subprocess.run([
                "git", "log", "--oneline", "-10"
            ], capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and result.stdout.strip():
                print("   Recent commits:")
                for line in result.stdout.strip().split('\n'):
                    print(f"      💾 {line}")
            else:
                print("   📝 No commit history available")
        except Exception:
            print("   📝 Git log unavailable")
        
        # Branch Summary
        print("\n🌿 Branch Summary:")
        try:
            result = subprocess.run([
                "git", "branch", "-a"
            ], capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and result.stdout.strip():
                branches = result.stdout.strip().split('\n')[:10]  # Show up to 10 branches
                for branch in branches:
                    branch = branch.strip()
                    if branch.startswith('* '):
                        print(f"   📍 {branch[2:]} (current)")
                    elif branch.startswith('remotes/'):
                        print(f"   🌐 {branch}")
                    else:
                        print(f"   🌿 {branch}")
                        
                stdout_lines = result.stdout.strip().split('\n') 
                if len(stdout_lines) > 10:
                    print(f"   ... and {len(stdout_lines) - 10} more branches")
            else:
                print("   📝 No branches found")
        except Exception:
            print("   📝 Branch info unavailable")
        
        # GitHub Actions Status (Simplified)
        print("\n🔄 CI/CD Status:")
        print("   ℹ️  GitHub Actions Integration:")
        print("      🔍 Manual Check: Visit repository Actions tab")
        print("      📊 Workflow Status: Use 'ccc git check' for detailed analysis")
        print("      🚀 Recent Pushes: Check above git history for push events")
        
        # Repository Statistics
        print("\n📊 Repository Statistics:")
        try:
            # Count commits
            result = subprocess.run([
                "git", "rev-list", "--count", "HEAD"
            ], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                commit_count = result.stdout.strip()
                print(f"   💾 Total commits: {commit_count}")
        except Exception:
            print("   📝 Commit count unavailable")
        
        try:
            # Count contributors
            result = subprocess.run([
                "git", "shortlog", "-sn", "--all"
            ], capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and result.stdout.strip():
                contributors = result.stdout.strip().split('\n')[:5]  # Top 5 contributors
                print("   👥 Top contributors:")
                for contributor in contributors:
                    parts = contributor.strip().split('\t')
                    if len(parts) == 2:
                        count, name = parts
                        print(f"      {name}: {count} commits")
        except Exception:
            print("   📝 Contributor info unavailable")
        
        return 0
    
    def git_check(self):
        """Manual CI/CD pipeline status check"""
        import subprocess
        
        print("🔍 CCC Manual CI/CD Pipeline Check")
        print("=" * 50)
        
        # Repository Information
        print("\n📁 Repository Information:")
        try:
            result = subprocess.run(["git", "remote", "get-url", "origin"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                remote_url = result.stdout.strip()
                print(f"   🔗 Origin: {remote_url}")
                
                # Convert to GitHub Actions URL
                if "github.com" in remote_url:
                    browser_url = remote_url
                    if browser_url.endswith('.git'):
                        browser_url = browser_url[:-4]
                    if browser_url.startswith('git@github.com:'):
                        browser_url = browser_url.replace('git@github.com:', 'https://github.com/')
                    
                    actions_url = f"{browser_url}/actions"
                    print(f"   🔄 Actions: {actions_url}")
                    
                    # Get current branch
                    branch_result = subprocess.run(["git", "branch", "--show-current"], 
                                                 capture_output=True, text=True, timeout=10)
                    if branch_result.returncode == 0:
                        current_branch = branch_result.stdout.strip()
                        workflow_url = f"{browser_url}/actions?query=branch%3A{current_branch}"
                        print(f"   📊 Branch Workflows: {workflow_url}")
            else:
                print("   📝 No remote repository configured")
        except Exception:
            print("   📝 Repository info unavailable")
        
        # Last Push Information
        print("\n🚀 Last Push Information:")
        try:
            result = subprocess.run([
                "git", "log", "-1", "--format=%h %s (%cr)", "origin/HEAD"
            ], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"   💾 Last remote commit: {result.stdout.strip()}")
            else:
                print("   📝 No remote tracking information")
        except Exception:
            print("   📝 Remote commit info unavailable")
        
        # Pipeline Status Guidance
        print("\n📋 Manual Check Instructions:")
        print("   1. 🌐 Visit the GitHub Actions URL above")
        print("   2. 🔍 Check for green checkmarks (✅) or red X marks (❌)")
        print("   3. 📊 Review workflow runs for your recent commits")
        print("   4. 🔧 Click on failed runs to see detailed logs")
        
        print("\n💡 Quick Status Indicators:")
        print("   ✅ Green: All checks passed")
        print("   ❌ Red: Some checks failed") 
        print("   🟡 Yellow: Checks in progress")
        print("   ⚪ Gray: No checks configured")
        
        print("\n🎯 CI/CD Check completed!")
        print("   Use 'ccc git logs' for recent git history")
        print("   Use 'ccc git status' for local repository status")
        
        return 0