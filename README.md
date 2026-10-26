# 🌿 RythuMitra AI — Voice-First Farming Companion

**Phase 1: React frontend + FastAPI backend.** The visual design follows the mockup supplied for this project. This first phase intentionally does **not** include Gnani.ai or a live reasoning LLM; it is an executable foundation, with browser-based voice previews where supported.

## What works right now

- Responsive, green-and-cream **landing page** inspired by the reference image.
- Dedicated **voice-agent screen** with microphone, animated visualizer, selected language, chat bubbles, and answer playback controls.
- **Typed questions** go to a real FastAPI backend and return clearly labeled **example** farming responses.
- **Conversation history** persists in SQLite; create, open, and delete chats.
- **Browser speech-recognition preview** on supported browsers (often Chrome). Recording/transcription is handled by the browser—not yet by Gnani Prisma. Browser support, service access and privacy behavior vary.
- **Browser text-to-speech preview** on supported devices. Voices differ by operating system; it is **not Gnani Timbre** yet.
- A selector lists 10 planned Indian-language locales. Example backend answer templates currently cover **Telugu and English only**; other selections currently fall back to English. Full language support depends on later model integration and testing.
- `/api/voice/transcribe` and `/api/voice/synthesize` explicitly return `501 Not Implemented` until Gnani integration, rather than faking API results.

**Important:** The example replies are not verified agronomic diagnoses or pesticide/fertilizer prescriptions. Do not use them as professional agricultural advice.

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite 6, responsive custom CSS, Lucide icons |
| Backend | Python 3.10+, FastAPI, Pydantic |
| Persistence | SQLite built into Python |
| Voice preview | Optional browser `SpeechRecognition` and `speechSynthesis` |
| Planned speech-to-text | Gnani Prisma |
| Planned text-to-speech | Gnani Timbre |
| Planned reasoning | LLM API with cited agricultural knowledge |

## Requirements on Ubuntu / VS Code

- Python 3.10 or later
- Node.js 20 or later and npm
- VS Code with Python and JavaScript extensions
- Chromium/Google Chrome recommended for the temporary voice preview

You can use GitHub Copilot to inspect/edit the source. Keep API keys out of Git.

## Run locally (two terminals)

### Terminal 1 — FastAPI

```bash
cd rythumitra-ai/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

FastAPI docs: **http://localhost:8000/docs**

Check: **http://localhost:8000/api/health**

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
3. Click the example **Paddy leaf yellowing**. The backend should create a chat and return a Telugu example response.
4. Refresh the page. Your conversation should appear in **Your conversations**.
5. Type a question in English and change language to English. The response should use the English example template.
6. Click **Listen to answer** for browser audio preview.
7. Click the microphone and allow browser microphone permission. In supported browsers, speech transcription is a **browser preview**, not Gnani. If unsupported, type instead.
8. Try **New conversation**, open an older chat, and delete it.

### Backend test suite

```bash
cd rythumitra-ai/backend
pip install pytest httpx
python -m pytest -q
```

## API overview

| Method | Route | Phase 1 |
|---|---|---|
| GET | `/api/health` | Ready |
| GET | `/api/conversations` | Ready |
| POST | `/api/conversations` | Ready |
| GET | `/api/conversations/{id}` | Ready |
| DELETE | `/api/conversations/{id}` | Ready |
| POST | `/api/chat` | Ready, **scripted example advisor** |
| POST | `/api/voice/transcribe` | Placeholder (501) |
| POST | `/api/voice/synthesize` | Placeholder (501) |

The API documentation includes interactive JSON request examples.

## Next phase: connect Gnani + reasoning LLM

Do this only after the current frontend/backend run correctly.

1. **Prisma STT:** Add `POST /api/voice/transcribe` that receives audio uploaded from the React microphone; validate audio type/size/duration and transcode browser audio where needed, then send audio to Prisma using a **backend-only** Gnani credential. Return the transcript and associated language. Handle errors, dialects and uncertain recognition without inventing a transcript.
2. **Reasoning:** Replace `DemoAdvisor` with an LLM agent. Pass the transcript, selected language, confirmed location/crop details, and relevant snippets from verified ICAR/agricultural-university resources. Ask for missing details. Return plain-language text plus actual source citations. Block invented chemical dosages/diagnoses.
3. **Timbre TTS:** Implement `POST /api/voice/synthesize` to call Gnani Timbre with the final response. Return the audio file/stream using a matching MIME type and play it in React. Voice availability must be checked by language.
4. **Persistence:** Preserve conversation continuity and farmer-provided details with user control and a privacy policy; store raw audio only if explicitly needed and agreed.
5. **Language testing:** Verify each displayed language for both speech input and audio output on your actual Gnani account. Don't assume every language is available for every model and voice.

**Documentation:**
- [Gnani developer quick start](https://docs.gnani.ai/api/introduction/quick-start)
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
**Status:** Frontend/back-end prototype created. **Gnani STT/TTS and reasoning LLM intentionally deferred.**

## Any-crop support — updated Phase 1 scope

**RythuMitra AI is NOT limited to paddy.** A farmer should eventually be able to
ask *any agricultural question about any crop*. The UI now features cotton,
tomato, maize, banana and paddy examples, and the backend recognizes common
crop names across several Indian languages. It also remembers the crop from
recent questions within a conversation, so you can ask follow-ups such as
"How much water does it need?"

**Be clear about the current limitation:** This Phase 1 backend remains a
**rule-based demo**, not a real reasoning LLM. It does **not** yet provide
open-ended, evidence-based advice about every possible crop. For recognized
questions it asks cautious, crop-specific clarification questions. For
unrecognized crops or questions it requests more information rather than
inventing advice. Telugu and English demo templates are available; other
selected languages fall back to English until the multilingual LLM is wired up.

### Sample questions

- Cotton: "There are insects on my cotton leaves. What should I check?"
- Tomato: "I want to start growing tomatoes. What should I prepare?"
- Maize: "How should I manage irrigation for my maize crop?"
- Banana: "What should I know before applying fertilizer to banana plants?"
- Paddy: "Why are my paddy leaves turning yellow?"
- Follow-up: Ask about cotton, then ask "How old should it be before harvesting?"

### Phase 2 — how to enable *genuine* any-crop answers

1. Add Gnani Prisma STT for farmer audio.
2. Send the verified transcript, conversation history, and chosen language to a
   multilingual reasoning LLM (Gemini or another tested free-tier API).
3. Retrieve and cite relevant, **verified** agricultural information by crop,
   location, season and growth stage (agricultural university / extension
   references); allow safe clarification when the answer is uncertain.
4. Keep high-impact chemical, fertilizer and diagnosis advice grounded; do not
   fabricate doses, treatments, or guarantees.
5. Use Gnani Timbre to synthesize the approved answer in the selected language.

No real Gnani or LLM integration is claimed in Phase 1.
