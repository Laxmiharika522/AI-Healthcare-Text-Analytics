"""
Database utility functions for AI Healthcare Text Analytics Platform.
Supports BOTH MySQL (via PyMySQL) and SQLite as fallback.
Configure MySQL in backend/.env file.
"""
import os

# Load .env file
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
except ImportError:
    pass

# ─── MySQL Config (from .env) ────────────────────────────────────────────────
DB_HOST     = os.getenv('DB_HOST', 'localhost')
DB_PORT     = int(os.getenv('DB_PORT', 3306))
DB_USER     = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME     = os.getenv('DB_NAME', 'healthcare_nlp')

# SQLite fallback path (used if MySQL is unavailable)
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'healthcare.db')

_USE_MYSQL = None   # lazily determined on first connect


def _detect_backend():
    """Try MySQL first, fall back to SQLite."""
    global _USE_MYSQL
    if _USE_MYSQL is not None:
        return _USE_MYSQL
    try:
        import pymysql
        conn = pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USER,
                               password=DB_PASSWORD, database=DB_NAME,
                               connect_timeout=3)
        conn.close()
        _USE_MYSQL = True
        print(f"[DB] Connected to MySQL: {DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    except Exception as e:
        _USE_MYSQL = False
        print(f"[DB] MySQL unavailable ({e}). Using SQLite fallback.")
    return _USE_MYSQL


def get_db():
    """Return a live database connection (MySQL or SQLite)."""
    if _detect_backend():
        import pymysql
        conn = pymysql.connect(
            host=DB_HOST, port=DB_PORT,
            user=DB_USER, password=DB_PASSWORD,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False
        )
        return conn
    else:
        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn


def query_db(query, args=(), one=False):
    """Run a SELECT and return list-of-dicts (or single dict if one=True)."""
    conn = get_db()
    try:
        if _USE_MYSQL:
            # MySQL: %s placeholders, DictCursor
            query = query.replace('?', '%s')
            with conn.cursor() as cur:
                cur.execute(query, args)
                rv = cur.fetchall()           # already list of dicts
        else:
            cur = conn.execute(query, args)
            rv = [dict(row) for row in cur.fetchall()]
        return (rv[0] if rv else None) if one else rv
    finally:
        conn.close()


def execute_db(query, args=()):
    """Run an INSERT/UPDATE/DELETE and return lastrowid."""
    conn = get_db()
    try:
        if _USE_MYSQL:
            query = query.replace('?', '%s')
            with conn.cursor() as cur:
                cur.execute(query, args)
                last_id = cur.lastrowid
            conn.commit()
        else:
            cur = conn.execute(query, args)
            conn.commit()
            last_id = cur.lastrowid
        return last_id
    finally:
        conn.close()


def rows_to_dict(rows):
    """Ensure rows are plain dicts (works for both backends)."""
    if not rows:
        return []
    if isinstance(rows[0], dict):
        return list(rows)
    return [dict(row) for row in rows]

