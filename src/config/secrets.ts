import { z } from 'zod';

const EnvSchema = z.object({
  ANTHROPIC_API_KEY: z.string().optional(),
  OPENROUTER_API_KEY: z.string().optional(),
  // Keine Secrets in Code!
});

export function loadSecrets() {
  try {
    return EnvSchema.parse(process.env);
  } catch {
    console.warn('Some API keys are missing');
    return {};
  }
}