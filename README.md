# CCC Commander - Collective Context Multi-Agent Orchestration

[![PyPI version](https://badge.fury.io/py/cccmd.svg)](https://badge.fury.io/py/cccmd)
[![Ubuntu PPA](https://img.shields.io/badge/Ubuntu-PPA%20Available-orange.svg)](https://launchpad.net/~collective-context/+archive/ubuntu/ccc)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Professional command-line tool for multi-agent AI orchestration, session management, and automated package deployment with flexible command abbreviations.

## Installation

### Ubuntu/Debian (Recommended - APT)
```bash
# Add PPA and install
sudo add-apt-repository ppa:collective-context/ccc
sudo apt update
sudo apt install ccc          # Base package
sudo apt install cccmd        # Complete development environment
```

### Universal (PIP/PIPX)
```bash
# Individual installation
pipx install cccmd

# Or with pip
pip install --user cccmd
```

### Development (DEV)
```bash
# Clone and setup development environment
git clone https://github.com/collective-context/ccc
cd ccc
pip install -e ".[dev]"
./ccc config mode dev          # Switch to development mode
```

### Installation Modes
- **APT**: System package via Ubuntu PPA (stable, auto-updates)
- **PIP**: Python package via PyPI (portable, user-managed)
- **DEV**: Development version (latest features, local development)

## Quick Start

```bash
# Check installation and version
ccc version                    # Short version info
ccc help                       # Show available commands

# Flexible command abbreviations (minimum 2 characters)
ccc he fu                      # → ccc help full (detailed help)
ccc gi pu ccc                  # → ccc git push ccc (quick git push)
ccc ex up ppa                  # → ccc exec upload ppa (package upload)

# Session management
ccc session start cl1         # Start session for Claude-1
ccc ses sav cl2               # Save session for Claude-2
ccc ses man list              # List JSON sessions

# Multi-agent context system
ccc context                   # Read own AI context
ccc co cl2                    # Read Claude-2's context
ccc context to cl2 -- "Hi"    # Send message to Claude-2

# Configuration management
ccc config show              # Show current configuration
ccc conf mode dev             # Switch to development mode
```

## Features

### Core Functionality
- ⚡ **Flexible Command Abbreviations**: Minimum 2-character shortcuts for all commands
- 🎭 **Multi-Agent Context System**: Communication between AI instances (cl1, cl2, ai1, ai2)
- 📝 **Session Management**: JSON-based session persistence with metadata
- 🚀 **Git Integration**: Automated website updates and GitHub push with testing
- ⚙️ **Configuration Management**: Mode switching (APT/PIP/DEV) and settings

### Professional Package Management
- 📦 **Ubuntu PPA Integration**: Automated package uploads to Launchpad
- 🔧 **Professional Build System**: Multi-distribution builds with identical checksums
- 🛡️ **Duplicate Prevention**: Automatic checking to prevent Launchpad rejections
- 🔐 **GPG Signing**: Automated package signing with fallback options
- 📊 **Build Status Monitoring**: Real-time feedback with professional logging

### Developer Experience
- 📋 **Comprehensive Help System**: Built-in documentation with examples
- 🛠️ **Troubleshooting Guides**: Integrated problem-solving assistance
- 🔄 **Version Management**: Multi-mode installation support
- 📄 **Professional Logging**: Clear status indicators and error handling

## Command Reference

### Package Management (Professional System)
```bash
ccc exec upload ppa           # Upload all packages (base + meta)
ccc ex up ppa ccc            # Upload base packages only
ccc ex up ppa cccmd          # Upload meta packages only
ccc ex sh ppa                # Show PPA configuration
```

### Git Integration
```bash
ccc git push homepage        # Update collective-context.org
ccc gi pu ccc               # Quick GitHub push
ccc gi pu ccc tests         # Push with full test suite
```

### Session Management
```bash
ccc session start <ai>      # Start session for AI instance
ccc ses sav <ai>            # Save session
ccc ses man save <name>     # Save JSON session
ccc ses man list            # List saved sessions
```

### Configuration
```bash
ccc config show            # Show current configuration
ccc config mode <mode>     # Switch installation mode
ccc conf mo dev            # Switch to development mode
```

### Help and Version
```bash
ccc help                   # Show compact help
ccc help full             # Show comprehensive help
ccc version               # Show version info
ccc ve fu                 # Show detailed version
```

## Documentation

- **Built-in Help**: `ccc help full` for comprehensive command reference
- **Online Documentation**: https://collective-context.org/ccc/installation/
- **Ubuntu PPA**: https://launchpad.net/~collective-context/+archive/ubuntu/ccc

## Contributing

Contributions welcome! Join the discussion at [GitHub Discussions](https://github.com/collective-context/ccc/discussions) or open issues and pull requests.

## License

MIT - See [LICENSE](LICENSE) file for details.
