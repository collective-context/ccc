"""
CCC Session Manager - Clean Implementation for Step 2
Simple, SQLite-based session management for AI instances
Claude-2 Sandbox Migration - Step 2
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path


class CCCSessionManager:
    """Simple session management for AI instances"""
    
    def __init__(self, db_path=None):
        """Initialize session manager with SQLite database"""
        if db_path is None:
            # Use sandbox .local/db/ directory
            sandbox_root = Path(__file__).parent.parent.parent
            db_dir = sandbox_root / ".local" / "db"
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = db_dir / "sessions.db"
        
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with session tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ai_instance TEXT NOT NULL,
                    session_name TEXT,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    status TEXT DEFAULT 'active',
                    metadata TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS session_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    message TEXT,
                    data TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_ai_instance 
                ON sessions (ai_instance)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_session_logs_session_id 
                ON session_logs (session_id)
            """)
    
    def start_session(self, ai_instance, session_name=None):
        """Start a new session for an AI instance"""
        # Validate AI instance
        valid_instances = ['cl1', 'cl2', 'ai1', 'ai2']
        if ai_instance not in valid_instances:
            raise ValueError(f"Invalid AI instance: {ai_instance}. Valid: {valid_instances}")
        
        # End any active sessions for this AI instance
        self._end_active_sessions(ai_instance)
        
        # Create new session
        now = datetime.now().isoformat()
        metadata = {
            "sandbox": "ccc-new",
            "version": "0.3.4",
            "step": "2-session-management"
        }
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO sessions (ai_instance, session_name, start_time, status, metadata, created_at)
                VALUES (?, ?, ?, 'active', ?, ?)
            """, (ai_instance, session_name, now, json.dumps(metadata), now))
            
            session_id = cursor.lastrowid
            
            # Log session start
            conn.execute("""
                INSERT INTO session_logs (session_id, timestamp, event_type, message)
                VALUES (?, ?, 'session_start', ?)
            """, (session_id, now, f"Session started for {ai_instance}"))
        
        return session_id
    
    def save_session(self, ai_instance, message=None):
        """Save/log current session state"""
        session_id = self._get_active_session_id(ai_instance)
        if not session_id:
            raise ValueError(f"No active session for {ai_instance}")
        
        now = datetime.now().isoformat()
        save_message = message or "Session state saved"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO session_logs (session_id, timestamp, event_type, message)
                VALUES (?, ?, 'session_save', ?)
            """, (session_id, now, save_message))
        
        return session_id
    
    def end_session(self, ai_instance):
        """End the active session for an AI instance"""
        session_id = self._get_active_session_id(ai_instance)
        if not session_id:
            raise ValueError(f"No active session for {ai_instance}")
        
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            # Update session end time and status
            conn.execute("""
                UPDATE sessions 
                SET end_time = ?, status = 'completed'
                WHERE id = ?
            """, (now, session_id))
            
            # Log session end
            conn.execute("""
                INSERT INTO session_logs (session_id, timestamp, event_type, message)
                VALUES (?, ?, 'session_end', ?)
            """, (session_id, now, f"Session ended for {ai_instance}"))
        
        return session_id
    
    def get_active_session(self, ai_instance):
        """Get the active session for an AI instance"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM sessions 
                WHERE ai_instance = ? AND status = 'active'
                ORDER BY start_time DESC
                LIMIT 1
            """, (ai_instance,))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def get_session_logs(self, session_id):
        """Get all logs for a session"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM session_logs 
                WHERE session_id = ?
                ORDER BY timestamp
            """, (session_id,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def list_sessions(self, ai_instance=None, limit=10):
        """List recent sessions"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            if ai_instance:
                cursor = conn.execute("""
                    SELECT * FROM sessions 
                    WHERE ai_instance = ?
                    ORDER BY start_time DESC
                    LIMIT ?
                """, (ai_instance, limit))
            else:
                cursor = conn.execute("""
                    SELECT * FROM sessions 
                    ORDER BY start_time DESC
                    LIMIT ?
                """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def _get_active_session_id(self, ai_instance):
        """Get the ID of the active session for an AI instance"""
        session = self.get_active_session(ai_instance)
        return session['id'] if session else None
    
    def _end_active_sessions(self, ai_instance):
        """End any active sessions for an AI instance"""
        session_id = self._get_active_session_id(ai_instance)
        if session_id:
            now = datetime.now().isoformat()
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE sessions 
                    SET end_time = ?, status = 'auto_ended'
                    WHERE id = ?
                """, (now, session_id))
    
    def get_database_info(self):
        """Get database statistics for debugging"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM sessions")
            session_count = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM session_logs")
            log_count = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM sessions WHERE status = 'active'")
            active_count = cursor.fetchone()[0]
            
            return {
                "database_path": str(self.db_path),
                "total_sessions": session_count,
                "total_logs": log_count,
                "active_sessions": active_count
            }