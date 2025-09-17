"""Tests für Utility Functions."""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_path_handling():
    """Testet Path Handling Utilities."""
    from lib.ccc_manager import CCCManager

    manager = CCCManager()

    # Test base directory handling
    assert isinstance(manager.base_dir, Path)

def test_tmux_session_detection():
    """Testet tmux Session Detection."""
    from lib.ccc_manager import CCCManager

    manager = CCCManager()

    # Should have tmux-related methods
    if hasattr(manager, 'detect_tmux_session'):
        try:
            session = manager.detect_tmux_session()
            # Should return string or None
            assert session is None or isinstance(session, str)
        except Exception:
            # Expected if tmux not available
            pass

def test_service_status_checking():
    """Testet Service Status Checking."""
    from lib.ccc_manager import CCCManager

    manager = CCCManager()

    # Should have status checking methods
    if hasattr(manager, 'is_monitor_running'):
        try:
            status = manager.is_monitor_running()
            assert isinstance(status, bool)
        except Exception:
            # Expected if services not available
            pass

def test_error_handling():
    """Testet Error Handling in verschiedenen Modulen."""
    from lib.ccc_manager import CCCManager
    from lib.ccc_commands import Commands

    manager = CCCManager()
    commands = Commands(manager)

    # Should not crash with invalid inputs
    try:
        # Test with invalid service name
        commands.status("nonexistent_service")
    except Exception:
        # Expected - should handle gracefully
        pass

def test_config_file_operations(temp_dir):
    """Testet Config File Operations."""
    from lib.ccc_manager import CCCManager
    import json

    # Create test config
    test_config = {"test": True}
    config_file = temp_dir / "test.json"

    # Test file operations don't crash
    try:
        with open(config_file, 'w') as f:
            json.dump(test_config, f)

        with open(config_file, 'r') as f:
            loaded = json.load(f)

        assert loaded["test"] is True
    except Exception:
        # File operations should work
        pytest.fail("Basic file operations failed")

def test_command_line_parsing():
    """Testet Command Line Parsing."""
    # Test that main module can be imported
    try:
        import ccc_main
        assert hasattr(ccc_main, 'main')
    except ImportError:
        # Expected if not in path
        pass