#!/usr/bin/env python3
"""
Claude Session Log Helper
Automatic conversation logging for Claude Self-Logging solution
"""

import json
import sys
from datetime import datetime
from pathlib import Path

def log_conversation(user_message, claude_response):
    """
    Log user message and Claude response to session log
    This is the core function Claude calls to implement self-logging
    """
    # Load CTC config to check if save service is enabled
    config_file = Path(__file__).parent / "config" / "config.json"
    
    if not config_file.exists():
        return False
    
    try:
        with open(config_file, "r") as f:
            config = json.load(f)
        
        save_config = config.get("services", {}).get("save", {})
        
        if not save_config.get("enabled", False):
            return False  # Service not enabled
        
        log_file = save_config.get("log_file")
        if not log_file:
            return False  # No log file configured
        
        # Ensure log file exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Append conversation to log file
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"### [{timestamp}] USER:\n")
            f.write(f"> {user_message}\n\n")
            
            f.write(f"### [{timestamp}] CLAUDE:\n")
            f.write(f"{claude_response}\n\n")
            f.write("---\n\n")
        
        return True
        
    except Exception as e:
        # Silently fail - don't interrupt Claude's normal operation
        return False

def demo_log(user_msg="Test user message", claude_msg="Test Claude response"):
    """Demo function to test the logging"""
    result = log_conversation(user_msg, claude_msg)
    if result:
        print("✅ Session log entry created successfully")
    else:
        print("❌ Session logging failed or not enabled")
    return result

if __name__ == "__main__":
    # Command line interface for testing
    if len(sys.argv) >= 3:
        user_msg = sys.argv[1]
        claude_msg = sys.argv[2]
        demo_log(user_msg, claude_msg)
    else:
        print("Usage: python3 claude_session_log.py 'user message' 'claude response'")
        demo_log()