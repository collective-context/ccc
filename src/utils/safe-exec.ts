import { spawn } from 'child_process';

// NIEMALS shell: true verwenden!
export function safeExecute(
  command: string,
  args: string[] = []
): Promise<string> {
  return new Promise((resolve, reject) => {
    // Whitelist erlaubter Commands
    const ALLOWED_COMMANDS = ['git', 'npm', 'node'];

    if (!ALLOWED_COMMANDS.includes(command)) {
      reject(new Error(`Command not allowed: ${command}`));
      return;
    }

    // Spawn ohne Shell
    const proc = spawn(command, args, {
      shell: false, // KRITISCH: Niemals true!
      stdio: 'pipe'
    });

    let output = '';
    proc.stdout.on('data', (data) => output += data);
    proc.on('close', (code) => {
      if (code === 0) resolve(output);
      else reject(new Error(`Command failed with code ${code}`));
    });
  });
}

// Beispiel-Nutzung:
// await safeExecute('git', ['status']); // OK
// await safeExecute('rm', ['-rf', '/']); // BLOCKED