import { writeFileSync, readFileSync, existsSync, mkdirSync } from 'fs';
import { join } from 'path';

export class SimpleSessionManager {
  private sessionDir = './local-only/SESSION';

  constructor() {
    if (!existsSync(this.sessionDir)) {
      mkdirSync(this.sessionDir, { recursive: true });
    }
  }

  saveSession(name: string, data: any): void {
    const timestamp = new Date().toISOString().split('T')[0];
    const filename = `${timestamp}_${name}.json`;
    const filepath = join(this.sessionDir, filename);

    writeFileSync(filepath, JSON.stringify(data, null, 2));
    console.log(`Session saved: ${filename}`);
  }

  loadSession(filename: string): any {
    const filepath = join(this.sessionDir, filename);
    if (!existsSync(filepath)) {
      throw new Error(`Session not found: ${filename}`);
    }

    const data = readFileSync(filepath, 'utf-8');
    return JSON.parse(data);
  }

  listSessions(): string[] {
    const fs = require('fs');
    return fs.readdirSync(this.sessionDir)
      .filter((f: string) => f.endsWith('.json'))
      .sort()
      .reverse();
  }
}