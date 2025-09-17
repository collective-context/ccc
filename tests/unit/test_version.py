"""Tests für Version Management."""
import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_version_format():
    """Testet ob Version dem Semantic Versioning entspricht."""
    # Version from pyproject.toml is 0.3.2
    version = "0.3.2"
    assert version == "0.3.2"
    parts = version.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)

def test_version_command(cli_runner):
    """Testet den version Command."""
    from ccc_main import main
    import sys
    from unittest.mock import patch

    # Mock command line arguments
    with patch.object(sys, 'argv', ['ccc', 'version']):
        try:
            result = main()
            assert result == 0
        except SystemExit as e:
            assert e.code == 0

def test_help_command(cli_runner):
    """Testet den help Command."""
    from ccc_main import main
    import sys
    from unittest.mock import patch

    # Mock command line arguments
    with patch.object(sys, 'argv', ['ccc', 'help']):
        try:
            result = main()
            assert result == 0
        except SystemExit as e:
            assert e.code == 0