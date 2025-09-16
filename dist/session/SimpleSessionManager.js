"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SimpleSessionManager = void 0;
const fs_1 = require("fs");
const path_1 = require("path");
/**
 * Simple JSON-based session manager for CCC
 * @class SimpleSessionManager
 * @description Manages sessions as JSON files in local-only/SESSION directory
 */
class SimpleSessionManager {
    /**
     * Initialize session manager and create directory if needed
     */
    constructor() {
        this.sessionDir = './local-only/SESSION';
        if (!(0, fs_1.existsSync)(this.sessionDir)) {
            (0, fs_1.mkdirSync)(this.sessionDir, { recursive: true });
        }
    }
    /**
     * Save a session with automatic timestamping
     * @param {string} name - Session identifier
     * @param {any} data - Session data to persist
     * @throws {Error} If write fails
     * @example
     * manager.saveSession('project-x', { status: 'active' });
     */
    saveSession(name, data) {
        const timestamp = new Date().toISOString().split('T')[0];
        const filename = `${timestamp}_${name}.json`;
        const filepath = (0, path_1.join)(this.sessionDir, filename);
        (0, fs_1.writeFileSync)(filepath, JSON.stringify(data, null, 2));
        console.log(`Session saved: ${filename}`);
    }
    /**
     * Load a previously saved session
     * @param {string} filename - Session filename to load
     * @returns {any} Parsed session data
     * @throws {Error} If session not found or invalid JSON
     */
    loadSession(filename) {
        const filepath = (0, path_1.join)(this.sessionDir, filename);
        if (!(0, fs_1.existsSync)(filepath)) {
            throw new Error(`Session not found: ${filename}`);
        }
        const data = (0, fs_1.readFileSync)(filepath, 'utf-8');
        return JSON.parse(data);
    }
    /**
     * List all available sessions
     * @returns {string[]} Array of session filenames, newest first
     */
    listSessions() {
        return (0, fs_1.readdirSync)(this.sessionDir)
            .filter((f) => f.endsWith('.json'))
            .sort()
            .reverse();
    }
}
exports.SimpleSessionManager = SimpleSessionManager;
//# sourceMappingURL=SimpleSessionManager.js.map