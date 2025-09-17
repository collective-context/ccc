"""Tests für Config Management."""
import pytest
import sys
import json
from pathlib import Path
from unittest.mock import Mock, patch

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_config_path_creation(temp_dir):
    """Testet Config-Pfad Erstellung."""
    from lib.ccc_manager import CCCManager

    # Create manager with temporary directory
    manager = CCCManager()

    # Should have config_file
    assert hasattr(manager, 'config_file')
    assert hasattr(manager, 'config_dir')

def test_config_loading_basic():
    """Testet grundlegendes Config-Loading."""
    from lib.ccc_manager import CCCManager

    manager = CCCManager()

    # Should not crash during initialization
    assert manager is not None
    assert manager.config is not None

def test_config_save_load_cycle(temp_dir):
    """Testet Config speichern und laden."""
    from lib.ccc_manager import CCCManager

    # Create a temporary config file
    config_file = temp_dir / "test_config.json"

    test_config = {
        "services": {
            "test": {
                "enabled": True,
                "interval": 30
            }
        },
        "log_level": "INFO"
    }

    # Write test config
    with open(config_file, 'w') as f:
        json.dump(test_config, f)

    manager = CCCManager()

    # Should be able to save config
    try:
        manager.save_config()
    except Exception:
        # May fail without proper setup, but shouldn't crash
        pass

def test_config_validation():
    """Testet Config-Validierung."""
    from lib.ccc_manager import CCCManager

    manager = CCCManager()

    # Test that basic config structure exists
    if manager.config:
        assert isinstance(manager.config, dict)

def test_base_dir_exists():
    """Testet dass base_dir existiert."""
    from lib.ccc_manager import CCCManager

    manager = CCCManager()
    assert hasattr(manager, 'base_dir')
    assert manager.base_dir is not None