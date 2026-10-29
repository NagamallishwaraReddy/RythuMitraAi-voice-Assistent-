# 🌿 RythuMitra AI — Voice-First Farming Companion

**Current stack: React + FastAPI + SQLite, with optional Gemini and Gnani integrations.** The existing green-and-white interface, routes, and conversation history are preserved.

## What works right now

- Responsive, green-and-cream **landing page** inspired by the reference image.
- Dedicated **voice-agent screen** with microphone, animated visualizer, selected language, chat bubbles, and answer playback controls.
- **Typed questions** retain the existing FastAPI/SQLite conversation workflow. With `GEMINI_API_KEY` configured, responses use Gemini and Google Search grounding; without it, the backend labels its deterministic responses as demo mode.
- **Conversation history** persists in SQLite; create, open, and delete chats.
- Microphone audio is recorded with `MediaRecorder`, uploaded to FastAPI, transcribed by Gnani Prisma, and presented for correction before submission.
- Assistant audio uses Gnani Timbre WAV with Play, Pause, and Replay controls. Timbre v2.5 voice selection is mapped to the selected language.
- The UI's ten BCP-47 locale codes are validated by the backend. Actual provider availability depends on the configured account and model access.

**Important:** The example replies are not verified agronomic diagnoses or pesticide/fertilizer prescriptions. Do not use them as professional agricultural advice.

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite 6, responsive custom CSS, Lucide icons |
| Backend | Python 3.10+, FastAPI, Pydantic, `google-genai`, `httpx` |
| Persistence | SQLite built into Python |
| Speech-to-text | Gnani Prisma REST API, FFmpeg conversion |
| Text-to-speech | Gnani Timbre v2.5 REST API |
| Reasoning | Gemini API with Google Search grounding |

## Requirements on Ubuntu / VS Code

- Python 3.10 or later
- Node.js 20 or later and npm
- FFmpeg and FFprobe (`sudo apt install ffmpeg` on Ubuntu)
- VS Code with Python and JavaScript extensions
- A secure context for microphone access (localhost is supported)

You can use GitHub Copilot to inspect/edit the source. Keep API keys out of Git.

## Run locally (two terminals)

### Terminal 1 — FastAPI

```bash
cd rythumitra-ai/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

To enable PostgreSQL locally on Ubuntu, create a role and database once (run this yourself because it uses the system PostgreSQL administrator account):

```bash
sudo -u postgres psql
```

At the `psql` prompt, set a private password of your choice:

```sql
CREATE USER rythumitra WITH PASSWORD 'choose_a_local_password';
CREATE DATABASE rythumitra OWNER rythumitra;
\q
```

Edit `backend/.env` and replace the password in `DATABASE_URL`. Set `GEMINI_API_KEY`, `GNANI_STT_KEY`, and `GNANI_TTS_KEY` when those providers are available. `GEMINI_MODEL` defaults to `gemini-3.8-flash`; `GNANI_TTS_MODEL` defaults to `timbre-v2.5`. Do not commit `.env` or put provider keys in frontend variables. If Gemini rejects the configured model, the API returns that provider error and compatible options; it does not switch models automatically.

Set `MIGRATE_SQLITE_HISTORY=1` for the first PostgreSQL startup if you want to copy existing SQLite conversations into an empty PostgreSQL database. This copy is non-destructive; SQLite remains unchanged. Set it back to `0` after migration. If `DATABASE_URL` is unset, local tests and development use the SQLite fallback.

FastAPI docs: **http://localhost:8000/docs**

Check: **http://localhost:8000/api/health**. It reports `database: postgresql` and `database_status: ok` when PostgreSQL is connected. If the role, database, or URL is wrong, the API returns a clear database-unavailable response rather than an opaque `500`.

### Terminal 2 — React

```bash
cd rythumitra-ai/frontend
npm install
npm run dev
```

Open **http://localhost:5173**. Click **Try the assistant**.

Vite proxies `/api` calls to FastAPI on port 8000. Both terminals must remain open. If you see “Backend offline” on the assistant page, verify the FastAPI terminal and `http://localhost:8000/api/health`.

> npm packages are downloaded on your computer during `npm install`. The archive intentionally does not include `node_modules`.

## Test it

1. Open the home page: the farmer hero, three feature cards and step-by-step explanation should display.
2. Click **Try the assistant**.
3. Click the example **Paddy leaf yellowing**. With Gemini configured, the response is generated and grounded by the provider; without a key, the API reports demo mode.
4. Refresh the page. Your conversation should appear in **Your conversations**.
5. Type a question in English and change language to English.
6. Use Play, Pause, or Replay to control the generated Gnani Timbre reply.
7. Record a short question; review and correct the transcript in the composer before sending it.
8. Try **New conversation**, open an older chat, and delete it.

### Backend test suite

```bash
cd rythumitra-ai/backend
python -m pytest -q
```

Provider tests use mocks and do not incur API calls. Live provider checks require credentials in `backend/.env`.

## API overview

| Method | Route | Behavior |
|---|---|---|
| GET | `/api/health` | Ready |
| GET | `/api/conversations` | Ready |
| POST | `/api/conversations` | Ready |
| GET | `/api/conversations/{id}` | Ready |
| DELETE | `/api/conversations/{id}` | Ready |
| POST | `/api/chat` | Gemini when configured; explicit demo mode without a Gemini key |
| POST | `/api/voice/transcribe` | Multipart `audio_file` + `language_code`; Prisma transcript |
| POST | `/api/voice/synthesize` | JSON text/locale; returns `audio/wav` from Timbre |

The API documentation includes interactive JSON request examples.

## Provider setup and limitations

- Gemini grounding uses Google Search. It prioritizes official agricultural domains and returns only source URLs actually present in the provider's grounding metadata. Search grounding is not a guarantee that every answer is agronomically verified.
- Exact fertilizer/pesticide rates and diagnoses are not invented; the system prompt requires clarification or a local agricultural expert when material facts are missing.
- Prisma accepts the ten configured Indian locales and recordings up to 60 seconds/15 MB; FFmpeg normalizes supported browser formats to mono 16 kHz WAV.
- Timbre v2.5 uses the official preferred voice mapping per locale. Unsupported languages and provider errors are returned to the UI rather than synthesized in another language.
- Live API calls have not been verified until valid local credentials are configured and a live request succeeds.

**Documentation:**
- [Gnani developer quick start](https://docs.gnani.ai/api/introduction/quick-start)
- [Gemini API docs](https://ai.google.dev/gemini-api/docs)
- [Gnani voice docs](https://docs.gnani.ai/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Vite](https://vite.dev/)

## Suggested file map

```
rythumitra-ai/
├── frontend/
│   ├── public/images/farmer-hero.jpg
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── styles.css
│   │   ├── components/{Header,Logo,LanguageSelect,MicrophoneButton,ChatBubble}.jsx
│   │   ├── pages/{Home,Assistant}.jsx
│   │   └── lib/{api,config}.js
│   ├── package.json
│   └── vite.config.js
├── backend/
│   ├── app/{main,advisor}.py
│   ├── tests/test_api.py
│   ├── requirements.txt
│   └── .env.example
├── .vscode/
├── .gitignore
└── README.md
```

### Security and realistic limitations

- **No login** is included. Conversations are local to this prototype backend, not isolated per user. **Do not deploy it publicly with real farmer data without adding authentication and account-level access control.**
- API credentials must only be stored on the backend; never in Vite's `VITE_*` variables or client source.
- Rate-limit user requests before public deployment; validate uploads and protect against unsafe use.
- Show the recorded transcript for farmer confirmation, especially crop name, dose, date and place names.
- Preserve any scientific uncertainty. Never represent example content as verified diagnosis.
- Images are cropped from design mockups provided in this project session; replace with licensed, original photography before deploying if appropriate.

---
**Status:** Gemini, Gnani Prisma, and Gnani Timbre integrations are implemented. Their live availability depends on valid keys, model access, account quota, and provider support; live calls have not been verified without local credentials.

## Current Limits

Gemini uses Google Search grounding with a preference for official agricultural sources. Grounding and returned citations do not guarantee agronomic correctness. Answers must not replace advice from a local agricultural extension officer, especially for diagnosis or high-impact chemical decisions.

The provider clients support the ten locales documented for Prisma and Timbre v2.5. The selected Timbre voice is chosen from Gnani's official preferred-voice catalog for that locale. A provider/account can still reject a model, language, or voice; the API returns that error instead of silently switching providers.

Without `GEMINI_API_KEY`, the backend explicitly reports demo mode and uses the existing deterministic example advisor. If Gemini is configured but fails, the request returns the provider error and does not fall back to demo content.

### Sample questions

- Cotton: "There are insects on my cotton leaves. What should I check?"
- Tomato: "I want to start growing tomatoes. What should I prepare?"
- Maize: "How should I manage irrigation for my maize crop?"
- Banana: "What should I know before applying fertilizer to banana plants?"
- Paddy: "Why are my paddy leaves turning yellow?"
- Follow-up: Ask about cotton, then ask "How old should it be before harvesting?"
