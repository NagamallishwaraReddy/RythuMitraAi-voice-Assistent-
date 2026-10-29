import io
import wave
from types import SimpleNamespace

import httpx
import pytest
from google import genai

from app.services import FarmingAgentService, GeminiService, GnaniSTTService, GnaniTTSService, ProviderError


def test_gemini_receives_recent_chat_and_returns_official_sources(monkeypatch):
    captured = {}
    response = SimpleNamespace(
        text='Check soil moisture before watering.',
        candidates=[SimpleNamespace(grounding_metadata=SimpleNamespace(grounding_chunks=[
            SimpleNamespace(web=SimpleNamespace(uri='https://icar.gov.in/advice', title='ICAR')),
            SimpleNamespace(web=SimpleNamespace(uri='https://example.com/blog', title='Unverified')),
        ]))],
    )

    class FakeClient:
        def __init__(self, api_key, **kwargs):
            captured['key'] = api_key
            self.models = self

        def generate_content(self, **kwargs):
            captured.update(kwargs)
            return response

    monkeypatch.setattr(genai, 'Client', FakeClient)
    history = [
        {'role': 'user', 'content': 'There are insects on my cotton leaves.'},
        {'role': 'assistant', 'content': 'How old is the crop?'},
    ]
    advice, mode = FarmingAgentService(gemini=GeminiService('test-key', 'gemini-test')).respond(
        'How should I water it?', 'en-IN', history
    )

    assert mode == 'gemini'
    assert advice.crop == 'cotton'
    assert 'cotton leaves' in captured['contents']
    assert 'How should I water it?' in captured['contents']
    assert advice.sources == [{'title': 'ICAR', 'url': 'https://icar.gov.in/advice'}]


def test_gemini_provider_error_does_not_fall_back(monkeypatch):
    class FailingClient:
        def __init__(self, api_key, **kwargs):
            self.models = self

        def generate_content(self, **kwargs):
            raise RuntimeError('model not found: gemini-unavailable')

    monkeypatch.setattr(genai, 'Client', FailingClient)
    agent = FarmingAgentService(gemini=GeminiService('test-key', 'gemini-unavailable'))
    with pytest.raises(ProviderError, match='model not found') as error:
        agent.respond('How do I grow wheat?', 'en-IN', [])
    assert 'gemini-3.6-flash' in error.value.detail
    assert 'No fallback was attempted' in error.value.detail


def test_prisma_multipart_request_and_transcript(monkeypatch):
    captured = {}

    def handler(request):
        captured['headers'] = request.headers
        captured['body'] = request.content
        return httpx.Response(200, json={'success': True, 'transcript': 'నా పత్తి పంటకు నీరు ఎలా పెట్టాలి?'})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    monkeypatch.setattr(GnaniSTTService, '_check_duration', staticmethod(lambda path: None))
    monkeypatch.setattr(GnaniSTTService, '_convert_to_wav', staticmethod(lambda source, destination: destination.write_bytes(b'wav-data')))
    service = GnaniSTTService('test-key', client)

    transcript = service.transcribe(b'webm-data', 'voice.webm', 'te-IN')

    assert transcript.startswith('నా పత్తి')
    assert captured['headers']['x-api-key-id'] == 'test-key'
    assert 'name="audio_file"' in captured['body'].decode('latin1')
    assert 'name="language_code"' in captured['body'].decode('latin1')


def test_timbre_uses_catalog_voice_and_returns_wav():
    captured = {}
    audio = b'RIFF\x00\x00\x00\x00WAVE'

    def handler(request):
        captured['headers'] = request.headers
        captured['payload'] = request.read()
        return httpx.Response(200, content=audio, headers={'content-type': 'audio/wav'})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    service = GnaniTTSService('test-key', client=client)

    assert service.synthesize('వరి పంటకు నీరు ఇవ్వండి', 'te-IN') == audio
    assert captured['headers']['x-api-key-id'] == 'test-key'
    assert b'"voice":"Suhana"' in captured['payload']
    assert b'"model":"timbre-v2.5"' in captured['payload']
    assert b'"language":"te-IN"' in captured['payload']


def test_timbre_synthesizes_long_text_chunks():
    chunks_sent = []
    def make_wav():
        bio = io.BytesIO()
        with wave.open(bio, 'wb') as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(48000)
            w.writeframes(b'\x00\x00' * 4800)
        return bio.getvalue()
    sample_wav = make_wav()

    def handler(request):
        chunks_sent.append(request.read())
        return httpx.Response(200, content=sample_wav, headers={'content-type': 'audio/wav'})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    service = GnaniTTSService('test-key', client=client)
    long_text = 'వరి పంటకు ఎరువుల యాజమాన్యం చాలా ముఖ్యం. ' * 30
    res = service.synthesize(long_text, 'te-IN')
    assert len(chunks_sent) > 1
    assert len(res) > len(sample_wav)


def test_timbre_rejects_unsupported_language():
    with pytest.raises(ProviderError, match='does not support'):
        GnaniTTSService('test-key').synthesize('hello', 'xx-XX')


def test_placeholder_values_are_not_treated_as_credentials():
    assert not GeminiService('your_gemini_api_key').configured
    assert not GnaniSTTService('your_gnani_prisma_key').configured
    assert not GnaniTTSService('your_gnani_timbre_key').configured


def test_prisma_reports_empty_transcript_and_timeout(monkeypatch):
    monkeypatch.setattr(GnaniSTTService, '_check_duration', staticmethod(lambda path: None))
    monkeypatch.setattr(GnaniSTTService, '_convert_to_wav', staticmethod(lambda source, destination: destination.write_bytes(b'wav-data')))
    empty_client = httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(200, json={'transcript': ' '})))
    with pytest.raises(ProviderError, match='empty transcript'):
        GnaniSTTService('test-key', empty_client).transcribe(b'webm-data', 'voice.webm', 'te-IN')

    def timeout(request):
        raise httpx.ReadTimeout('provider timeout')

    timeout_client = httpx.Client(transport=httpx.MockTransport(timeout))
    with pytest.raises(ProviderError, match='timed out') as error:
        GnaniSTTService('test-key', timeout_client).transcribe(b'webm-data', 'voice.webm', 'te-IN')
    assert error.value.status_code == 504


@pytest.mark.parametrize(('status_code', 'expected_status'), [(401, 502), (429, 429)])
def test_timbre_maps_bad_credentials_and_quota(status_code, expected_status):
    client = httpx.Client(transport=httpx.MockTransport(
        lambda request: httpx.Response(status_code, json={'error': {'message': 'provider rejected request'}})
    ))
    with pytest.raises(ProviderError, match='provider rejected request') as error:
        GnaniTTSService('test-key', client=client).synthesize('hello', 'en-IN')
    assert error.value.status_code == expected_status