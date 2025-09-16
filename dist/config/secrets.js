"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.loadSecrets = loadSecrets;
const zod_1 = require("zod");
const EnvSchema = zod_1.z.object({
    ANTHROPIC_API_KEY: zod_1.z.string().optional(),
    OPENROUTER_API_KEY: zod_1.z.string().optional(),
    // Keine Secrets in Code!
});
function loadSecrets() {
    try {
        return EnvSchema.parse(process.env);
    }
    catch {
        console.warn('Some API keys are missing');
        return {};
    }
}
//# sourceMappingURL=secrets.js.map