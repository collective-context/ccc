"""Tests für CCC Manager."""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_manager_initialization():
    """Testet CCCManager Initialisierung."""
    from lib.ccc_manager import CCCManager

    manager = CCCManager()
    assert manager is not None
    assert hasattr(manager, 'config')

def test_manager_config_loading(temp_dir):
    """Testet Config-Loading im Manager."""
    from lib.ccc_manager import CCCManager

    # Test with temporary directory
    manager = CCCManager()
    assert manager.config is not None

def test_manager_service_methods():
    """Testet Service-Methoden des Managers."""
    from lib.ccc_manager import CCCManager

    manager = CCCManager()

    # Test if key methods exist
    assert hasattr(manager, 'load_config')
    assert hasattr(manager, 'save_config')
    assert callable(manager.load_config)
    assert callable(manager.save_config)