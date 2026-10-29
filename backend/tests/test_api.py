"""Run with: pip install pytest httpx && pytest -q"""
from fastapi.testclient import TestClient
from app.main import app
from app import main as main_module
from app import database
from app.advisor import Advice
from sqlalchemy.exc import SQLAlchemyError


def test_health_and_farming_chat():
    with TestClient(app) as client:
        assert client.get('/api/health').json()['mode'] == 'demo'
        created = client.post('/api/conversations', json={'language_code': 'te-IN'})
        assert created.status_code == 201
        id = created.json()['id']
        answer = client.post('/api/chat', json={'conversation_id': id, 'language_code': 'te-IN', 'message': 'నా వరి ఆకులు పసుపుగా మారుతున్నాయి'})
        assert answer.status_code == 200
        assert answer.json()['topic'] == 'yellow'
        fetched = client.get(f'/api/conversations/{id}')
        assert len(fetched.json()['messages']) == 2
        assert client.delete(f'/api/conversations/{id}').status_code == 200
        assert client.get(f'/api/conversations/{id}').status_code == 404


def test_voice_endpoints_validate_requests_and_report_missing_keys():
    with TestClient(app) as client:
        assert client.post('/api/voice/transcribe').status_code == 422
        response = client.post('/api/voice/transcribe', data={'language_code': 'te-IN'}, files={'audio_file': ('sample.wav', b'audio', 'audio/wav')})
        assert response.status_code == 503
        assert 'GNANI_STT_KEY' in response.json()['detail']
        response = client.post('/api/voice/synthesize', json={'text': 'hello', 'language_code': 'te-IN'})
        assert response.status_code == 503
        assert 'GNANI_TTS_KEY' in response.json()['detail']


def test_multi_crop_demo_and_conversation_context():
    with TestClient(app) as client:
        conv = client.post('/api/conversations', json={'language_code': 'en-IN'}).json()['id']
        cotton = client.post('/api/chat', json={
            'conversation_id': conv, 'language_code': 'en-IN',
            'message': 'There are insects on my cotton leaves. What should I check?'
        }).json()
        assert cotton['crop'] == 'cotton'
        assert cotton['topic'] == 'pest'
        assert 'cotton' in cotton['assistant_message']['content']
        followup = client.post('/api/chat', json={
            'conversation_id': conv, 'language_code': 'en-IN',
            'message': 'How should I water it?'
        }).json()
        assert followup['crop'] == 'cotton'
        assert followup['topic'] == 'water'
        tomatoes = client.post('/api/chat', json={
            'conversation_id': conv, 'language_code': 'en-IN',
            'message': 'I want to start growing tomatoes.'
        }).json()
        assert tomatoes['crop'] == 'tomato'
        assert tomatoes['topic'] == 'planting'
        banana = client.post('/api/chat', json={
            'conversation_id': conv, 'language_code': 'en-IN',
            'message': 'What fertilizer should I use for banana?'
        }).json()
        assert banana['crop'] == 'banana'
        assert banana['topic'] == 'fertilizer'
        cotton_climate = client.post('/api/chat', json={
            'conversation_id': conv, 'language_code': 'en-IN',
            'message': 'What climate and temperature is needed for cotton?'
        }).json()
        assert cotton_climate['crop'] == 'cotton'
        assert cotton_climate['topic'] == 'climate'
        assert 'temperature' in cotton_climate['assistant_message']['content'].lower()
        client.delete(f'/api/conversations/{conv}')


def test_unknown_crop_does_not_invent_details():
    with TestClient(app) as client:
        conv = client.post('/api/conversations', json={'language_code': 'en-IN'}).json()['id']
        dragonfruit = client.post('/api/chat', json={
            'conversation_id': conv, 'language_code': 'en-IN',
            'message': 'I want to grow dragon fruit.'
        }).json()
        assert dragonfruit['crop'] == 'dragon fruit'
        assert 'source' not in dragonfruit['assistant_message']['content'].lower() or dragonfruit['mode'] == 'demo_rule_based'
        unknown = client.post('/api/chat', json={
            'conversation_id': client.post('/api/conversations', json={'language_code':'en-IN'}).json()['id'],
            'language_code': 'en-IN',
            'message': 'Can you help me with my plants?'
        }).json()
        assert unknown['crop'] is None
        assert 'Which crop' in unknown['assistant_message']['content']


def test_voice_routes_validate_locale_upload_limit_and_media_type(monkeypatch):
    monkeypatch.setattr(main_module, 'MAX_AUDIO_BYTES', 4)
    monkeypatch.setattr(main_module, 'STT_SERVICE', type('FakeSTT', (), {
        'transcribe': staticmethod(lambda audio, filename, language: 'తెలుగు వాక్యం')
    })())
    monkeypatch.setattr(main_module, 'TTS_SERVICE', type('FakeTTS', (), {
        'synthesize': staticmethod(lambda text, language: b'RIFF-WAVE')
    })())

    with TestClient(app) as client:
        oversized = client.post('/api/voice/transcribe', data={'language_code': 'te-IN'}, files={'audio_file': ('recording.wav', b'12345', 'audio/wav')})
        assert oversized.status_code == 413
        unsupported_stt = client.post('/api/voice/transcribe', data={'language_code': 'xx-XX'}, files={'audio_file': ('recording.wav', b'1234', 'audio/wav')})
        assert unsupported_stt.status_code == 422
        transcript = client.post('/api/voice/transcribe', data={'language_code': 'te-IN'}, files={'audio_file': ('recording.wav', b'1234', 'audio/wav')})
        assert transcript.json() == {'transcript': 'తెలుగు వాక్యం', 'language_code': 'te-IN'}
        unsupported_tts = client.post('/api/voice/synthesize', json={'text': 'hello', 'language_code': 'xx-XX'})
        assert unsupported_tts.status_code == 422
        audio = client.post('/api/voice/synthesize', json={'text': 'hello', 'language_code': 'en-IN'})
        assert audio.status_code == 200
        assert audio.headers['content-type'] == 'audio/wav'
        assert audio.content == b'RIFF-WAVE'


def test_chat_route_passes_history_to_gemini_agent_and_persists_sources(monkeypatch):
    captured = {}

    class FakeAgent:
        def respond(self, message, language_code, history):
            captured.update(message=message, language_code=language_code, history=history)
            return Advice('Check the local soil moisture first.', 'water', [], 'cotton', [
                {'title': 'ICAR', 'url': 'https://icar.gov.in/water'}
            ]), 'gemini'

    monkeypatch.setattr(main_module, 'ADVISOR', FakeAgent())
    with TestClient(app) as client:
        conversation_id = client.post('/api/conversations', json={'language_code': 'en-IN'}).json()['id']
        client.post('/api/chat', json={
            'conversation_id': conversation_id,
            'language_code': 'en-IN',
            'message': 'There are insects on my cotton leaves.',
        })
        response = client.post('/api/chat', json={
            'conversation_id': conversation_id,
            'language_code': 'en-IN',
            'message': 'How should I water it?',
        })

        assert captured['message'] == 'How should I water it?'
        assert captured['language_code'] == 'en-IN'
        assert [turn['role'] for turn in captured['history']] == ['user', 'assistant']
        assert response.json()['mode'] == 'gemini'
        assert 'https://icar.gov.in/water' in response.json()['assistant_message']['content']


def test_postgres_url_normalization_and_database_unavailable_response(monkeypatch):
    monkeypatch.setenv('DATABASE_URL', 'postgres://farmer:local-only@127.0.0.1:5432/fields')
    assert database._database_url() == 'postgresql+psycopg://farmer:local-only@127.0.0.1:5432/fields'

    def unavailable():
        raise SQLAlchemyError('connection refused')

    monkeypatch.setattr(main_module, 'check_database', unavailable)
    with TestClient(app) as client:
        response = client.get('/api/health')
        assert response.status_code == 503
        assert response.json()['detail'].startswith('Database unavailable.')
