#!/usr/bin/env python3
"""
CC - Collective Context Commander Short Entry Point
Alias for ccc command
"""

import sys
import os
from pathlib import Path

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent / "lib"))

# Import main function from ccc_main
from ccc_main import main

if __name__ == "__main__":
    # Execute the same main function as ccc
    sys.exit(main())