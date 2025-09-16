"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.loadSafeConfig = loadSafeConfig;
const zod_1 = require("zod");
const fs_1 = require("fs");
/**
 * Secure configuration schema with strict validation
 * Prevents code execution by only allowing safe JSON data types
 */
const ConfigSchema = zod_1.z.object({
    /** AI prompt templates */
    prompts: zod_1.z.object({
        /** System prompt for AI behavior */
        system: zod_1.z.string().optional(),
        /** User prompt template */
        user: zod_1.z.string().optional()
    }).optional(),
    /** AI behavior settings */
    settings: zod_1.z.object({
        /** Temperature for response randomness (0-2) */
        temperature: zod_1.z.number().min(0).max(2).optional(),
        /** Maximum tokens in response */
        maxTokens: zod_1.z.number().positive().optional()
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
function loadSafeConfig(path) {
    try {
        const content = (0, fs_1.readFileSync)(path, 'utf-8');
        const parsed = JSON.parse(content);
        return ConfigSchema.parse(parsed);
    }
    catch (error) {
        console.error(`Invalid config at ${path}:`, error);
        throw new Error('Configuration validation failed');
    }
}
//# sourceMappingURL=safe-loader.js.map