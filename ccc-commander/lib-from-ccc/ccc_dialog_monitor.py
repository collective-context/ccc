#!/usr/bin/env python3
"""
CTC Dialog Monitor - Session dialog logger
Captures all tmux input/output and logs complete conversations
"""

import sys
import time
import signal
import subprocess
import re
from pathlib import Path
from datetime import datetime

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent / "lib"))

from ccc_manager import CCCManager

class CCCDialogMonitor:
    def __init__(self):
        self.manager = CCCManager()
        self.running = True
        self.dialog_service = self.manager.config["services"]["dialog"]
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Initialize dialog log file
        self.init_dialog_log()
        
        print("📝 CTC Dialog Monitor Started")
        print(f"📁 Dialog log: {self.dialog_log_file}")
        print("=" * 50)
        print("Monitoring tmux session for dialog...")
        print()
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\n🛑 Shutting down dialog monitor...")
        self.log_dialog_entry("SYSTEM", "Dialog monitoring stopped")
        self.running = False
    
    def init_dialog_log(self):
        """Initialize dialog log file with session info"""
        # Create logs directory if needed
        dialog_logs_dir = self.manager.logs_dir / "dialogs"
        dialog_logs_dir.mkdir(exist_ok=True)
        
        # Generate session ID and log filename with better format
        session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.dialog_log_file = dialog_logs_dir / f"dialog_{session_id}.log"
        
        # Update config with session info
        self.dialog_service["session_id"] = session_id
        self.dialog_service["log_file"] = str(self.dialog_log_file)
        self.dialog_service["last_run"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.manager.save_config()
        
        # Write dialog header
        with open(self.dialog_log_file, 'w', encoding='utf-8') as f:
            f.write(f"=== CTC Dialog Log ===\n")
            f.write(f"Session ID: {session_id}\n")
            f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Tmux Session: {self.dialog_service['tmux_session']}\n")
            f.write(f"Target Dir: {self.dialog_service['target_dir']}\n")
            f.write("=" * 80 + "\n\n")
    
    def log_dialog_entry(self, source, content, timestamp=None):
        """Log a dialog entry"""
        if timestamp is None:
            timestamp = datetime.now().strftime("%H:%M:%S")
        
        try:
            with open(self.dialog_log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {source}: {content}\n")
                if source != "SYSTEM":
                    f.write("-" * 40 + "\n")
        except Exception as e:
            print(f"❌ Failed to write to dialog log: {e}")
    
    def capture_tmux_pane_content(self):
        """Capture current tmux pane content"""
        try:
            session = self.dialog_service['tmux_session']
            result = subprocess.run(
                ["tmux", "capture-pane", "-t", session, "-p"],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode == 0:
                return result.stdout
            return None
            
        except Exception as e:
            print(f"❌ Failed to capture tmux content: {e}")
            return None
    
    def is_ui_noise(self, text):
        """Check if text is UI noise that should be filtered out"""
        noise_patterns = [
            '⏵⏵ accept edits',
            '✗ Auto-update failed',
            '│ >',
            '╰──',
            '────',
            'shift+tab to cycle',
            'Try claude doctor',
            'npm i -g',
            r'^\s*$',  # Empty lines
            r'^\s*[\│╰─⏵✗]+\s*$',  # Just UI characters
        ]
        
        for pattern in noise_patterns:
            import re
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def detect_user_input(self, current_content, last_content):
        """Detect genuine user input (not UI updates)"""
        if not current_content or not last_content:
            return None
        
        current_lines = current_content.strip().split('\n')
        last_lines = last_content.strip().split('\n')
        
        # Look for new lines that appear to be actual user input
        if len(current_lines) > len(last_lines):
            new_lines = current_lines[len(last_lines):]
            
            for line in new_lines:
                line = line.strip()
                
                # Skip UI noise
                if self.is_ui_noise(line):
                    continue
                    
                # Look for genuine user input patterns
                if (line and 
                    not line.startswith('[') and  # Not timestamps
                    not line.startswith('=') and  # Not dividers
                    len(line) > 3 and             # Meaningful length
                    not line.startswith('ctc ') and  # Not our tool commands
                    '/' not in line[:10]):        # Not file paths
                    return line
        
        return None
    
    def detect_claude_response(self, current_content, last_content):
        """Detect genuine Claude responses (not tool output)"""
        if not current_content or not last_content:
            return None
        
        current_lines = current_content.strip().split('\n')
        last_lines = last_content.strip().split('\n')
        
        # Look for new content that appears to be Claude's actual response
        if len(current_lines) > len(last_lines):
            new_lines = current_lines[len(last_lines):]
            
            # Filter for genuine Claude responses
            response_lines = []
            for line in new_lines:
                line = line.strip()
                
                # Skip UI noise
                if self.is_ui_noise(line):
                    continue
                
                # Skip tool outputs and system messages
                if (line and 
                    not line.startswith('$') and      # Not shell prompts
                    not line.startswith('>') and      # Not continuation prompts  
                    not line.startswith('✅') and     # Not tool success
                    not line.startswith('❌') and     # Not tool errors
                    not line.startswith('📋') and     # Not status displays
                    not line.startswith('🔍') and     # Not search results
                    not line.startswith('/') and      # Not file paths
                    'function_calls' not in line and  # Not tool calls
                    '<' not in line and         # Not tool XML
                    len(line) > 10):                  # Meaningful content
                    response_lines.append(line)
            
            # Join meaningful response lines
            if response_lines:
                response = ' '.join(response_lines)
                # Only return if it looks like actual conversation
                if len(response) > 20 and any(word in response.lower() for word in 
                    ['das', 'ich', 'du', 'wir', 'ist', 'sind', 'kann', 'soll', 'wird']):
                    return response
        
        return None
    
    def monitor_tmux_activity(self):
        """Monitor tmux session for activity and log dialog"""
        last_content = ""
        last_activity_time = time.time()
        
        while self.running:
            # Check if dialog service is still enabled
            self.manager.config = self.manager.load_config()
            if not self.manager.config["services"]["dialog"]["enabled"]:
                print("ℹ️  Dialog service disabled, stopping monitor")
                break
            
            current_content = self.capture_tmux_pane_content()
            if current_content and current_content != last_content:
                current_time = time.time()
                
                # Detect genuine user input (filter out UI noise)
                user_input = self.detect_user_input(current_content, last_content)
                if user_input and not self.is_ui_noise(user_input):
                    self.log_dialog_entry("USER", user_input)
                    print(f"👤 USER: {user_input}")
                
                # Detect genuine Claude response (filter out tool outputs)
                time.sleep(1.0)  # Wait longer for full response
                updated_content = self.capture_tmux_pane_content()
                if updated_content:
                    claude_response = self.detect_claude_response(updated_content, current_content)
                    if claude_response and not self.is_ui_noise(claude_response):
                        self.log_dialog_entry("CLAUDE", claude_response)
                        print(f"🤖 CLAUDE: {claude_response[:100]}..." if len(claude_response) > 100 else f"🤖 CLAUDE: {claude_response}")
                
                last_content = updated_content or current_content
                last_activity_time = current_time
            
            # Short sleep to avoid excessive polling
            time.sleep(1)
        
        print("\n👋 Dialog monitor stopped")
        self.manager.log("Dialog monitor stopped", "INFO")
    
    def run(self):
        """Main monitor loop"""
        try:
            self.log_dialog_entry("SYSTEM", "Dialog monitoring started")
            self.monitor_tmux_activity()
        except Exception as e:
            print(f"❌ Dialog monitor error: {e}")
            self.log_dialog_entry("SYSTEM", f"Monitor error: {e}")

def main():
    """Main entry point"""
    monitor = CTCDialogMonitor()
    
    try:
        monitor.run()
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Dialog monitor error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())