#!/usr/bin/env python3
"""
CTC Monitor - Background service for automatic input
Runs continuously and monitors control file for commands
"""

import sys
import time
import signal
from pathlib import Path
from datetime import datetime

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent / "lib"))

from ccc_manager import CCCManager

class CCCMonitor:
    def __init__(self):
        self.manager = CCCManager()
        self.running = True
        self.active = False
        self.counter = 0
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("🚀 CTC Monitor Started")
        print(f"📁 Control file: {self.manager.control_file}")
        print(f"📝 Log file: {self.manager.log_file}")
        print("=" * 50)
        print("Waiting for commands... (Ctrl+C to stop)")
        print()
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\n🛑 Shutting down monitor...")
        self.running = False
    
    def check_control_file(self):
        """Check control file for commands"""
        command = self.manager.read_control_file()
        
        if command == "START":
            self.active = True
            self.manager.log("Monitor ACTIVATED via control file", "SUCCESS")
            print(f"✅ AUTO-INPUT STARTED")
            return True
        elif command == "STOP":
            self.active = False
            self.manager.log("Monitor PAUSED via control file", "INFO")
            print(f"⏸️  AUTO-INPUT STOPPED")
            return True
        elif command == "EXIT":
            self.manager.log("Monitor EXIT command received", "INFO")
            print(f"🛑 EXIT command received")
            self.running = False
            return True
        
        return False
    
    def send_autoinput(self):
        """Send automatic input if enabled"""
        service = self.manager.config["services"]["autoinput"]
        
        if not service["enabled"]:
            return
        
        text = service["current_text"]
        self.counter += 1
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Cycle #{self.counter}: Sending '{text}'")
        
        if self.manager.send_to_tmux(text):
            # Update last run time
            service["last_run"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.manager.save_config()
            self.manager.log(f"Auto-input cycle #{self.counter} successful", "SUCCESS")
        else:
            self.manager.log(f"Auto-input cycle #{self.counter} failed", "ERROR")
    
    def run(self):
        """Main monitor loop"""
        # Check initial state from config
        if self.manager.config["services"]["autoinput"]["enabled"]:
            self.active = True
            print("ℹ️  Service is enabled in config - starting active")
        
        last_run = time.time()
        last_config_check = time.time()
        
        while self.running:
            # Check control file for commands
            self.check_control_file()
            
            # Reload config every 10 seconds to catch interval changes
            current_time = time.time()
            if current_time - last_config_check >= 10:
                self.manager.config = self.manager.load_config()
                last_config_check = current_time
            
            # Get current interval from config
            interval = self.manager.config["services"]["autoinput"]["interval"]
            
            # Send input if active and interval has passed
            if self.active:
                if current_time - last_run >= interval:
                    self.send_autoinput()
                    last_run = current_time
                    
                    # Show next run time with current interval
                    next_run = datetime.fromtimestamp(last_run + interval)
                    print(f"⏰ Next run at: {next_run.strftime('%H:%M:%S')} (interval: {interval/60}min)")
            
            # Short sleep to check control file frequently
            time.sleep(2)
        
        print("\n👋 Monitor stopped")
        self.manager.log("Monitor stopped", "INFO")

def main():
    """Main entry point"""
    monitor = CTCMonitor()
    
    try:
        monitor.run()
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Monitor error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())