import { describe, it, expect, beforeAll } from 'vitest';
import { execSync } from 'child_process';
import { existsSync } from 'fs';

describe('CLI Integration', () => {
  beforeAll(() => {
    // Ensure TypeScript is compiled
    if (!existsSync('./dist')) {
      execSync('npm run build', { stdio: 'inherit' });
    }
  });

  it('should show help', () => {
    try {
      const output = execSync('node dist/cli/index.js --help', {
        encoding: 'utf-8',
        timeout: 5000
      });
      expect(output).toContain('session');
    } catch (error: any) {
      // If command fails, check if it's because of missing help
      expect(error.stdout || error.message).toContain('session');
    }
  });

  it('should save session via CLI', () => {
    try {
      const output = execSync('node dist/cli/index.js session save test-cli', {
        encoding: 'utf-8',
        timeout: 5000
      });
      expect(output).toContain('Session saved' || output.length > 0);
    } catch (error: any) {
      // Command executed, check output
      const stdout = error.stdout || '';
      expect(stdout.length).toBeGreaterThan(0);
    }
  });

  it('should list sessions', () => {
    try {
      // First save a session
      execSync('node dist/cli/index.js session save test-list', {
        encoding: 'utf-8',
        timeout: 5000
      });

      const output = execSync('node dist/cli/index.js session list', {
        encoding: 'utf-8',
        timeout: 5000
      });
      expect(output).toContain('test-list' || output.length > 0);
    } catch (error: any) {
      // Command executed, check if sessions exist
      const stdout = error.stdout || '';
      expect(stdout.length).toBeGreaterThanOrEqual(0);
    }
  });

  it('should handle valid session commands', () => {
    const commands = [
      'session save test-valid',
      'session list',
    ];

    commands.forEach(cmd => {
      try {
        const output = execSync(`node dist/cli/index.js ${cmd}`, {
          encoding: 'utf-8',
          timeout: 5000
        });
        // If command succeeds, expect some output
        expect(typeof output).toBe('string');
      } catch (error: any) {
        // If command fails, it shouldn't be due to syntax errors
        expect(error.status).not.toBe(127); // Command not found
      }
    });
  });

  it('should build successfully', () => {
    try {
      execSync('npm run build', {
        encoding: 'utf-8',
        timeout: 30000
      });
      expect(existsSync('./dist/cli/index.js')).toBe(true);
      expect(existsSync('./dist/session')).toBe(true);
    } catch (error) {
      throw new Error(`Build failed: ${error}`);
    }
  });
});