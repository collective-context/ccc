/**
 * Simple JSON-based session manager for CCC
 * @class SimpleSessionManager
 * @description Manages sessions as JSON files in local-only/SESSION directory
 */
export declare class SimpleSessionManager {
    private sessionDir;
    /**
     * Initialize session manager and create directory if needed
     */
    constructor();
    /**
     * Save a session with automatic timestamping
     * @param {string} name - Session identifier
     * @param {any} data - Session data to persist
     * @throws {Error} If write fails
     * @example
     * manager.saveSession('project-x', { status: 'active' });
     */
    saveSession(name: string, data: any): void;
    /**
     * Load a previously saved session
     * @param {string} filename - Session filename to load
     * @returns {any} Parsed session data
     * @throws {Error} If session not found or invalid JSON
     */
    loadSession(filename: string): any;
    /**
     * List all available sessions
     * @returns {string[]} Array of session filenames, newest first
     */
    listSessions(): string[];
}
//# sourceMappingURL=SimpleSessionManager.d.ts.map