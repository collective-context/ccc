import { z } from 'zod';
import { readFileSync } from 'fs';

// Definiere sicheres Schema
const ConfigSchema = z.object({
  prompts: z.object({
    system: z.string().optional(),
    user: z.string().optional()
  }).optional(),
  settings: z.object({
    temperature: z.number().min(0).max(2).optional()
  }).optional(),
  // Keine executable code hooks!
});

export function loadSafeConfig(path: string) {
  try {
    const content = readFileSync(path, 'utf-8');
    const parsed = JSON.parse(content);
    return ConfigSchema.parse(parsed);
  } catch (error) {
    console.error(`Invalid config at ${path}:`, error);
    throw new Error('Configuration validation failed');
  }
}