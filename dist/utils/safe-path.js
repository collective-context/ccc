"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.validatePath = validatePath;
exports.safeReadFile = safeReadFile;
const path = __importStar(require("path"));
const fs_1 = require("fs");
const PROJECT_ROOT = path.resolve(process.cwd());
function validatePath(userPath) {
    // Resolve to absolute path
    const resolved = path.resolve(PROJECT_ROOT, userPath);
    // Check if path is within project
    if (!resolved.startsWith(PROJECT_ROOT)) {
        throw new Error('Path traversal detected!');
    }
    // Check if path exists
    if (!(0, fs_1.existsSync)(resolved)) {
        throw new Error('Path does not exist');
    }
    return resolved;
}
// Nutze in allen File-Operationen:
function safeReadFile(filePath) {
    const safePath = validatePath(filePath);
    return (0, fs_1.readFileSync)(safePath, 'utf-8');
}
//# sourceMappingURL=safe-path.js.map