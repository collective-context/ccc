"""
CCC Command Parser - Simplified for Step 1 Migration
Essential command parsing functionality extracted from legacy system
"""

class CommandParser:
    """Simplified command parser for core functionality"""
    
    def __init__(self):
        # Minimal command tree for Step 1 - only help commands
        self.command_tree = {
            'help': ['he', 'hel', 'help'],
            'full': ['fu', 'ful', 'full'],
            'experimental': ['ex', 'exp', 'expe', 'exper', 'experi', 'experim', 'experime', 'experimen', 'experiment', 'experimenta', 'experimental'],
            'version': ['ve', 'ver', 'vers', 'versi', 'versio', 'version'],
            'config': ['co', 'con', 'conf', 'confi', 'config'],
            # Core sections for help
            'core': ['co', 'cor', 'core'],
            'session': ['se', 'ses', 'sess', 'sessi', 'sessio', 'session'],
            'context': ['co', 'con', 'cont', 'conte', 'contex', 'context'],
            'git': ['gi', 'git']
        }
    
    def parse_command(self, args):
        """
        Parse command arguments with flexible abbreviations
        Returns: (expanded_commands, free_string, success)
        """
        if not args:
            return [], "", True
        
        expanded_commands = []
        free_string = ""
        
        # Simple parsing for Step 1 - just expand abbreviations
        for i, arg in enumerate(args):
            if arg == '--':
                # Everything after -- is free string
                free_string = ' '.join(args[i+1:])
                break
            
            # Try to expand the command
            expanded = self._expand_command(arg)
            if expanded:
                expanded_commands.append(expanded)
            else:
                # Unknown command - keep as is for now
                expanded_commands.append(arg)
        
        return expanded_commands, free_string, True
    
    def _expand_command(self, cmd):
        """Expand abbreviated command to full form"""
        cmd_lower = cmd.lower()
        
        # Look for exact matches first
        if cmd_lower in self.command_tree:
            return cmd_lower
        
        # Look for abbreviation matches
        for full_cmd, abbreviations in self.command_tree.items():
            if cmd_lower in abbreviations:
                return full_cmd
        
        # No match found
        return None
    
    def display_expansion(self, original_args, expanded_commands, free_string):
        """Display command expansion for user feedback"""
        if original_args != expanded_commands:
            print(f"Expanded: {' '.join(original_args)} → {' '.join(expanded_commands)}")
            if free_string:
                print(f"Free string: {free_string}")
    
    def validate_command_chain(self, expanded_commands):
        """Validate that the command sequence makes sense"""
        if not expanded_commands:
            return False
        
        # For Step 1, just validate basic help patterns
        if expanded_commands[0] == 'help':
            return True
        if expanded_commands[0] == 'version':
            return True
        if expanded_commands[0] == 'config':
            return True
        
        # Allow any other commands for now (they'll show not implemented message)
        return True