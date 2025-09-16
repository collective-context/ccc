"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.safeExecute = safeExecute;
const child_process_1 = require("child_process");
// NIEMALS shell: true verwenden!
function safeExecute(command, args = []) {
    return new Promise((resolve, reject) => {
        // Whitelist erlaubter Commands
        const ALLOWED_COMMANDS = ['git', 'npm', 'node'];
        if (!ALLOWED_COMMANDS.includes(command)) {
            reject(new Error(`Command not allowed: ${command}`));
            return;
        }
        // Spawn ohne Shell
        const proc = (0, child_process_1.spawn)(command, args, {
            shell: false, // KRITISCH: Niemals true!
            stdio: 'pipe'
        });
        let output = '';
        proc.stdout.on('data', (data) => output += data);
        proc.on('close', (code) => {
            if (code === 0)
                resolve(output);
            else
                reject(new Error(`Command failed with code ${code}`));
        });
    });
}
// Beispiel-Nutzung:
// await safeExecute('git', ['status']); // OK
// await safeExecute('rm', ['-rf', '/']); // BLOCKED
//# sourceMappingURL=safe-exec.js.map