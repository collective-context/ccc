#!/usr/bin/env python3
"""
CCC Claude Communication Module
Handles inter-Claude communication via session log files
"""

import os
import re
from datetime import datetime
from pathlib import Path

class ClaudeCommunication:
    """Manages Claude-to-Claude communication through session logs"""
    
    def __init__(self):
        """Initialize Claude Communication"""
        self.base_path = Path(os.environ.get('CCC_PROJECT_DIR', str(Path.home() / 'prog/claude/osCASH.me'))) / 'readme'
        self.claude_1_file = self.base_path / "claude-1.md"
        self.claude_2_file = self.base_path / "claude-2.md"
        
        # Detect which Claude instance we are (based on recent activity or session context)
        self.current_claude = self._detect_current_instance()
        self.other_claude = "claude-2" if self.current_claude == "claude-1" else "claude-1"
        
    def _detect_current_instance(self):
        """Detect which Claude instance is currently active"""
        # For now, assume Claude-1 (can be enhanced with better detection logic)
        # Could check recent modifications, session markers, or environment variables
        return "claude-1"
    
    def _get_timestamp(self):
        """Get current timestamp in standard format"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def read_other_claude(self):
        """Read the other Claude's session log and check for unread messages"""
        other_file = self.claude_2_file if self.current_claude == "claude-1" else self.claude_1_file
        
        if not other_file.exists():
            print(f"❌ {self.other_claude}.md file not found at {other_file}")
            return 1
        
        print(f"📖 Reading {self.other_claude}.md for new messages...")
        print(f"🤖 Current instance: {self.current_claude}")
        print("-" * 60)
        
        try:
            with open(other_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find messages directed to current Claude
            message_pattern = r'## 💬 \*\*DIREKTE MESSAGE AN ' + self.current_claude.upper() + r'.*?\*\*Gesendet von.*?(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\*\*'
            
            messages = re.finditer(message_pattern, content, re.DOTALL)
            unread_count = 0
            unread_positions = []
            
            for match in messages:
                sent_line_end = match.end()
                # Check if there's a "Gelesen von" timestamp after this message
                next_100_chars = content[sent_line_end:sent_line_end+100]
                if f"Gelesen von {self.current_claude.capitalize()}" not in next_100_chars:
                    unread_count += 1
                    unread_positions.append(sent_line_end)
                    
                    # Extract message content for display
                    message_start = match.start()
                    message_end = sent_line_end
                    message_content = content[message_start:message_end]
                    
                    print(f"\n🔔 UNREAD MESSAGE found:")
                    print("-" * 40)
                    # Show first 500 chars of message
                    preview = message_content[:500]
                    if len(message_content) > 500:
                        preview += "\n[... message truncated ...]"
                    print(preview)
                    print("-" * 40)
            
            if unread_count > 0:
                print(f"\n✉️  Found {unread_count} unread message(s) from {self.other_claude}")
                
                # AUTOMATICALLY add read timestamps
                print(f"✍️  Automatically adding read timestamps...")
                timestamp = self._get_timestamp()
                
                # Sort positions in reverse order to maintain correct offsets
                unread_positions.sort(reverse=True)
                
                # Add acknowledgment timestamps
                updated_content = content
                for position in unread_positions:
                    acknowledgment = f"\n**Gelesen von {self.current_claude.capitalize()} am {timestamp}**"
                    updated_content = (
                        updated_content[:position] + 
                        acknowledgment + 
                        updated_content[position:]
                    )
                
                # Write back the updated content
                with open(other_file, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                
                print(f"✅ Automatically added {unread_count} read timestamp(s) to {self.other_claude}.md")
            else:
                print(f"✅ No unread messages from {self.other_claude}")
            
            # Show last modification time
            mod_time = datetime.fromtimestamp(other_file.stat().st_mtime)
            print(f"\n📅 Last modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            return 0
            
        except Exception as e:
            print(f"❌ Error reading {other_file}: {e}")
            return 1
    
    def write_to_own_claude(self):
        """Write acknowledgment timestamps to own Claude session log"""
        own_file = self.claude_1_file if self.current_claude == "claude-1" else self.claude_2_file
        
        if not own_file.exists():
            print(f"❌ {self.current_claude}.md file not found at {own_file}")
            return 1
        
        print(f"✍️  Writing to {self.current_claude}.md...")
        print(f"🤖 Current instance: {self.current_claude}")
        print("-" * 60)
        
        try:
            with open(own_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find messages from other Claude that need acknowledgment
            other_claude_name = "Claude-2" if self.current_claude == "claude-1" else "Claude-1"
            pattern = r'(\*\*Gesendet von ' + other_claude_name + r' am \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\*\*)'
            
            updated_content = content
            acknowledgments_added = 0
            
            for match in re.finditer(pattern, content):
                sent_line_end = match.end()
                # Check if there's already a "Gelesen von" timestamp
                next_100_chars = content[sent_line_end:sent_line_end+100]
                if f"Gelesen von {self.current_claude.capitalize()}" not in next_100_chars:
                    # Add acknowledgment timestamp
                    timestamp = self._get_timestamp()
                    acknowledgment = f"\n**Gelesen von {self.current_claude.capitalize()} am {timestamp}**"
                    
                    # Insert acknowledgment after the sent timestamp
                    updated_content = (
                        updated_content[:sent_line_end] + 
                        acknowledgment + 
                        updated_content[sent_line_end:]
                    )
                    acknowledgments_added += 1
                    print(f"✅ Added acknowledgment timestamp: {timestamp}")
            
            if acknowledgments_added > 0:
                # Write back the updated content
                with open(own_file, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                print(f"\n📝 Added {acknowledgments_added} acknowledgment timestamp(s) to {self.current_claude}.md")
            else:
                print(f"✅ No new messages to acknowledge in {self.current_claude}.md")
            
            return 0
            
        except Exception as e:
            print(f"❌ Error updating {own_file}: {e}")
            return 1
    
    def check_crontab(self):
        """Reserved for future crontab integration"""
        # This will be implemented after sleeping on it :)
        # Ideas:
        # - Read ~/prog/ai/etc/crontab for scheduled tasks
        # - Execute scheduled Claude communication checks
        # - Manage automated message acknowledgments
        pass