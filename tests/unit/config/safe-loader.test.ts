import { describe, it, expect, afterEach } from 'vitest';
import { loadSafeConfig } from '../../../src/config/safe-loader';
import { writeFileSync, rmSync } from 'fs';

describe('Safe Config Loader', () => {
  const testConfigPath = './test-config.json';

  afterEach(() => {
    rmSync(testConfigPath, { force: true });
  });

  it('should load valid JSON config', () => {
    const validConfig = {
      prompts: { system: 'Test prompt' },
      settings: { temperature: 0.7 }
    };

    writeFileSync(testConfigPath, JSON.stringify(validConfig));
    const loaded = loadSafeConfig(testConfigPath);

    expect(loaded.prompts?.system).toBe('Test prompt');
    expect(loaded.settings?.temperature).toBe(0.7);
  });

  it('should reject invalid temperature values', () => {
    const invalidConfig = {
      settings: { temperature: 3.0 } // Max is 2.0
    };

    writeFileSync(testConfigPath, JSON.stringify(invalidConfig));

    expect(() => loadSafeConfig(testConfigPath))
      .toThrow('Configuration validation failed');
  });

  it('should reject configs with unknown fields', () => {
    const unknownFieldConfig = '{"evil": "() => exec(rm -rf /)", "unknown": "value"}';

    writeFileSync(testConfigPath, unknownFieldConfig);
    const loaded = loadSafeConfig(testConfigPath);

    // Unknown fields should be stripped by Zod
    expect(loaded.evil).toBeUndefined();
    expect(loaded.unknown).toBeUndefined();
  });

  it('should handle missing optional fields', () => {
    const minimalConfig = {};

    writeFileSync(testConfigPath, JSON.stringify(minimalConfig));
    const loaded = loadSafeConfig(testConfigPath);

    expect(loaded).toBeDefined();
    expect(loaded.prompts).toBeUndefined();
  });

  it('should validate temperature range', () => {
    const configs = [
      { settings: { temperature: -1 } }, // Too low
      { settings: { temperature: 0 } },  // Valid
      { settings: { temperature: 1 } },  // Valid
      { settings: { temperature: 2 } },  // Valid
      { settings: { temperature: 2.1 } } // Too high
    ];

    configs.forEach((config, index) => {
      const path = `./test-config-${index}.json`;
      writeFileSync(path, JSON.stringify(config));

      if (index === 0 || index === 4) {
        expect(() => loadSafeConfig(path)).toThrow();
      } else {
        expect(() => loadSafeConfig(path)).not.toThrow();
      }

      rmSync(path, { force: true });
    });
  });

  it('should handle malformed JSON gracefully', () => {
    const malformedJson = '{ "invalid": json }';
    writeFileSync(testConfigPath, malformedJson);

    expect(() => loadSafeConfig(testConfigPath))
      .toThrow('Configuration validation failed');
  });

  it('should validate prompts structure', () => {
    const validPromptConfig = {
      prompts: {
        system: 'You are a helpful assistant',
        user: 'Please help with {{task}}'
      }
    };

    writeFileSync(testConfigPath, JSON.stringify(validPromptConfig));
    const loaded = loadSafeConfig(testConfigPath);

    expect(loaded.prompts?.system).toBe('You are a helpful assistant');
    expect(loaded.prompts?.user).toBe('Please help with {{task}}');
  });
});