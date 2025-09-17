"""Gemeinsame Test-Fixtures für alle Tests."""
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock

@pytest.fixture
def temp_dir():
    """Erstellt temporäres Verzeichnis für Tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def mock_config(temp_dir):
    """Mock-Konfiguration für Tests."""
    return {
        "mode": "dev",
        "config_path": temp_dir / "config.yaml",
        "data_dir": temp_dir / "data",
    }

@pytest.fixture
def cli_runner():
    """CLI Test Runner."""
    from click.testing import CliRunner
    return CliRunner()