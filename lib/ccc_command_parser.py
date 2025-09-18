"""
CCC Command Parser - Flexible abbreviation system
"""

class CommandParser:
    def __init__(self):
        # Define command tree with all possible commands and their abbreviations
        self.command_tree = {
            'ccc': ['cc', 'ccc'],
            'git': ['gi', 'git'],
            'push': ['pu', 'pus', 'push'],
            'pull': ['pl', 'pul', 'pull'],
            'exec': ['ex', 'exe', 'exec'],
            'upload': ['up', 'upl', 'uplo', 'uploa', 'upload'],
            'config': ['co', 'con', 'conf', 'confi', 'config'],
            'session': ['se', 'ses', 'sess', 'sessi', 'sessio', 'session'],
            'context': ['co', 'con', 'cont', 'conte', 'contex', 'context'],
            'help': ['he', 'hel', 'help'],
            'status': ['st', 'sta', 'stat', 'statu', 'status'],
            'start': ['st', 'sta', 'star', 'start'],
            'stop': ['st', 'sto', 'stop'],
            'restart': ['re', 'res', 'rest', 'resta', 'restar', 'restart'],
            'list': ['li', 'lis', 'list'],
            'test': ['te', 'tes', 'test'],
            'tests': ['te', 'tes', 'test', 'tests'],
            'full': ['fu', 'ful', 'full'],
            'show': ['sh', 'sho', 'show'],
            'set': ['se', 'set'],
            'homepage': ['ho', 'hom', 'home', 'homep', 'homepa', 'homepag', 'homepage'],
            'ppa': ['pp', 'ppa'],
            'ccc': ['cc', 'ccc'],  # can be command or target
            'version': ['ve', 'ver', 'vers', 'versi', 'versio', 'version'],
            'fix': ['fi', 'fix'],
            'gpg': ['gp', 'gpg']
        }

        # Define conflicts where abbreviations are ambiguous
        self.conflicts = {
            'co': ['config', 'context'],  # Need at least 4 letters (conf vs cont)
            'con': ['config', 'context'],  # Need at least 4 letters (conf vs cont)
            'pu': ['push', 'pull'],  # Need at least 3 letters (pus vs pul)
            'st': ['status', 'start', 'stop'],  # Need at least 3 letters
            're': ['restart'],  # Need at least 3 letters
            'se': ['session', 'set'],  # Need at least 3 letters
            'te': ['test', 'tests'],  # Need at least 3 letters
        }

    def parse_command(self, args):
        """
        Parse command arguments with flexible abbreviations
        Returns: (expanded_command_list, free_string, success)
        """
        if not args:
            return [], "", False

        # Check for free string separator
        free_string = ""
        if '--' in args:
            dash_index = args.index('--')
            command_args = args[:dash_index]
            free_string = ' '.join(args[dash_index + 1:])
        else:
            command_args = args

        # Expand each command part
        expanded_commands = []
        for i, arg in enumerate(command_args):
            expanded = self.expand_command(arg, i, command_args)
            if expanded is None:
                return [], "", False
            expanded_commands.append(expanded)

        return expanded_commands, free_string, True

    def expand_command(self, abbrev, position, full_command_context):
        """
        Expand a single command abbreviation
        Returns expanded command or None if ambiguous/invalid
        """
        # Check if it's already a full command
        if abbrev in self.command_tree:
            return abbrev

        # Find possible matches
        matches = []
        for full_cmd, abbreviations in self.command_tree.items():
            if any(abbr.startswith(abbrev) for abbr in abbreviations):
                matches.append(full_cmd)

        # Remove duplicates while preserving order
        matches = list(dict.fromkeys(matches))

        # Check for ambiguity
        if len(matches) == 0:
            print(f"❌ Unknown command: '{abbrev}'")
            self.show_available_commands(position, full_command_context)
            return None
        elif len(matches) > 1:
            # Check if abbreviation is too short and conflicts
            if abbrev in self.conflicts:
                print(f"❌ Ambiguous command: '{abbrev}' could be: {', '.join(self.conflicts[abbrev])}")
                print(f"💡 Use at least 3 characters for clarity")
                return None
            else:
                print(f"❌ Ambiguous command: '{abbrev}' matches: {', '.join(matches)}")
                print(f"💡 Use more characters for clarity")
                return None

        return matches[0]

    def show_available_commands(self, position, context):
        """Show available commands based on context"""
        if position == 0:
            print("Available commands: ccc, git, exec, config, session, context, help, status, version")
        elif position == 1 and len(context) > 0:
            if context[0] in ['git', 'gi']:
                print("Available git commands: push, pull")
            elif context[0] in ['exec', 'ex']:
                print("Available exec commands: upload, fix")
            elif context[0] in ['config', 'co', 'con']:
                print("Available config commands: show, set")
            else:
                print("Available commands depend on first command")
        else:
            print("💡 Use 'ccc help' for complete command reference")

    def display_expansion(self, original_args, expanded_commands, free_string):
        """Display the command expansion before execution"""
        original_cmd = ' '.join(original_args)
        expanded_cmd = ' '.join(expanded_commands)

        if free_string:
            expanded_cmd += f" -- {free_string}"

        if original_cmd != expanded_cmd:
            print(f"🔍 Expanding: '{original_cmd}' → '{expanded_cmd}'")
            print()

    def validate_command_chain(self, expanded_commands):
        """Validate that the expanded command chain makes sense"""
        if len(expanded_commands) == 0:
            return False

        # Define valid command patterns
        valid_patterns = [
            ['help'],
            ['version'],
            ['status'],
            ['config', 'show'],
            ['config', 'set'],
            ['session'],
            ['context'],
            ['git', 'push', 'homepage'],
            ['git', 'push', 'ccc'],
            ['git', 'push', 'ccc', 'test'],
            ['git', 'push', 'ccc', 'tests'],
            ['git', 'push', 'ccc', 'full'],
            ['exec', 'upload', 'ppa'],
            ['exec', 'fix', 'gpg'],
        ]

        # Check if command matches any valid pattern
        for pattern in valid_patterns:
            if len(expanded_commands) >= len(pattern):
                if expanded_commands[:len(pattern)] == pattern:
                    return True

        return False