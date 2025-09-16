/**
 * Load and validate configuration from JSON file
 * @param {string} path - Path to JSON configuration file
 * @returns {object} Validated configuration object
 * @throws {Error} If file not found, invalid JSON, or validation fails
 * @example
 * const config = loadSafeConfig('./config-json/global/config.json');
 * console.log(config.prompts?.system);
 */
export declare function loadSafeConfig(path: string): {
    prompts?: {
        system?: string | undefined;
        user?: string | undefined;
    } | undefined;
    settings?: {
        temperature?: number | undefined;
        maxTokens?: number | undefined;
    } | undefined;
};
//# sourceMappingURL=safe-loader.d.ts.map