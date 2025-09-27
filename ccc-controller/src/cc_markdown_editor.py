#!/usr/bin/env python3
"""
CC Markdown Editor - WordOps Edition
Vereinfachte Version für schnellen Start
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
auth = HTTPBasicAuth()

# Konfiguration
DB_PATH = Path.home() / "prog/ai/git/collective-context/ccc/memory.db"
STATIC_PATH = Path.home() / "prog/ai/git/collective-context/ccc/static"
TEMPLATES_PATH = Path.home() / "prog/ai/git/collective-context/ccc/templates"

# Basic Auth (später durch echte Auth ersetzen)
users = {
    "admin": generate_password_hash(os.environ.get('CC_ADMIN_PASSWORD', 'changeme')),
    "editor": generate_password_hash(os.environ.get('CC_EDITOR_PASSWORD', 'editor123'))
}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username

# Hauptseite
@app.route('/')
@auth.login_required
def index():
    return render_template('editor.html')

# API Endpoints
@app.route('/api/records')
@auth.login_required
def get_records():
    """Alle aktiven Records laden"""
    # Use current_db instead of DB_PATH
    db_to_use = current_db if 'current_db' in globals() else DB_PATH

    conn = sqlite3.connect(str(db_to_use))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Check if it's the cc_knowledge.db with different structure
    if 'cc_knowledge.db' in str(db_to_use):
        cursor.execute("""
            SELECT content_id as id, content_type as memory_type,
                   'system' as agent_name, content_body as content,
                   is_visible as status, created_at, updated_at
            FROM contents
            WHERE is_visible = 1
            ORDER BY updated_at DESC
            LIMIT 200
        """)
    else:
        cursor.execute("""
            SELECT id, memory_type, agent_name, content, status, created_at, updated_at
            FROM memory
            WHERE status = 1
            ORDER BY updated_at DESC
            LIMIT 200
        """)

    records = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(records)

@app.route('/api/record/<int:record_id>')
@auth.login_required
def get_record(record_id):
    """Einzelnen Record laden"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM memory WHERE id = ?", (record_id,))
    record = cursor.fetchone()
    conn.close()

    if record:
        return jsonify(dict(record))
    return jsonify({'error': 'Record not found'}), 404

@app.route('/api/record/<int:record_id>', methods=['PUT'])
@auth.login_required
def update_record(record_id):
    """Record aktualisieren"""
    data = request.json
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Backup erstellen (in dieselbe Tabelle mit status=99)
    cursor.execute("""
        INSERT INTO memory (memory_type, agent_name, content, metadata, status, created_at)
        SELECT memory_type, agent_name, content, metadata, 99, datetime('now')
        FROM memory WHERE id = ?
    """, (record_id,))

    # Update durchführen
    cursor.execute("""
        UPDATE memory
        SET content = ?,
            updated_at = datetime('now'),
            metadata = json_set(
                COALESCE(metadata, '{}'),
                '$.updated_by', ?,
                '$.update_count', COALESCE(json_extract(metadata, '$.update_count'), 0) + 1
            )
        WHERE id = ?
    """, (data['content'], auth.current_user(), record_id))

    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()

    if rows_affected:
        return jsonify({'success': True, 'message': 'Record updated'})
    return jsonify({'error': 'Update failed'}), 400

@app.route('/api/record/<int:record_id>', methods=['DELETE'])
@auth.login_required
def delete_record(record_id):
    """Soft-Delete (Status 22)"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE memory
        SET status = 22,
            updated_at = datetime('now'),
            metadata = json_set(
                COALESCE(metadata, '{}'),
                '$.deleted_by', ?,
                '$.deleted_at', datetime('now')
            )
        WHERE id = ?
    """, (auth.current_user(), record_id))

    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()

    if rows_affected:
        return jsonify({'success': True, 'message': 'Record marked as deleted'})
    return jsonify({'error': 'Delete failed'}), 400

@app.route('/api/stats')
@auth.login_required
def get_stats():
    """Datenbank-Statistiken"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    stats = {}

    # Anzahl Records
    cursor.execute("SELECT COUNT(*) FROM memory WHERE status = 1")
    stats['active_records'] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM memory WHERE status = 22")
    stats['deleted_records'] = cursor.fetchone()[0]

    # DB-Größe
    cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
    stats['db_size'] = cursor.fetchone()[0]

    conn.close()
    return jsonify(stats)

@app.route('/api/logout', methods=['POST'])
def logout():
    """
    Logout Endpoint - Erzwingt Re-Authentication
    Bei Basic Auth gibt es kein echtes Logout,
    daher senden wir 401 um neue Anmeldung zu erzwingen
    """
    return jsonify({'message': 'Logged out'}), 401

# Optional: Session-Clear für zukünftige Session-basierte Auth
from flask import session
import subprocess
import sys

# Store current database path
current_db = DB_PATH

@app.route('/api/logout-session', methods=['POST'])
@auth.login_required
def logout_session():
    """Für zukünftige Session-basierte Authentifizierung"""
    session.clear()
    return jsonify({'message': 'Session cleared', 'redirect': '/'})

@app.route('/api/switch-database', methods=['POST'])
@auth.login_required
def switch_database():
    """Switch to a different database"""
    global current_db
    data = request.json
    db_name = data.get('database', 'memory.db')

    # Build the new database path
    new_db_path = Path.home() / "prog/ai/git/collective-context/ccc"

    if db_name == 'cc_knowledge.db':
        new_db_path = new_db_path / "database" / db_name
    else:
        new_db_path = new_db_path / db_name

    if new_db_path.exists():
        current_db = new_db_path
        return jsonify({'success': True, 'message': f'Switched to {db_name}'})
    else:
        return jsonify({'success': False, 'error': f'Database {db_name} not found'}), 404

@app.route('/api/import-website', methods=['POST'])
@auth.login_required
def import_website():
    """Import website content to selected database"""
    data = request.json
    db_name = data.get('database', 'cc_knowledge.db')

    if db_name != 'cc_knowledge.db':
        return jsonify({'success': False, 'error': 'Website import only works with cc_knowledge.db'}), 400

    try:
        # Run the import script
        script_path = Path.home() / "prog/ai/git/collective-context/ccc/database/import_website_to_db.py"
        result = subprocess.run([sys.executable, str(script_path)],
                              capture_output=True, text=True, cwd=script_path.parent)

        if result.returncode == 0:
            return jsonify({'success': True, 'message': 'Website imported successfully'})
        else:
            return jsonify({'success': False, 'error': result.stderr}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/export-starlight', methods=['POST'])
@auth.login_required
def export_starlight():
    """Export database to Starlight format"""
    data = request.json
    db_name = data.get('database', 'cc_knowledge.db')

    if db_name != 'cc_knowledge.db':
        return jsonify({'success': False, 'error': 'Export only works with cc_knowledge.db'}), 400

    try:
        # Run the export script
        script_path = Path.home() / "prog/ai/git/collective-context/ccc/database/export_to_starlight.py"
        result = subprocess.run([sys.executable, str(script_path)],
                              capture_output=True, text=True, cwd=script_path.parent)

        if result.returncode == 0:
            export_path = Path.home() / "prog/ai/git/collective-context/collective-context.github.io/src/content/docs/bibliothek"
            return jsonify({'success': True, 'message': 'Export successful', 'path': str(export_path)})
        else:
            return jsonify({'success': False, 'error': result.stderr}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/git-push', methods=['POST'])
@auth.login_required
def git_push():
    """Push changes to GitHub"""
    try:
        # Change to the website directory
        website_path = Path.home() / "prog/ai/git/collective-context/collective-context.github.io"

        # Git add all changes
        result_add = subprocess.run(['git', 'add', '-A'],
                                   capture_output=True, text=True, cwd=website_path)

        if result_add.returncode != 0:
            return jsonify({'success': False, 'error': f'git add failed: {result_add.stderr}'}), 500

        # Git commit
        commit_message = f"Update from CC Controller - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        result_commit = subprocess.run(['git', 'commit', '-m', commit_message],
                                      capture_output=True, text=True, cwd=website_path)

        # Check if there were changes to commit
        if result_commit.returncode != 0:
            if 'nothing to commit' in result_commit.stdout:
                return jsonify({'success': True, 'message': 'No changes to commit'})
            else:
                return jsonify({'success': False, 'error': f'git commit failed: {result_commit.stderr}'}), 500

        # Git push
        result_push = subprocess.run(['git', 'push'],
                                    capture_output=True, text=True, cwd=website_path)

        if result_push.returncode == 0:
            return jsonify({'success': True, 'message': 'Successfully pushed to GitHub',
                          'output': result_push.stdout})
        else:
            return jsonify({'success': False, 'error': f'git push failed: {result_push.stderr}'}), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Development
    app.run(host='127.0.0.1', port=5001, debug=True)