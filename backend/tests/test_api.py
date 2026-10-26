"""Run with: pip install pytest httpx && pytest -q"""
from fastapi.testclient import TestClient
from app.main import app


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


def test_future_integration_stubs():
    with TestClient(app) as client:
        assert client.post('/api/voice/transcribe').status_code == 501
        assert client.post('/api/voice/synthesize', json={'text':'hello'}).status_code == 501


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
