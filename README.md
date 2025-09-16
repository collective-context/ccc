# CCC Commander (cccmd) - Collective Context Multi-Agent Orchestration

[![PyPI version](https://badge.fury.io/py/cccmd.svg)](https://badge.fury.io/py/cccmd)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Pragmatic multi-agent AI orchestration for the Collective Context ecosystem.

## Installation

### Via pipx (Recommended)
```bash
pipx install cccmd
```

### Via pip
```bash
pip install --user cccmd
```

### From Source (Development)
```bash
git clone https://github.com/collective-context/ccc
cd ccc
pip install -e ".[dev]"
```

## Quick Start

```bash
# Initialize a new CC session
cccmd init my-project

# Create an agent configuration
cccmd agent create --name claude-1 --type aider

# Start orchestration
cccmd orchestrate
```

## Features

- 🎭 Multi-agent orchestration with 4-agent pattern
- 🔄 Session persistence via CONTEXT.md
- 📦 XDG Base Directory compliance
- 🚀 Support for 300+ AI models via OpenRouter
- 🔒 Privacy-first options with self-hosting
- 🎯 Pragmatic hybrid approach (FOSS + selected tools)

## Documentation

Full documentation available at: https://collective-context.org/ccc/

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT - See [LICENSE](LICENSE) file for details.
