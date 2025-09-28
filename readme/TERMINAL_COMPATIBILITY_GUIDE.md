# Terminal Compatibility Guide - CCC Character System

## ✅ Quick Reference for Claude-1

### WORKING EMOJIS (Safe to use):
```
🛡️ 💻 📊 🔒 ⚡ 😊 😱 🏆 📚 📋 🗂️ 🔍 ⭐ 🖥️ ⌨️ 🖱️ 💿 📷 📹 📺 🔊 🔉 🔈 🔇 📻 🎧
```

### FORBIDDEN EMOJIS (Never use):
```
🚨 🔥 🧪 📱 💾 🎯 🔴 🚀 📝 🌐 🔧 🤔 💪 🎉 🎊 💡 📂 📁 🔎 🌟 🌈 🎨 💽 📸 🎥 🔔 🔕 📢 📣 🎵 🎶 🎼 🎤
```

### ALWAYS SAFE ASCII & UNICODE:
```
ASCII: ! @ # $ % ^ & * ( ) - = + [ ] { } | \ / ? < >
Symbols: ✓ ✗ ● ○ ■ □ ▲ ▼ ► ◄ ⚠ ⛔ ❌ ✅
Box: ╔═══╗ ┌───┐ ▓▓▓ ░░░
```

## Usage Examples

### ✅ CORRECT:
```
✅ System operational
🛡️ Security active
💻 Terminal ready
📊 Stats available
● Task completed
```

### ❌ WRONG:
```
🚨 Alert system    → Use: ❌ Alert system
🔥 Hot features    → Use: ⚡ Hot features
🧪 Test results   → Use: ● Test results
📱 Mobile ready   → Use: 🖥️ Mobile ready
```

## SysOps Alert Format

### Standard Format:
```
################################################################################
  SYSOPS AKTION ERFORDERLICH
################################################################################

[!] PROBLEM: Description
[!] ORT: Location
[!] LÖSUNG: Solution

BEFEHL FÜR SEPARATES TERMINAL:
-------------------------------
command here
-------------------------------

>>> STATUS: WARTE AUF BESTÄTIGUNG (schreibe "erledigt")
```

## Validation Function

```python
from ccc_rule_enforcer import SysOpsAlert

# Check if text is terminal-compatible
is_valid, forbidden = SysOpsAlert.validate_characters("Text with 🚨")
if not is_valid:
    for char in forbidden:
        alternative = SysOpsAlert.suggest_alternatives(char)
        print(f"Replace {char} with {alternative}")
```

---
**Last updated:** 2025-09-22 - Based on CCC_CL1_07.md requirements
**Status:** Complete terminal compatibility system implemented