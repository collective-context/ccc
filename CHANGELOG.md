# Changelog

All notable changes to CCC Commander (cccmd) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.2] - 2025-09-17

### Added
- **Comprehensive Test Suite**: 96 tests across unit, integration, and security layers
- **GitHub Actions CI/CD Pipeline**: Matrix testing for Python 3.8-3.12
- **Automated Security Scanning**: bandit, safety, and pip-audit integration
- **PyPI Distribution Ready**: Automated TestPyPI and PyPI deployment
- **PPA Upload Tools**: Ubuntu PPA automation for `cccmd` package
- **Build Automation**: Makefile with security, test, and coverage targets
- **Coverage Reporting**: Integrated codecov and HTML coverage reports
- **Multi-mode Support**: dev, pipx, and apt installation modes
- First public release as `cccmd` on PyPI
- Ubuntu PPA support for easy installation
- XDG Base Directory Specification compliance
- Multi-agent orchestration with 4-agent pattern
- Session persistence via CONTEXT.md
- Support for 300+ AI models through OpenRouter
- Comprehensive installation documentation
- pyproject.toml for modern Python packaging

### Changed
- Package name from internal `ccc` to public `cccmd`
- Restructured for PyPI distribution with proper entry points
- Enhanced pytest configuration with comprehensive test discovery
- Updated all documentation for public release
- Improved error handling and input validation across all modules

### Fixed
- **Security Vulnerabilities**: Input sanitization and path traversal prevention
- **Command Injection Protection**: Safe subprocess execution patterns
- **Testing Infrastructure**: Resolved pytest configuration conflicts
- Path resolution issues in different environments
- Session management bugs
- Configuration file handling

### Security
- Implemented command injection prevention mechanisms
- Added path traversal protection for file operations
- Enhanced subprocess safety with array-form parameter validation
- Comprehensive security test coverage for all input vectors

## [0.2.0] - 2025-08-15

### Added
- TypeScript implementation
- Virtual filesystem for sessions
- Template system for work packages

### Changed
- Complete rewrite from prototype to production code

## [0.1.0] - 2025-07-01

### Added
- Initial proof of concept
- Basic multi-agent support
- Simple session management