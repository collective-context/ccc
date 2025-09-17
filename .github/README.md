# GitHub Actions CI/CD Setup

This directory contains the CI/CD pipeline configuration for CCC Commander.

## Workflows

### 1. CI Workflow (`.github/workflows/ci.yml`)

**Triggers**: Push to main, Pull Requests to main

**Features**:
- **Matrix Testing**: Python 3.8, 3.9, 3.10, 3.11, 3.12
- **Dependency Installation**: pip install -e .[dev]
- **Code Quality**: ruff linting, mypy type checking
- **Testing**: pytest with coverage reporting
- **Security**: bandit, safety, pip-audit scanning
- **Build Validation**: Package building and verification
- **Artifacts**: Uploads dist/ packages for inspection

### 2. Release Workflow (`.github/workflows/release.yml`)

**Triggers**: GitHub Release creation

**Features**:
- **Full Test Suite**: All CI tests must pass
- **Security Validation**: Complete security scan
- **Package Building**: Python wheel and source distribution
- **TestPyPI Upload**: Validation deployment to test repository
- **PyPI Deployment**: Production package release
- **GitHub Release**: Automated release with artifacts

## Required Secrets

To enable PyPI deployment, configure these repository secrets:

### Repository Settings → Secrets and variables → Actions

1. **`PYPI_API_TOKEN`** (Required for production PyPI uploads)
   - Go to https://pypi.org/manage/account/token/
   - Create API token with scope for `cccmd` project
   - Add token to repository secrets

2. **`TEST_PYPI_API_TOKEN`** (Optional, for TestPyPI validation)
   - Go to https://test.pypi.org/manage/account/token/
   - Create API token for testing
   - Add token to repository secrets

### Token Configuration

```bash
# Example PyPI token format
# pypi-AgEIcHlwaS5vcmcCJGZhZGQ5...
```

## Pipeline Status

### Current Status
- ✅ **CI Pipeline**: Configured and functional
- ✅ **Security Scanning**: bandit, safety, pip-audit integrated
- ✅ **Matrix Testing**: Python 3.8-3.12 support validated
- ⚠️ **PyPI Deployment**: Requires API token configuration
- ✅ **Build Artifacts**: Automatic dist/ package generation

### Manual Deployment (if needed)

```bash
# Build packages
python -m build

# Check packages
twine check dist/*

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

## Troubleshooting

### Common Issues

1. **PyPI Authentication Errors**
   - Verify `PYPI_API_TOKEN` secret is configured
   - Check token scope includes project permissions
   - Ensure token is not expired

2. **Test Failures**
   - Check Python version compatibility
   - Verify dependencies in `pyproject.toml`
   - Review test logs for specific failures

3. **Build Failures**
   - Ensure `pyproject.toml` is valid
   - Check for missing dependencies
   - Verify package structure

### Security Scan Failures

Security scans use `continue-on-error: true` to avoid blocking releases for low-priority issues. Review scan results in:
- `reports/bandit.json` - Static security analysis
- `reports/safety.json` - Known vulnerability database
- pip-audit output - Package dependency vulnerabilities

## Workflow Improvements

Future enhancements to consider:
- **Trusted Publishing**: Configure OpenID Connect for PyPI
- **Code Coverage**: Set minimum coverage thresholds
- **Performance Testing**: Add benchmark comparisons
- **Documentation**: Auto-generate and deploy docs
- **Dependency Updates**: Automated dependency scanning