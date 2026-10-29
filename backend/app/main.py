"""RythuMitra AI — FastAPI backend (phase 1: no paid AI dependencies)."""
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from uuid import uuid4
import os

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from typing import Literal
from starlette.concurrency import run_in_threadpool

from .database import DATABASE_PROVIDER, check_database, get_connection, migrate_sqlite_history
from .services import FarmingAgentService, GeminiService, GnaniSTTService, GnaniTTSService, ProviderError

ADVISOR = FarmingAgentService()
STT_SERVICE = GnaniSTTService()
TTS_SERVICE = GnaniTTSService()
MAX_AUDIO_BYTES = 15 * 1024 * 1024
LanguageCode = Literal['te-IN', 'en-IN', 'hi-IN', 'kn-IN', 'ta-IN', 'ml-IN', 'mr-IN', 'bn-IN', 'gu-IN', 'pa-IN']


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def initialize_db() -> None:
    with get_connection() as db:
        db.execute(text('''CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            language_code TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )'''))
        db.execute(text('''CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            conversation_id TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('user','assistant')),
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
        )'''))


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        initialize_db()
        migrate_sqlite_history()
    except SQLAlchemyError:
        app.state.database_startup_failed = True
    yield


app = FastAPI(title='RythuMitra AI API', description='Backend for the multilingual voice-first farming assistant.', version='0.2.0', lifespan=lifespan)
allowed_origins = [x.strip() for x in os.getenv('ALLOWED_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(',') if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=allowed_origins, allow_methods=['GET', 'POST', 'DELETE'], allow_headers=['Content-Type'])


@app.exception_handler(SQLAlchemyError)
async def database_error_handler(_request, _exc):
    return JSONResponse(
        status_code=503,
        content={'detail': 'Database unavailable. Check that PostgreSQL is running and DATABASE_URL is correct.'},
    )


class CreateConversation(BaseModel):
    language_code: LanguageCode = 'te-IN'


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2500)
    language_code: LanguageCode = 'te-IN'
    conversation_id: str = Field(min_length=1, max_length=100)


class SynthesisRequest(BaseModel):
    text: str = Field(min_length=1, max_length=3000)
    language_code: LanguageCode = 'te-IN'


def conversation_or_404(db, id: str):
    result = db.execute(text('SELECT * FROM conversations WHERE id = :id'), {'id': id}).mappings().first()
    if result is None:
        raise HTTPException(404, detail='Conversation not found')
    return result


@app.get('/api/health')
def health():
    gemini_configured = ADVISOR.gemini.configured
    stt_configured = STT_SERVICE.configured
    tts_configured = TTS_SERVICE.configured
    try:
        check_database()
        database_status = 'ok'
    except SQLAlchemyError:
        raise HTTPException(503, detail='Database unavailable. Check that PostgreSQL is running and DATABASE_URL is correct.') from None
    return {
        'status': 'ok', 'mode': 'gemini' if gemini_configured else 'demo',
        'database': DATABASE_PROVIDER, 'database_status': database_status,
        'reasoning_provider': 'gemini' if gemini_configured else 'deterministic_examples',
        'stt_provider': 'gnani_prisma' if stt_configured else 'not_connected',
        'tts_provider': 'gnani_timbre' if tts_configured else 'not_connected',
        'message': 'All provider keys are configured.' if gemini_configured and stt_configured and tts_configured else 'One or more provider keys are not configured; unavailable providers will report setup instructions.'
    }


@app.get('/api/conversations')
def list_conversations():
    with get_connection() as db:
        items = db.execute(text('SELECT * FROM conversations ORDER BY updated_at DESC')).mappings().all()
        return [dict(item) for item in items]


@app.post('/api/conversations', status_code=201)
def create_conversation(payload: CreateConversation):
    now = now_iso()
    item = dict(id=str(uuid4()), title='New conversation', language_code=payload.language_code, created_at=now, updated_at=now)
    with get_connection() as db:
        db.execute(text('INSERT INTO conversations (id, title, language_code, created_at, updated_at) VALUES (:id, :title, :language_code, :created_at, :updated_at)'), item)
    return item


@app.get('/api/conversations/{conversation_id}')
def get_conversation(conversation_id: str):
    with get_connection() as db:
        result = db.execute(text('SELECT * FROM conversations WHERE id = :id'), {'id': conversation_id}).mappings().first()
        if result is None:
            raise HTTPException(404, detail='Conversation not found')
        conv = dict(result)
        conv['messages'] = [dict(row) for row in db.execute(
            text('SELECT * FROM messages WHERE conversation_id = :id ORDER BY created_at ASC, id ASC'),
            {'id': conversation_id},
        ).mappings().all()]
        return conv


@app.delete('/api/conversations/{conversation_id}')
def delete_conversation(conversation_id: str):
    with get_connection() as db:
        conversation_or_404(db, conversation_id)
        db.execute(text('DELETE FROM conversations WHERE id = :id'), {'id': conversation_id})
    return {'deleted': True, 'conversation_id': conversation_id}


@app.post('/api/chat')
def chat(payload: ChatRequest):
    question = payload.message.strip()
    if not question:
        raise HTTPException(422, detail='Please provide a question.')
    with get_connection() as db:
        conv = conversation_or_404(db, payload.conversation_id)
        history = [dict(row) for row in db.execute(
            text('SELECT role, content FROM messages WHERE conversation_id = :id ORDER BY created_at ASC, id ASC'),
            {'id': payload.conversation_id},
        ).mappings().all()]
        try:
            answer, mode = ADVISOR.respond(question, payload.language_code, history)
        except ProviderError as exc:
            raise HTTPException(exc.status_code, detail=exc.detail) from None
        count = db.execute(
            text('SELECT COUNT(*) AS count FROM messages WHERE conversation_id = :id'),
            {'id': payload.conversation_id},
        ).mappings().one()['count']
        now = now_iso()
        user_msg = {'id': str(uuid4()), 'conversation_id': payload.conversation_id, 'role': 'user', 'content': question, 'created_at': now}
        content = answer.text
        if answer.sources:
            content += '\n\nSources:\n' + '\n'.join(f"- {source['title']}: {source['url']}" for source in answer.sources)
        ai_msg = {'id': str(uuid4()), 'conversation_id': payload.conversation_id, 'role': 'assistant', 'content': content, 'created_at': now_iso()}
        for msg in (user_msg, ai_msg):
            db.execute(text('INSERT INTO messages (id, conversation_id, role, content, created_at) VALUES (:id, :conversation_id, :role, :content, :created_at)'), msg)
        title = question[:43] + ('…' if len(question) > 43 else '') if count == 0 else conv['title']
        db.execute(text('UPDATE conversations SET title = :title, updated_at = :updated_at, language_code = :language_code WHERE id = :id'), {
            'title': title, 'updated_at': now_iso(), 'language_code': payload.language_code, 'id': payload.conversation_id,
        })
        return {'conversation_id': payload.conversation_id, 'user_message': user_msg, 'assistant_message': ai_msg,
            'topic': answer.topic, 'crop': answer.crop, 'suggested_questions': answer.suggestions,
            'sources': answer.sources, 'mode': mode,
            'notice': 'This is a rule-based demo response; configure GEMINI_API_KEY for grounded reasoning.' if mode == 'demo_rule_based' else None}


@app.post('/api/voice/transcribe')
async def transcribe_voice(audio_file: UploadFile = File(...), language_code: LanguageCode = Form(...)):
    if audio_file.size is not None and audio_file.size > MAX_AUDIO_BYTES:
        raise HTTPException(413, detail='Audio upload exceeds the 15 MB limit.')
    audio = await audio_file.read(MAX_AUDIO_BYTES + 1)
    if len(audio) > MAX_AUDIO_BYTES:
        raise HTTPException(413, detail='Audio upload exceeds the 15 MB limit.')
    try:
        transcript = await run_in_threadpool(STT_SERVICE.transcribe, audio, audio_file.filename or 'recording.webm', language_code)
    except ProviderError as exc:
        raise HTTPException(exc.status_code, detail=exc.detail) from None
    return {'transcript': transcript, 'language_code': language_code}


@app.post('/api/voice/synthesize')
def synthesize_voice(payload: SynthesisRequest):
    text = payload.text.strip()
    if not text:
        raise HTTPException(422, detail='Please provide text to synthesize.')
    try:
        audio = TTS_SERVICE.synthesize(text, payload.language_code)
    except ProviderError as exc:
        raise HTTPException(exc.status_code, detail=exc.detail) from None
    return Response(content=audio, media_type='audio/wav', headers={'Cache-Control': 'no-store'})
