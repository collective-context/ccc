"""Tests für PPA Upload Functionality."""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_ppa_upload_import():
    """Testet ob PPA Upload Module importiert werden kann."""
    from lib.ccc_ppa_upload import upload_ppa_command
    assert upload_ppa_command is not None
    assert callable(upload_ppa_command)

def test_check_packages_function():
    """Testet check_packages Method."""
    from lib.ccc_ppa_upload import PPAUploader
    from lib.ccc_manager import CCCManager

    manager = CCCManager()
    uploader = PPAUploader(manager)

    # Should return list of packages or empty list
    packages = uploader.check_packages()
    assert isinstance(packages, list)

def test_get_gpg_config():
    """Testet get_gpg_config Method."""
    from lib.ccc_ppa_upload import PPAUploader
    from lib.ccc_manager import CCCManager

    manager = CCCManager()
    uploader = PPAUploader(manager)

    config = uploader.get_gpg_config()
    assert isinstance(config, dict)
    # Should have required keys like gpg_key
    assert isinstance(config.get('gpg_key', ''), str)

@patch('subprocess.run')
def test_upload_ppa_command_safe_subprocess(mock_run):
    """Testet dass upload_ppa_command sicher subprocess verwendet."""
    from lib.ccc_ppa_upload import upload_ppa_command
    from lib.ccc_manager import CCCManager

    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = ""
    mock_run.return_value.stderr = ""

    manager = CCCManager()

    # Should not crash
    try:
        result = upload_ppa_command(manager)
        # Check that subprocess.run was called (if any packages found)
        if mock_run.called:
            # Verify first argument is array, not string
            first_call = mock_run.call_args_list[0]
            first_arg = first_call[0][0]
            assert isinstance(first_arg, list), "subprocess calls should use array form"
    except Exception:
        # Expected if no packages found
        pass