"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.addSessionCommands = addSessionCommands;
const SimpleSessionManager_1 = require("../session/SimpleSessionManager");
function addSessionCommands(program) {
    const session = program.command('session');
    session
        .command('save <name>')
        .description('Save current session')
        .action((name) => {
        const manager = new SimpleSessionManager_1.SimpleSessionManager();
        const sessionData = {
            timestamp: new Date().toISOString(),
            name: name,
            cwd: process.cwd(),
            environment: {
                node_version: process.version,
                platform: process.platform,
            }
        };
        manager.saveSession(name, sessionData);
    });
    session
        .command('list')
        .description('List saved sessions')
        .action(() => {
        const manager = new SimpleSessionManager_1.SimpleSessionManager();
        const sessions = manager.listSessions();
        console.log('\nSaved Sessions:');
        if (sessions.length === 0) {
            console.log('  No sessions found');
        }
        else {
            sessions.forEach(s => console.log(`  - ${s}`));
        }
    });
    session
        .command('load <filename>')
        .description('Load and display session data')
        .action((filename) => {
        const manager = new SimpleSessionManager_1.SimpleSessionManager();
        try {
            const data = manager.loadSession(filename);
            console.log('\nSession Data:');
            console.log(JSON.stringify(data, null, 2));
        }
        catch (error) {
            console.error(`Error loading session: ${error instanceof Error ? error.message : String(error)}`);
        }
    });
}
//# sourceMappingURL=session-commands.js.map