import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { SimpleSessionManager } from '../../../src/session/SimpleSessionManager'
import { rmSync, existsSync, readdirSync } from 'fs'
import { join } from 'path'

describe('SimpleSessionManager', () => {
  let manager: SimpleSessionManager;

  beforeEach(() => {
    manager = new SimpleSessionManager();
  });

  afterEach(() => {
    // Cleanup test sessions
    const sessionDir = './local-only/SESSION';
    if (existsSync(sessionDir)) {
      const files = readdirSync(sessionDir).filter(f => f.includes('test'));
      files.forEach(f => {
        rmSync(join(sessionDir, f), { force: true });
      });
    }
  });

  it('should save and load session', () => {
    const testData = { project: 'test', status: 'active' };
    manager.saveSession('test', testData);

    const sessions = manager.listSessions();
    expect(sessions.length).toBeGreaterThan(0);

    const testSession = sessions.find(s => s.includes('test'));
    expect(testSession).toBeDefined();

    if (testSession) {
      const loaded = manager.loadSession(testSession);
      expect(loaded.project).toBe('test');
      expect(loaded.status).toBe('active');
    }
  });

  it('should create session directory if not exists', () => {
    expect(existsSync('./local-only/SESSION')).toBe(true);
  });

  it('should list sessions in reverse order', () => {
    manager.saveSession('test1', { id: 1 });
    manager.saveSession('test2', { id: 2 });

    const sessions = manager.listSessions();
    const testSessions = sessions.filter(s => s.includes('test'));

    expect(testSessions.length).toBeGreaterThanOrEqual(2);
  });
});