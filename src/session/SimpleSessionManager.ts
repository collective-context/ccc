import { writeFileSync, readFileSync, existsSync, mkdirSync, readdirSync } from 'fs';
import { join } from 'path';

/**
 * Simple JSON-based session manager for CCC
 * @class SimpleSessionManager
 * @description Manages sessions as JSON files in local-only/SESSION directory
 */
export class SimpleSessionManager {
  private sessionDir = './local-only/SESSION';

  /**
   * Initialize session manager and create directory if needed
   */
  constructor() {
    if (!existsSync(this.sessionDir)) {
      mkdirSync(this.sessionDir, { recursive: true });
    }
  }

  /**
   * Save a session with automatic timestamping
   * @param {string} name - Session identifier
   * @param {any} data - Session data to persist
   * @throws {Error} If write fails
   * @example
   * manager.saveSession('project-x', { status: 'active' });
   */
  saveSession(name: string, data: any): void {
    const timestamp = new Date().toISOString().split('T')[0];
    const filename = `${timestamp}_${name}.json`;
    const filepath = join(this.sessionDir, filename);

    writeFileSync(filepath, JSON.stringify(data, null, 2));
    console.log(`Session saved: ${filename}`);
  }

  /**
   * Load a previously saved session
   * @param {string} filename - Session filename to load
   * @returns {any} Parsed session data
   * @throws {Error} If session not found or invalid JSON
   */
  loadSession(filename: string): any {
    const filepath = join(this.sessionDir, filename);
    if (!existsSync(filepath)) {
      throw new Error(`Session not found: ${filename}`);
    }

    const data = readFileSync(filepath, 'utf-8');
    return JSON.parse(data);
  }

  /**
   * List all available sessions
   * @returns {string[]} Array of session filenames, newest first
   */
  listSessions(): string[] {
    return readdirSync(this.sessionDir)
      .filter((f: string) => f.endsWith('.json'))
      .sort()
      .reverse();
  }
}