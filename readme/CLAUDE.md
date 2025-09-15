# CCC - Collective Context Commander Integration

## Claude Code Setup Instructions

### For Users (pipx install ccc)

If you installed CCC via `pipx install ccc`, this tool is now available globally as `ccc` command.

**Quick Start Commands:**
```bash
# Show all available services
ccc list

# Get help
ccc help

# Start multi-agent session logging  
ccc start save

# Create 4-agent tmux layout
ccc tmux init --agents=4

# Monitor your AI conversations
ccc start dialog
```

### Configuration

CCC uses environment variables for project-specific settings:

```bash
# Set your main project directory
export CCC_PROJECT_DIR="~/your-project"

# For permanent setup, add to your ~/.bashrc:
echo 'export CCC_PROJECT_DIR="~/your-project"' >> ~/.bashrc
```

### Integration with Claude Code

CCC enhances Claude Code with:

1. **Multi-Agent Orchestration**: Coordinate multiple AI assistants
2. **Session Management**: Automatic session logging and restoration  
3. **tmux Integration**: Professional 4-pane terminal layouts
4. **Inter-Agent Communication**: Claude-to-Claude message passing
5. **Service Monitoring**: Real-time status of AI services

### Common Workflows

#### Orchestra Pattern (4-Agent Setup)
```bash
# 1. Start session logging
ccc start save

# 2. Create tmux layout  
ccc tmux init --agents=4

# 3. Start agent communication
ccc start dialog

# 4. Check status
ccc list
```

#### Pipeline Development
```bash
# Start autoinput for regular check-ins
ccc start autoinput -t=5  # Every 5 minutes

# Monitor all services
ccc status
```

### Troubleshooting

**Command not found?**
```bash
# Verify installation
which ccc
ccc --version

# If not found, reinstall:
pipx install ccc
```

**No project directory?**
```bash
# Set project directory
export CCC_PROJECT_DIR="$(pwd)"
ccc config
```

**tmux issues?**
```bash
# Install tmux if missing
sudo apt install tmux  # Linux
brew install tmux      # macOS

# Test tmux integration
ccc tmux status
```

### Documentation

- **Full Documentation**: https://collective-context.org
- **CLI Reference**: https://collective-context.org/ccc/cli/
- **Patterns Guide**: https://collective-context.org/patterns/
- **Installation Guide**: https://collective-context.org/quickstart/installation/

### Support

- **GitHub Issues**: https://github.com/collective-context/ccc/issues
- **Discord Community**: https://discord.gg/collective-context

---

**Ready to revolutionize your AI workflow with CCC!** ⚡