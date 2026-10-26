"""RythuMitra AI — FastAPI backend (phase 1: no paid AI dependencies)."""
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
import os
import sqlite3

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal

from .advisor import DemoAdvisor

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = Path(os.getenv('RYTHUMITRA_DB_PATH', str(BASE_DIR / 'data' / 'rythumitra.sqlite3')))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
ADVISOR = DemoAdvisor()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH, timeout=15)
    connection.row_factory = sqlite3.Row
    connection.execute('PRAGMA foreign_keys = ON')
    return connection


def initialize_db() -> None:
    with get_connection() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            language_code TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )''')
        db.execute('''CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            conversation_id TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('user','assistant')),
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
        )''')


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_db()
    yield


app = FastAPI(title='RythuMitra AI API', description='Backend for the voice-first farming assistant — demo mode.', version='0.1.0', lifespan=lifespan)
allowed_origins = [x.strip() for x in os.getenv('ALLOWED_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(',') if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=allowed_origins, allow_methods=['GET', 'POST', 'DELETE'], allow_headers=['Content-Type'])


class CreateConversation(BaseModel):
    language_code: str = Field('te-IN', min_length=2, max_length=12)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2500)
    language_code: str = Field('te-IN', min_length=2, max_length=12)
    conversation_id: str = Field(min_length=1, max_length=100)


class SynthesisRequest(BaseModel):
    text: str = Field(min_length=1, max_length=3000)
    language_code: str = 'te-IN'


def conversation_or_404(db: sqlite3.Connection, id: str) -> sqlite3.Row:
    result = db.execute('SELECT * FROM conversations WHERE id = ?', (id,)).fetchone()
    if result is None:
        raise HTTPException(404, detail='Conversation not found')
    return result


@app.get('/api/health')
def health():
    return {
        'status': 'ok', 'mode': 'demo',
        'reasoning_provider': 'deterministic_examples',
        'stt_provider': 'not_connected', 'tts_provider': 'not_connected',
        'message': 'API online; Gnani + LLM integrations come in phase 2.'
    }


@app.get('/api/conversations')
def list_conversations():
    with get_connection() as db:
        items = db.execute('SELECT * FROM conversations ORDER BY updated_at DESC').fetchall()
        return [dict(item) for item in items]


@app.post('/api/conversations', status_code=201)
def create_conversation(payload: CreateConversation):
    now = now_iso()
    item = dict(id=str(uuid4()), title='New conversation', language_code=payload.language_code, created_at=now, updated_at=now)
    with get_connection() as db:
        db.execute('INSERT INTO conversations (id, title, language_code, created_at, updated_at) VALUES (:id, :title, :language_code, :created_at, :updated_at)', item)
    return item


@app.get('/api/conversations/{conversation_id}')
def get_conversation(conversation_id: str):
    with get_connection() as db:
        conv = dict(conversation_or_404(db, conversation_id))
        conv['messages'] = [dict(r) for r in db.execute('SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at ASC, rowid ASC', (conversation_id,)).fetchall()]
        return conv


@app.delete('/api/conversations/{conversation_id}')
def delete_conversation(conversation_id: str):
    with get_connection() as db:
        conversation_or_404(db, conversation_id)
        db.execute('DELETE FROM conversations WHERE id = ?', (conversation_id,))
    return {'deleted': True, 'conversation_id': conversation_id}


@app.post('/api/chat')
def chat(payload: ChatRequest):
    text = payload.message.strip()
    if not text:
        raise HTTPException(422, detail='Please provide a question.')
    with get_connection() as db:
        conv = conversation_or_404(db, payload.conversation_id)
        previous_questions = [row['content'] for row in db.execute(
            "SELECT content FROM messages WHERE conversation_id = ? AND role = 'user' ORDER BY rowid ASC",
            (payload.conversation_id,)
        ).fetchall()]
        answer = ADVISOR.respond(text, payload.language_code, previous_questions)
        count = db.execute('SELECT COUNT(*) AS count FROM messages WHERE conversation_id = ?', (payload.conversation_id,)).fetchone()['count']
        now = now_iso()
        user_msg = {'id': str(uuid4()), 'conversation_id': payload.conversation_id, 'role': 'user', 'content': text, 'created_at': now}
        ai_msg = {'id': str(uuid4()), 'conversation_id': payload.conversation_id, 'role': 'assistant', 'content': answer.text, 'created_at': now_iso()}
        for msg in (user_msg, ai_msg):
            db.execute('INSERT INTO messages (id, conversation_id, role, content, created_at) VALUES (:id, :conversation_id, :role, :content, :created_at)', msg)
        title = text[:43] + ('…' if len(text) > 43 else '') if count == 0 else conv['title']
        db.execute('UPDATE conversations SET title = ?, updated_at = ?, language_code = ? WHERE id = ?', (title, now_iso(), payload.language_code, payload.conversation_id))
    return {'conversation_id': payload.conversation_id, 'user_message': user_msg, 'assistant_message': ai_msg,
            'topic': answer.topic, 'crop': answer.crop, 'suggested_questions': answer.suggestions, 'mode': 'demo_rule_based',
            'notice': 'This demo recognizes various crops and common question types, but open-ended, source-backed reasoning requires the future LLM integration.'}


@app.post('/api/voice/transcribe', status_code=501)
def transcribe_placeholder():
    raise HTTPException(501, detail='Gnani Prisma integration is intentionally not connected yet. Browser speech preview is available in supported browsers.')


@app.post('/api/voice/synthesize', status_code=501)
def synthesize_placeholder(payload: SynthesisRequest):
    raise HTTPException(501, detail='Gnani Timbre integration is intentionally not connected yet. Browser speech synthesis is used for local preview.')
