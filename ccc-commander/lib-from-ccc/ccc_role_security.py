#!/usr/bin/env python3
"""
CCC Role Security Module
========================
Ensures that role changes can ONLY happen through official 'ccc session start' command.
Maintains strict role normalization and identity management.
"""

import os
import json
from pathlib import Path
from datetime import datetime

class RoleSecurityManager:
    """Manages secure role assignments and prevents unauthorized role changes"""

    # Official role definitions (single source of truth)
    OFFICIAL_ROLES = {
        # Primary identifiers (normalized lowercase)
        "claude-1": {
            "name": "Claude-1",
            "alias": "CL1",
            "role": "System Architect & Conductor",
            "description": "Technical leadership, system design, implementation"
        },
        "claude-2": {
            "name": "Claude-2",
            "alias": "CL2",
            "role": "Quality Gate & Code Review",
            "description": "Code quality, testing, security review"
        },
        "aider-1": {
            "name": "Aider-1",
            "alias": "AI1",
            "role": "Primary Code Implementation",
            "description": "Main code development and implementation"
        },
        "aider-2": {
            "name": "Aider-2",
            "alias": "AI2",
            "role": "Parallel Development & Testing",
            "description": "Parallel development tasks and testing"
        }
    }

    # Accepted aliases (all normalize to primary identifier)
    ROLE_ALIASES = {
        # Claude-1 aliases
        "cl1": "claude-1",
        "CL1": "claude-1",
        "Claude-1": "claude-1",
        "CLAUDE-1": "claude-1",

        # Claude-2 aliases
        "cl2": "claude-2",
        "CL2": "claude-2",
        "Claude-2": "claude-2",
        "CLAUDE-2": "claude-2",

        # Aider-1 aliases
        "ai1": "aider-1",
        "AI1": "aider-1",
        "Aider-1": "aider-1",
        "AIDER-1": "aider-1",

        # Aider-2 aliases
        "ai2": "aider-2",
        "AI2": "aider-2",
        "Aider-2": "aider-2",
        "AIDER-2": "aider-2"
    }

    def __init__(self, session_file_path=None):
        """Initialize role security manager"""
        self.session_file = session_file_path or Path.home() / ".config" / "ccc" / "current_role.json"
        self.current_role = None
        self.load_current_role()

    def normalize_role_identifier(self, identifier):
        """
        Normalize any role identifier to canonical form
        Returns: (normalized_id, role_info) or (None, None) if invalid
        """
        if not identifier:
            return None, None

        # First check direct match
        normalized = identifier.lower()
        if normalized in self.OFFICIAL_ROLES:
            return normalized, self.OFFICIAL_ROLES[normalized]

        # Check aliases
        if identifier in self.ROLE_ALIASES:
            normalized = self.ROLE_ALIASES[identifier]
            return normalized, self.OFFICIAL_ROLES[normalized]

        # Try with lowercase
        if identifier.lower() in self.ROLE_ALIASES:
            normalized = self.ROLE_ALIASES[identifier.lower()]
            return normalized, self.OFFICIAL_ROLES[normalized]

        return None, None

    def set_role(self, identifier, source="session_start"):
        """
        Set the current role (ONLY allowed from session_start)
        """
        if source != "session_start":
            raise SecurityError(
                f"⛔ SECURITY VIOLATION: Role change attempted from '{source}'\n"
                f"Role changes are ONLY allowed through 'ccc session start' command!"
            )

        normalized_id, role_info = self.normalize_role_identifier(identifier)

        if not normalized_id:
            raise ValueError(f"❌ Unknown role identifier: {identifier}")

        self.current_role = {
            "id": normalized_id,
            "name": role_info["name"],
            "alias": role_info["alias"],
            "role": role_info["role"],
            "description": role_info["description"],
            "set_at": datetime.now().isoformat(),
            "set_by": "ccc session start"
        }

        self.save_current_role()

        return self.current_role

    def get_current_role(self):
        """Get the current role information"""
        return self.current_role

    def verify_role_command(self, command_string):
        """
        Verify that a role change command is legitimate
        Returns True only for valid 'ccc session start' commands
        """
        valid_patterns = [
            "ccc session start",
            "ccc se start",
            "ccc sess start",
            "./ccc session start",
            "./ccc se start",
            "./ccc sess start"
        ]

        # Normalize command
        cmd_lower = command_string.strip().lower()

        # Check if it starts with any valid pattern
        for pattern in valid_patterns:
            if cmd_lower.startswith(pattern):
                return True

        return False

    def save_current_role(self):
        """Save current role to persistent storage"""
        if self.current_role:
            with open(self.session_file, 'w') as f:
                json.dump(self.current_role, f, indent=2)

    def load_current_role(self):
        """Load current role from persistent storage"""
        if self.session_file.exists():
            try:
                with open(self.session_file, 'r') as f:
                    self.current_role = json.load(f)
            except:
                self.current_role = None

    def clear_role(self):
        """Clear the current role (for session end)"""
        self.current_role = None
        if self.session_file.exists():
            self.session_file.unlink()

    def get_role_display(self):
        """Get formatted role display string"""
        if not self.current_role:
            return "No role assigned"

        return (
            f"🎭 Current Role: {self.current_role['name']} ({self.current_role['alias']})\n"
            f"📋 Function: {self.current_role['role']}\n"
            f"📝 Description: {self.current_role['description']}"
        )

class SecurityError(Exception):
    """Raised when security violation is detected"""
    pass

# Module-level convenience functions
_manager = None

def get_manager():
    """Get or create the singleton manager"""
    global _manager
    if _manager is None:
        _manager = RoleSecurityManager()
    return _manager

def set_role(identifier, source="session_start"):
    """Set role through security manager"""
    return get_manager().set_role(identifier, source)

def get_current_role():
    """Get current role through security manager"""
    return get_manager().get_current_role()

def verify_role_command(command_string):
    """Verify role command through security manager"""
    return get_manager().verify_role_command(command_string)

def get_role_display():
    """Get role display through security manager"""
    return get_manager().get_role_display()

if __name__ == "__main__":
    # Test the role security system
    print("CCC Role Security Test")
    print("=" * 60)

    manager = RoleSecurityManager()

    # Test normalization
    test_cases = ["cl1", "CL1", "Claude-1", "CLAUDE-1", "ai2", "AI2", "invalid"]
    for test in test_cases:
        normalized, info = manager.normalize_role_identifier(test)
        if normalized:
            print(f"✅ '{test}' → {info['name']} ({info['alias']})")
        else:
            print(f"❌ '{test}' → Invalid")

    print("\n" + "=" * 60)

    # Test command verification
    commands = [
        "ccc session start cl1",
        "ccc se start CL2",
        "./ccc sess start ai1",
        "some other command",
        "context to cl1"
    ]

    for cmd in commands:
        if manager.verify_role_command(cmd):
            print(f"✅ Valid role command: {cmd}")
        else:
            print(f"❌ Invalid role command: {cmd}")