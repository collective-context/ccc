import { z } from 'zod';
import { readFileSync } from 'fs';

/**
 * Secure configuration schema with strict validation
 * Prevents code execution by only allowing safe JSON data types
 */
const ConfigSchema = z.object({
  /** AI prompt templates */
  prompts: z.object({
    /** System prompt for AI behavior */
    system: z.string().optional(),
    /** User prompt template */
    user: z.string().optional()
  }).optional(),
  /** AI behavior settings */
  settings: z.object({
    /** Temperature for response randomness (0-2) */
    temperature: z.number().min(0).max(2).optional(),
    /** Maximum tokens in response */
    maxTokens: z.number().positive().optional()
  }).optional(),
  // Keine executable code hooks!
});

/**
 * Load and validate configuration from JSON file
 * @param {string} path - Path to JSON configuration file
 * @returns {object} Validated configuration object
 * @throws {Error} If file not found, invalid JSON, or validation fails
 * @example
 * const config = loadSafeConfig('./config-json/global/config.json');
 * console.log(config.prompts?.system);
 */
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