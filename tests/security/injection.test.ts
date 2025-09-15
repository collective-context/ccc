import { describe, it, expect } from 'vitest';
import { safeExecute } from '../../src/utils/safe-exec';
import { validatePath } from '../../src/utils/safe-path';

describe('Security: Command Injection Prevention', () => {
  it('should block dangerous commands', async () => {
    await expect(
      safeExecute('rm', ['-rf', '/'])
    ).rejects.toThrow('Command not allowed');
  });

  it('should allow safe git commands', async () => {
    const result = await safeExecute('git', ['--version']);
    expect(result).toContain('git version');
  });
});

describe('Security: Path Traversal Prevention', () => {
  it('should block path traversal attempts', () => {
    expect(() => validatePath('../../../etc/passwd'))
      .toThrow('Path traversal detected');

    expect(() => validatePath('/etc/passwd'))
      .toThrow('Path traversal detected');
  });

  it('should allow valid project paths', () => {
    const result = validatePath('./package.json');
    expect(result).toContain('package.json');
  });
});