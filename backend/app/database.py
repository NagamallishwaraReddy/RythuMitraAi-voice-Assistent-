"""SQLAlchemy database configuration for PostgreSQL and local SQLite fallback."""
from __future__ import annotations

from contextlib import contextmanager
import os
from pathlib import Path
import sqlite3
from typing import Iterator

from dotenv import load_dotenv
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Connection, Engine

BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / '.env')


def _database_url() -> str:
    configured = os.getenv('DATABASE_URL', '').strip()
    if 'replace_with_local_password' in configured or 'replace_me' in configured.lower() or 'changeme' in configured.lower():
        configured = ''
    if configured.startswith('postgres://'):
        return 'postgresql+psycopg://' + configured.removeprefix('postgres://')
    if configured.startswith('postgresql://'):
        return 'postgresql+psycopg://' + configured.removeprefix('postgresql://')
    if configured:
        return configured
    db_path = Path(os.getenv('RYTHUMITRA_DB_PATH', str(BACKEND_DIR / 'data' / 'rythumitra.sqlite3')))
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return f'sqlite:///{db_path}'


DATABASE_URL = _database_url()
IS_SQLITE = DATABASE_URL.startswith('sqlite:')
DATABASE_PROVIDER = 'sqlite' if IS_SQLITE else 'postgresql'
ENGINE: Engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={'check_same_thread': False} if IS_SQLITE else {},
)


if IS_SQLITE:
    @event.listens_for(ENGINE, 'connect')
    def _enable_sqlite_foreign_keys(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute('PRAGMA foreign_keys = ON')
        cursor.close()


@contextmanager
def get_connection() -> Iterator[Connection]:
    with ENGINE.begin() as connection:
        yield connection


def check_database() -> None:
    with ENGINE.connect() as connection:
        connection.execute(text('SELECT 1'))


def migrate_sqlite_history(source_path: Path | None = None) -> int:
    """Copy local SQLite history to an empty configured PostgreSQL database when explicitly enabled."""
    if IS_SQLITE or os.getenv('MIGRATE_SQLITE_HISTORY', '').strip().lower() not in {'1', 'true', 'yes'}:
        return 0
    source = source_path or BACKEND_DIR / 'data' / 'rythumitra.sqlite3'
    if not source.is_file():
        return 0

    with get_connection() as target:
        existing = target.execute(text('SELECT COUNT(*) FROM conversations')).scalar_one()
        if existing:
            return 0

        source_db = sqlite3.connect(f'file:{source}?mode=ro', uri=True)
        source_db.row_factory = sqlite3.Row
        try:
            conversations = [dict(row) for row in source_db.execute('SELECT * FROM conversations')]
            messages = [dict(row) for row in source_db.execute('SELECT * FROM messages ORDER BY rowid ASC')]
        finally:
            source_db.close()

        if conversations:
            target.execute(text('''INSERT INTO conversations (id, title, language_code, created_at, updated_at)
                VALUES (:id, :title, :language_code, :created_at, :updated_at)'''), conversations)
        if messages:
            target.execute(text('''INSERT INTO messages (id, conversation_id, role, content, created_at)
                VALUES (:id, :conversation_id, :role, :content, :created_at)'''), messages)
    return len(conversations)