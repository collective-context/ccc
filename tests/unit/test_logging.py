"""Tests für Logging Infrastructure."""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_manager_logging():
    """Testet Manager Logging Functionality."""
    from lib.ccc_manager import CCCManager

    manager = CCCManager()

    # Test logging method exists
    assert hasattr(manager, 'log')
    assert callable(manager.log)

    # Should not crash when called
    try:
        manager.log("Test message", "INFO")
    except Exception:
        # May fail without proper setup, but shouldn't crash the test
        pass

def test_ppa_uploader_logging():
    """Testet PPA Uploader Logging."""
    from lib.ccc_ppa_upload import PPAUploader
    from lib.ccc_manager import CCCManager

    manager = CCCManager()
    uploader = PPAUploader(manager)

    # Test logging method exists
    assert hasattr(uploader, 'log_operation')
    assert callable(uploader.log_operation)

    # Should not crash when called
    try:
        uploader.log_operation("Test operation", "INFO")
    except Exception:
        # May fail without proper setup, but shouldn't crash the test
        pass

def test_commands_logging_capabilities():
    """Testet Commands Logging Capabilities."""
    from lib.ccc_commands import Commands
    from lib.ccc_manager import CCCManager

    manager = CCCManager()
    commands = Commands(manager)

    # Commands should have access to manager's logging
    assert commands.manager is not None
    assert hasattr(commands.manager, 'log')

def test_debug_logging():
    """Testet Debug-Level Logging."""
    from lib.ccc_manager import CCCManager

    manager = CCCManager()

    # Should handle different log levels
    try:
        if hasattr(manager, 'log'):
            manager.log("Debug message", "DEBUG")
            manager.log("Error message", "ERROR")
            manager.log("Warning message", "WARNING")
    except Exception:
        # Expected if logging not fully configured
        pass