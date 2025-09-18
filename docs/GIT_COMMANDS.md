# 📝 CCC Git Commands Documentation

## Overview

CCC Commander provides integrated Git workflows for maintaining code quality and managing deployments.

## 🚀 Available Commands

### 1. `ccc git push homepage`
**Purpose**: Update collective-context.org with session achievements

```bash
ccc git push homepage
```

**What it does:**
- Prompts Claude to reflect on session achievements
- Updates documentation on https://collective-context.org
- Publishes release notes and feature announcements

---

### 2. `ccc git push ccc` (Quick Mode)
**Purpose**: Quick push to GitHub for small changes

```bash
ccc git push ccc
```

**What it does:**
- ⚡ **Skips** tests and security audits (fast)
- 📝 Commits uncommitted changes
- 🚀 Pushes directly to GitHub repository
- ⏱️ **Time**: ~5 seconds

**Use when:**
- Making small documentation updates
- Fixing typos or comments
- Non-critical changes that don't affect functionality
- You're confident the changes are safe

**Commit format:**
```
chore: CCC quick update

Quick push for minor changes:
- Small improvements and fixes
- No breaking changes
- Tests skipped for speed
```

---

### 3. `ccc git push ccc tests` (Full Mode)
**Purpose**: Full quality control, security audit, then push to GitHub

```bash
ccc git push ccc tests
```

**Alternative forms:**
```bash
ccc git push ccc test     # singular form
ccc git push ccc full     # explicit full mode
ccc git push ccc --tests  # with flag
```

**What it does:**
1. 🧪 **Runs full test suite** (96 tests)
2. 🔒 **Security audit:**
   - Checks for hardcoded secrets
   - Scans for unsafe subprocess calls
   - Detects SQL injection patterns
3. 📋 **Code quality checks:**
   - Python syntax validation
   - Import verification
4. 📝 **Commits changes** with detailed message
5. 🚀 **Pushes to GitHub**
6. ⏱️ **Time**: ~60 seconds

**Use when:**
- Adding new features
- Modifying core functionality
- Before releases
- When security is critical
- Making significant changes

**Commit format:**
```
feat: CCC update with full quality control

Comprehensive validation including:
- 96 test suite fully validated
- Security audit completed
- Quality control passed
- All checks verified before push
```

---

## 📊 Comparison Table

| Feature | `ccc git push ccc` | `ccc git push ccc tests` |
|---------|-------------------|-------------------------|
| **Speed** | ⚡ ~5 seconds | ⏱️ ~60 seconds |
| **Tests** | ❌ Skipped | ✅ 96 tests run |
| **Security Audit** | ❌ Skipped | ✅ Full scan |
| **Quality Check** | ❌ Skipped | ✅ Complete |
| **Commit Type** | `chore:` | `feat:` |
| **Use Case** | Small changes | Major updates |
| **Risk Level** | Higher | Lower |
| **Recommended For** | Docs, typos | Features, fixes |

---

## 🎯 Best Practices

### When to use Quick Mode (`ccc git push ccc`)
✅ **Good for:**
- README updates
- Documentation fixes
- Comment improvements
- Configuration tweaks
- Non-code changes

❌ **Avoid for:**
- New features
- Bug fixes in core logic
- Security-related changes
- Before releases
- First-time contributions

### When to use Full Mode (`ccc git push ccc tests`)
✅ **Always use for:**
- New feature implementations
- Bug fixes
- Security updates
- Before version releases
- Changes to core modules
- PR merges
- Production deployments

---

## 💡 Pro Tips

1. **Default to safety**: When in doubt, use `tests` mode
2. **CI/CD backup**: GitHub Actions will catch issues even if you skip local tests
3. **Combine with aliases**: Create shell aliases for common operations
   ```bash
   alias qpush='ccc git push ccc'
   alias fpush='ccc git push ccc tests'
   ```
4. **Check before push**: Always review `git diff` before pushing
5. **Use for releases**: Always use full mode before creating releases

---

## 🔧 Implementation Details

### Directory Management
- Automatically switches to `~/prog/ai/git/collective-context/ccc`
- Works from any directory

### Error Handling
- Tests failures stop the push (full mode)
- Security warnings are informational only
- Git conflicts prevent push

### Integration
- Works with GitHub Actions CI/CD
- Compatible with PyPI release workflow
- Triggers homepage documentation updates

---

## 📝 Examples

### Quick documentation fix
```bash
# Fix a typo in README
echo "Fixed typo" >> README.md
ccc git push ccc
# Done in 5 seconds! ⚡
```

### Feature development
```bash
# After implementing new feature
vim lib/ccc_commands.py
# ... make changes ...
ccc git push ccc tests
# Full validation before push ✅
```

### Release preparation
```bash
# Always use full validation for releases
ccc git push ccc tests
ccc exec upload ppa
ccc git push homepage
```

---

## 🚀 Summary

The improved `ccc git push ccc` command provides flexibility:
- **Quick mode** for rapid iterations on safe changes
- **Full mode** for comprehensive validation when it matters
- **Smart defaults** that encourage best practices
- **Clear feedback** about what's being skipped or validated

Choose the right mode for your workflow and maintain code quality with confidence!