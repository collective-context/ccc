import * as path from 'path';
import { existsSync, readFileSync } from 'fs';

const PROJECT_ROOT = path.resolve(process.cwd());

export function validatePath(userPath: string): string {
  // Resolve to absolute path
  const resolved = path.resolve(PROJECT_ROOT, userPath);

  // Check if path is within project
  if (!resolved.startsWith(PROJECT_ROOT)) {
    throw new Error('Path traversal detected!');
  }

  // Check if path exists
  if (!existsSync(resolved)) {
    throw new Error('Path does not exist');
  }

  return resolved;
}

// Nutze in allen File-Operationen:
export function safeReadFile(filePath: string) {
  const safePath = validatePath(filePath);
  return readFileSync(safePath, 'utf-8');
}