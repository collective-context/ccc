#!/usr/bin/env node

import { Command } from 'commander';
import { addSessionCommands } from './session-commands';

const program = new Command();

program
  .name('ccc-session')
  .description('CCC Session Management CLI')
  .version('1.0.0');

// Add session commands
addSessionCommands(program);

program.parse();