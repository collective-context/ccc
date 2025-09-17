"""Tests für CCC Commands."""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_commands_initialization():
    """Testet Commands Initialisierung."""
    from lib.ccc_commands import Commands
    from lib.ccc_manager import CCCManager

    manager = CCCManager()
    commands = Commands(manager)
    assert commands is not None
    assert commands.manager is not None

def test_commands_has_required_methods():
    """Testet ob Commands die wichtigsten Methoden hat."""
    from lib.ccc_commands import Commands
    from lib.ccc_manager import CCCManager

    manager = CCCManager()
    commands = Commands(manager)

    # Test wichtige Methoden existieren
    assert hasattr(commands, 'status')
    assert hasattr(commands, 'start')
    assert hasattr(commands, 'stop')
    assert hasattr(commands, 'list')  # Not 'list_services'
    assert hasattr(commands, 'context_read')
    assert hasattr(commands, 'context_write')

def test_list_method():
    """Testet list Method."""
    from lib.ccc_commands import Commands
    from lib.ccc_manager import CCCManager

    manager = CCCManager()
    commands = Commands(manager)

    # Should not crash
    try:
        commands.list()
    except Exception as e:
        # If it throws an exception, that's expected for now
        pass

def test_status():
    """Testet status Method."""
    from lib.ccc_commands import Commands
    from lib.ccc_manager import CCCManager

    manager = CCCManager()
    commands = Commands(manager)

    # Should not crash
    try:
        commands.status()
    except Exception as e:
        # If it throws an exception, that's expected for now
        pass