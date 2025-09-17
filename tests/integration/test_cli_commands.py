"""Integration Tests für CLI Commands."""
import pytest
import sys
from pathlib import Path
from unittest.mock import patch

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_main_no_arguments():
    """Testet main() ohne Argumente."""
    from ccc_main import main

    with patch.object(sys, 'argv', ['ccc']):
        result = main()
        assert result == 0

def test_help_command_integration():
    """Testet Help-Output."""
    from ccc_main import main

    with patch.object(sys, 'argv', ['ccc', 'help']):
        result = main()
        assert result == 0

def test_version_command_integration():
    """Testet Version-Output."""
    from ccc_main import main

    with patch.object(sys, 'argv', ['ccc', 'version']):
        result = main()
        assert result == 0

def test_context_command():
    """Testet context Command - currently expects error since methods not implemented."""
    from ccc_main import main

    with patch.object(sys, 'argv', ['ccc', 'context']):
        result = main()
        assert result == 1  # Expect error since handle_context_command not implemented

def test_session_command():
    """Testet session Command - currently expects error since methods not implemented."""
    from ccc_main import main

    with patch.object(sys, 'argv', ['ccc', 'session']):
        result = main()
        assert result == 1  # Expect error since handle_session_command not implemented

def test_unknown_command():
    """Testet Verhalten bei unbekanntem Command."""
    from ccc_main import main

    with patch.object(sys, 'argv', ['ccc', 'unknown_command']):
        result = main()
        assert result == 1  # Should return error code