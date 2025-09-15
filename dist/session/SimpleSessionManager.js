"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SimpleSessionManager = void 0;
const fs_1 = require("fs");
const path_1 = require("path");
class SimpleSessionManager {
    constructor() {
        this.sessionDir = './local-only/SESSION';
        if (!(0, fs_1.existsSync)(this.sessionDir)) {
            (0, fs_1.mkdirSync)(this.sessionDir, { recursive: true });
        }
    }
    saveSession(name, data) {
        const timestamp = new Date().toISOString().split('T')[0];
        const filename = `${timestamp}_${name}.json`;
        const filepath = (0, path_1.join)(this.sessionDir, filename);
        (0, fs_1.writeFileSync)(filepath, JSON.stringify(data, null, 2));
        console.log(`Session saved: ${filename}`);
    }
    loadSession(filename) {
        const filepath = (0, path_1.join)(this.sessionDir, filename);
        if (!(0, fs_1.existsSync)(filepath)) {
            throw new Error(`Session not found: ${filename}`);
        }
        const data = (0, fs_1.readFileSync)(filepath, 'utf-8');
        return JSON.parse(data);
    }
    listSessions() {
        const fs = require('fs');
        return fs.readdirSync(this.sessionDir)
            .filter((f) => f.endsWith('.json'))
            .sort()
            .reverse();
    }
}
exports.SimpleSessionManager = SimpleSessionManager;
//# sourceMappingURL=SimpleSessionManager.js.map