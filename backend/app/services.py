"""External AI services used by the farming assistant."""
from __future__ import annotations

import io
import os
import re
import struct
import subprocess
import tempfile
import time
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx
from dotenv import load_dotenv

from .advisor import Advice, DemoAdvisor, detect_crop, detect_topic

BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / '.env')
LANGUAGE_CODES = {'te-IN', 'en-IN', 'hi-IN', 'kn-IN', 'ta-IN', 'ml-IN', 'mr-IN', 'bn-IN', 'gu-IN', 'pa-IN'}


class ProviderError(Exception):
    def __init__(self, status_code: int, detail: str):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


def _configured_secret(value: str | None) -> str:
    secret = (value or '').strip()
    lowered = secret.lower()
    if not secret or lowered.startswith(('your_', '<')) or lowered in {'replace_me', 'changeme'}:
        return ''
    return secret


@dataclass(frozen=True)
class GeminiResult:
    text: str
    sources: list[dict[str, str]]


class GeminiService:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = _configured_secret(api_key if api_key is not None else os.getenv('GEMINI_API_KEY'))
        self.model = model or os.getenv('GEMINI_MODEL', '').strip() or 'gemini-3.8-flash'

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    def answer(self, message: str, language_code: str, history: list[dict[str, str]]) -> GeminiResult:
        if not self.configured:
            raise ProviderError(503, 'Gemini is not configured. Add GEMINI_API_KEY to backend/.env.')

        try:
            from google import genai
            from google.genai import types
        except ImportError:
            raise ProviderError(503, 'Install backend requirements to enable the Gemini SDK.') from None

        language_names = {
            'te-IN': 'Telugu', 'en-IN': 'English', 'hi-IN': 'Hindi', 'kn-IN': 'Kannada',
            'ta-IN': 'Tamil', 'ml-IN': 'Malayalam', 'mr-IN': 'Marathi', 'bn-IN': 'Bengali',
            'gu-IN': 'Gujarati', 'pa-IN': 'Punjabi',
        }
        language = language_names[language_code]
        prior_turns = '\n'.join(
            f"{turn['role']}: {turn['content']}" for turn in history[-12:]
        ) or '(No earlier messages.)'
        prompt = (
            f"Conversation so far:\n{prior_turns}\n\n"
            f"Farmer's latest question ({language_code}): {message}"
        )
        system_instruction = (
            f"You are RythuMitra, a highly knowledgeable, practical agricultural expert assistant for farmers across India. "
            f"Reply only in {language}. "
            "Always provide DIRECT, ACCURATE, ACTIONABLE, and COMPLETE agricultural solutions immediately. "
            "Do NOT deflect, refuse to answer, or tell the farmer to consult a KVK or agricultural officer instead of answering. "
            "\n"
            "You MUST thoroughly answer all farming questions including:\n"
            "• CLIMATE & WEATHER FOR CROPS: Ideal temperature range in °C (for germination, vegetative growth, flowering, and maturity), rainfall requirements (mm), relative humidity (%), sunlight/daylight needs, suitable climatic zones, and optimal Indian sowing seasons (Kharif, Rabi, Zaid with specific months).\n"
            "• WEATHER RISK MANAGEMENT: Direct protection measures against heat stress, frost/cold waves, unseasonal heavy rains, waterlogging, hailstorms, drought spells, and climate-induced fungal/pest attacks.\n"
            "• AGRONOMY & PLANT HEALTH: Soil preparation, seed treatment, spacing, fertilizer schedules (NPK with exact split doses), irrigation methods, and pest/disease remedies with safe standard dosages (e.g. grams or ml per liter of water, or per acre) based on ICAR, ANGRAU, PJTSAU, and state agricultural university recommendations.\n"
            "\n"
            "Formatting Rules:\n"
            "- For climate & seasonal queries: Clearly structure with bullet points covering (1) Ideal Climate & Temperature Range, (2) Optimal Sowing Seasons & Months (Kharif/Rabi/Zaid), (3) Rainfall & Humidity Requirements, and (4) Weather Protection & Field Care Tips.\n"
            "- For pest, disease & nutrient queries: Structure with (1) Likely Causes/Identification, (2) Direct Solutions with Exact Safe Dosages, and (3) Important Precautions & Field Care.\n"
            "- For other general crop queries: Provide clear, concise, structured practical advice.\n"
            "Keep the language simple, respectful, practical, and easy for farmers to follow."
        )
        try:
            client = genai.Client(api_key=self.api_key, http_options=types.HttpOptions(timeout=45000))
            try:
                response = client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        tools=[types.Tool(google_search=types.GoogleSearch())],
                    ),
                )
            except Exception as search_exc:
                if '429' in str(search_exc) or 'quota' in str(search_exc).lower():
                    response = client.models.generate_content(
                        model=self.model,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction,
                        ),
                    )
                else:
                    raise
        except (httpx.TimeoutException, TimeoutError):
            raise ProviderError(504, 'Gemini timed out. Please try again.') from None
        except Exception as exc:
            code = getattr(exc, 'code', None)
            status = int(code) if isinstance(code, int) and 400 <= code <= 599 else 502
            detail = str(exc).strip() or 'Gemini request failed.'
            detail = detail.replace(self.api_key, '[redacted]')
            if status == 404 or 'model' in detail.lower() and any(term in detail.lower() for term in ('not found', 'not supported', 'unavailable')):
                detail += ' Compatible models to check explicitly include gemini-3.6-flash, gemini-3.5-flash-lite, and gemini-2.5-flash. No fallback was attempted.'
            raise ProviderError(status, f'Gemini API error: {detail}') from None

        answer = (getattr(response, 'text', None) or '').strip()
        if not answer:
            raise ProviderError(502, 'Gemini returned an empty response. Please retry.')
        sources: list[dict[str, str]] = []
        candidates = getattr(response, 'candidates', None) or []
        metadata = getattr(candidates[0], 'grounding_metadata', None) if candidates else None
        chunks = getattr(metadata, 'grounding_chunks', None) or []
        for chunk in chunks:
            web = getattr(chunk, 'web', None)
            uri = getattr(web, 'uri', None)
            title = getattr(web, 'title', None)
            if uri and _is_agricultural_source(uri) and uri not in {source['url'] for source in sources}:
                sources.append({'title': title or uri, 'url': uri})
        return GeminiResult(answer, sources)


def _is_agricultural_source(url: str) -> bool:
    parsed = urlparse(url)
    host = (parsed.hostname or '').lower()
    if parsed.scheme != 'https':
        return False
    return host.endswith(('.gov.in', '.icar.gov.in', '.icar.org.in', '.ac.in')) or host in {
        'icar.gov.in', 'icar.org.in'
    }


class FarmingAgentService:
    def __init__(self, gemini: GeminiService | None = None, demo: DemoAdvisor | None = None):
        self.gemini = gemini or GeminiService()
        self.demo = demo or DemoAdvisor()

    def respond(self, message: str, language_code: str, history: list[dict[str, str]]) -> tuple[Advice, str]:
        if not self.gemini.configured:
            user_history = [turn['content'] for turn in history if turn['role'] == 'user']
            return self.demo.respond(message, language_code, user_history), 'demo_rule_based'

        result = self.gemini.answer(message, language_code, history)
        crop = detect_crop(message)
        if crop is None:
            for turn in reversed(history):
                if turn['role'] == 'user':
                    crop = detect_crop(turn['content'])
                    if crop:
                        break
        return Advice(result.text, detect_topic(message), [], crop, result.sources), 'gemini'


class GnaniSTTService:
    endpoint = 'https://api.vachana.ai/stt/v3'

    def __init__(self, api_key: str | None = None, client: httpx.Client | None = None):
        self.api_key = _configured_secret(api_key if api_key is not None else os.getenv('GNANI_STT_KEY'))
        self.client = client

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    def transcribe(self, audio: bytes, filename: str, language_code: str) -> str:
        if language_code not in LANGUAGE_CODES:
            raise ProviderError(422, 'Unsupported language code for Gnani Prisma.')
        if not self.configured:
            raise ProviderError(503, 'Gnani Prisma is not configured. Add GNANI_STT_KEY to backend/.env.')
        if not audio:
            raise ProviderError(422, 'The recorded audio is empty.')

        try:
            with tempfile.TemporaryDirectory(prefix='rythumitra-stt-') as temp_dir:
                input_path = Path(temp_dir) / _safe_audio_name(filename)
                wav_path = Path(temp_dir) / 'recording.wav'
                input_path.write_bytes(audio)
                self._check_duration(input_path)
                self._convert_to_wav(input_path, wav_path)
                with wav_path.open('rb') as recording:
                    result = self._post_audio(recording.read(), language_code)
        except ProviderError:
            raise
        except subprocess.TimeoutExpired:
            raise ProviderError(422, 'Audio conversion timed out. Try a shorter recording.') from None
        except (OSError, subprocess.SubprocessError) as exc:
            raise ProviderError(422, f'Unable to process this recording: {exc}') from None

        transcript = str(result.get('transcript') or '').strip()
        if not transcript:
            raise ProviderError(422, 'Gnani Prisma returned an empty transcript. Please try recording again.')
        return transcript

    @staticmethod
    def _check_duration(path: Path) -> None:
        try:
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', str(path)],
                check=True, capture_output=True, text=True, timeout=10,
            )
            duration = float(result.stdout.strip())
        except FileNotFoundError:
            raise ProviderError(503, 'FFprobe is required for safe audio duration checks. Install FFmpeg.') from None
        except (subprocess.SubprocessError, ValueError):
            raise ProviderError(422, 'The uploaded audio format is invalid or unreadable.') from None
        if duration <= 0 or duration > 60:
            raise ProviderError(413, 'Recordings must be longer than 0 seconds and no longer than 60 seconds.')

    @staticmethod
    def _convert_to_wav(source: Path, destination: Path) -> None:
        try:
            subprocess.run(
                ['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', str(source), '-ac', '1', '-ar', '16000', '-t', '60', str(destination)],
                check=True, capture_output=True, timeout=20,
            )
        except FileNotFoundError:
            raise ProviderError(503, 'FFmpeg is required to process microphone audio. Install FFmpeg.') from None
        except subprocess.CalledProcessError:
            raise ProviderError(422, 'This browser audio format could not be converted. Try another recording.') from None

    def _post_audio(self, audio: bytes, language_code: str) -> dict[str, Any]:
        data = {'language_code': language_code, 'format': 'transcribe'}
        files = {'audio_file': ('recording.wav', audio, 'audio/wav')}
        headers = {'X-API-Key-ID': self.api_key}
        try:
            if self.client:
                response = self.client.post(self.endpoint, headers=headers, data=data, files=files, timeout=45)
            else:
                with httpx.Client(timeout=45) as client:
                    response = client.post(self.endpoint, headers=headers, data=data, files=files)
        except httpx.TimeoutException:
            raise ProviderError(504, 'Gnani Prisma timed out. Please try again.') from None
        except httpx.RequestError:
            raise ProviderError(503, 'Could not connect to Gnani Prisma.') from None
        if not response.is_success:
            raise _http_provider_error('Gnani Prisma', response, self.api_key)
        try:
            return response.json()
        except ValueError:
            raise ProviderError(502, 'Gnani Prisma returned an invalid response.') from None


def _clean_tts_text(text: str) -> str:
    """Clean markdown and syntax formatting for clean pronunciation."""
    cleaned = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    cleaned = re.sub(r'[*#_`~>]', '', cleaned)
    cleaned = re.sub(r'\n+', '. ', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


def _split_tts_chunks(text: str, max_chunk_chars: int = 1000) -> list[str]:
    """Split text into sentence-safe chunks that Gnani Timbre can process without HTTP 500 errors."""
    cleaned = _clean_tts_text(text)
    if not cleaned:
        return []
    if len(cleaned) <= max_chunk_chars:
        return [cleaned]

    sentences = re.split(r'([.?!।]\s+)', cleaned)
    pieces: list[str] = []
    i = 0
    while i < len(sentences):
        s = sentences[i]
        if i + 1 < len(sentences):
            s += sentences[i + 1]
            i += 2
        else:
            i += 1
        if s.strip():
            pieces.append(s.strip())

    chunks: list[str] = []
    current = ''
    for p in pieces:
        if not current:
            current = p
        elif len(current) + 1 + len(p) <= max_chunk_chars:
            current += ' ' + p
        else:
            chunks.append(current)
            if len(p) <= max_chunk_chars:
                current = p
            else:
                words = p.split(' ')
                sub = ''
                for w in words:
                    if not sub:
                        sub = w
                    elif len(sub) + 1 + len(w) <= max_chunk_chars:
                        sub += ' ' + w
                    else:
                        chunks.append(sub)
                        sub = w
                current = sub
    if current:
        chunks.append(current)
    return chunks


def _extract_pcm_from_wav(wav_bytes: bytes) -> bytes:
    """Extract raw linear PCM audio samples from WAV bytes, correctly handling streaming WAVs."""
    idx = wav_bytes.find(b'data')
    if idx == -1:
        return wav_bytes[44:] if len(wav_bytes) > 44 else wav_bytes
    return wav_bytes[idx + 8:]


def _concatenate_wav_bytes(chunks: list[bytes], sample_rate: int = 48000, num_channels: int = 1, bits_per_sample: int = 16) -> bytes:
    """Concatenate multiple PCM WAV audio byte buffers into a single seamless, fully playable WAV file."""
    if not chunks:
        return b''
    if len(chunks) == 1:
        return chunks[0]

    all_pcm = bytearray()
    for chunk in chunks:
        all_pcm.extend(_extract_pcm_from_wav(chunk))

    data_size = len(all_pcm)
    riff_size = 36 + data_size
    byte_rate = sample_rate * num_channels * (bits_per_sample // 8)
    block_align = num_channels * (bits_per_sample // 8)
    header = struct.pack(
        '<4sI4s4sIHHIIHH4sI',
        b'RIFF',
        riff_size,
        b'WAVE',
        b'fmt ',
        16,              # Subchunk1Size for PCM
        1,               # AudioFormat 1 = PCM
        num_channels,
        sample_rate,
        byte_rate,
        block_align,
        bits_per_sample,
        b'data',
        data_size,
    )
    return header + bytes(all_pcm)


class GnaniTTSService:
    endpoint = 'https://api.vachana.ai/api/v1/tts/inference'
    voices = {
        'en-IN': 'Kaveri', 'hi-IN': 'Nalini', 'te-IN': 'Suhana', 'kn-IN': 'Saanvi',
        'ta-IN': 'Asmita', 'ml-IN': 'Reshma', 'mr-IN': 'Zahira', 'bn-IN': 'Kirra',
        'gu-IN': 'Falak', 'pa-IN': 'Mehuli',
    }

    def __init__(self, api_key: str | None = None, model: str | None = None, client: httpx.Client | None = None):
        self.api_key = _configured_secret(api_key if api_key is not None else os.getenv('GNANI_TTS_KEY'))
        self.model = model or os.getenv('GNANI_TTS_MODEL', '').strip() or 'timbre-v2.5'
        self.client = client

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    def _synthesize_chunk(self, chunk_text: str, language_code: str) -> bytes:
        payload = {
            'text': chunk_text,
            'voice': self.voices[language_code],
            'model': self.model,
            'language': language_code,
            'speed': 1.0,
            'audio_config': {
                'sample_rate': 48000,
                'num_channels': 1,
                'sample_width': 2,
                'encoding': 'linear_pcm',
                'container': 'wav',
            },
        }
        try:
            if self.client:
                response = self.client.post(self.endpoint, headers={'X-API-Key-ID': self.api_key}, json=payload, timeout=60)
            else:
                with httpx.Client(timeout=60) as client:
                    response = client.post(self.endpoint, headers={'X-API-Key-ID': self.api_key}, json=payload)
        except httpx.TimeoutException:
            raise ProviderError(504, 'Gnani Timbre timed out. Please try again.') from None
        except httpx.RequestError:
            raise ProviderError(503, 'Could not connect to Gnani Timbre.') from None
        if not response.is_success:
            raise _http_provider_error('Gnani Timbre', response, self.api_key)
        content_type = response.headers.get('content-type', '').split(';', 1)[0].strip().lower()
        if content_type not in {'audio/wav', 'audio/x-wav', 'application/octet-stream'} or not response.content:
            raise ProviderError(502, 'Gnani Timbre did not return playable WAV audio.')
        return response.content

    def _synthesize_chunk_with_retry(self, chunk_text: str, language_code: str, max_retries: int = 2) -> bytes:
        for attempt in range(max_retries + 1):
            try:
                return self._synthesize_chunk(chunk_text, language_code)
            except ProviderError as exc:
                if exc.status_code == 429 and attempt < max_retries:
                    time.sleep(0.6 * (attempt + 1))
                    continue
                raise exc
        return b''

    def synthesize(self, text: str, language_code: str) -> bytes:
        if language_code not in self.voices:
            raise ProviderError(422, 'Timbre does not support this language code.')
        if not self.configured:
            raise ProviderError(503, 'Gnani Timbre is not configured. Add GNANI_TTS_KEY to backend/.env.')
        chunks = _split_tts_chunks(text, max_chunk_chars=1000)
        if not chunks:
            raise ProviderError(422, 'Please provide text to synthesize.')
        if len(chunks) == 1:
            return self._synthesize_chunk_with_retry(chunks[0], language_code)

        audio_chunks: list[bytes] = []
        for idx, chunk in enumerate(chunks):
            if idx > 0:
                time.sleep(0.3)
            try:
                audio = self._synthesize_chunk_with_retry(chunk, language_code)
                if audio:
                    audio_chunks.append(audio)
            except ProviderError as exc:
                if audio_chunks:
                    break
                raise exc
        return _concatenate_wav_bytes(audio_chunks)


def _safe_audio_name(filename: str) -> str:
    suffix = Path(filename or '').suffix.lower()
    supported = {'.wav', '.mp3', '.ogg', '.flac', '.aac', '.m4a', '.mp4', '.webm', '.oga'}
    return f'upload{suffix if suffix in supported else ".audio"}'


def _http_provider_error(provider: str, response: httpx.Response, secret: str) -> ProviderError:
    detail = ''
    try:
        payload = response.json()
        error = payload.get('error', payload) if isinstance(payload, dict) else {}
        detail = str(error.get('message') or error.get('detail') or '') if isinstance(error, dict) else ''
    except ValueError:
        detail = ''
    detail = detail.replace(secret, '[redacted]') if secret else detail
    status = 429 if response.status_code == 429 else 503 if response.status_code >= 500 else 502
    explanation = f'{provider} request failed with HTTP {response.status_code}'
    return ProviderError(status, f'{explanation}: {detail}' if detail else f'{explanation}.')