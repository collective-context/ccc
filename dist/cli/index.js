#!/usr/bin/env node
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const commander_1 = require("commander");
const session_commands_1 = require("./session-commands");
const program = new commander_1.Command();
program
    .name('ccc-session')
    .description('CCC Session Management CLI')
    .version('1.0.0');
// Add session commands
(0, session_commands_1.addSessionCommands)(program);
program.parse();
//# sourceMappingURL=index.js.map