/**
 * Configuration schema for CCC
 */
export interface CCCConfig {
    /** AI prompt templates */
    prompts?: {
        /** System prompt for AI behavior */
        system?: string;
        /** User prompt template */
        user?: string;
    };
    /** AI behavior settings */
    settings?: {
        /** Temperature for response randomness (0-2) */
        temperature?: number;
        /** Maximum tokens in response */
        maxTokens?: number;
    };
    /** Environment configuration */
    env?: {
        /** API keys (use environment variables instead!) */
        apiKeys?: never;
    };
}
/**
 * Session data structure
 */
export interface SessionData {
    /** Unique session identifier */
    id: string;
    /** ISO timestamp of creation */
    timestamp: string;
    /** Project name */
    project: string;
    /** Session status */
    status: 'active' | 'paused' | 'completed';
    /** List of agents involved in session */
    agents?: string[];
    /** Additional metadata */
    metadata?: {
        /** Node.js version */
        nodeVersion?: string;
        /** Operating system platform */
        platform?: string;
        /** Current working directory */
        cwd?: string;
        /** Additional custom metadata */
        [key: string]: any;
    };
}
/**
 * Command execution result
 */
export interface CommandResult {
    /** Exit code (0 = success) */
    exitCode: number;
    /** Standard output */
    stdout: string;
    /** Standard error */
    stderr: string;
    /** Execution time in milliseconds */
    duration: number;
}
/**
 * AI Agent configuration
 */
export interface AgentConfig {
    /** Agent identifier */
    id: string;
    /** Display name */
    name: string;
    /** AI model to use */
    model: string;
    /** Agent role/specialty */
    role: string;
    /** Custom prompts for this agent */
    prompts?: CCCConfig['prompts'];
    /** Agent-specific settings */
    settings?: CCCConfig['settings'];
}
//# sourceMappingURL=index.d.ts.map