# 🌾 RythuMitra AI — Voice-First Multilingual Farming Assistant

[![Live Frontend](https://img.shields.io/badge/Live%20Demo-Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://rythu-mitra-ai-voice-assistent.vercel.app/)
[![Backend Status](https://img.shields.io/badge/Backend-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://render.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-6.0-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vite.dev/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

> **Live Application URL:** **[https://rythu-mitra-ai-voice-assistent.vercel.app/](https://rythu-mitra-ai-voice-assistent.vercel.app/)**

---

## 📌 Problem Statement

Agriculture is the backbone of India's economy, supporting over **58% of the rural population**. However, millions of smallholder and marginal farmers face severe challenges in accessing timely, scientific, and actionable agricultural guidance:

1. **Digital & Literacy Divide**: Traditional agricultural portals, PDFs, and government websites are text-heavy and predominantly in English or formal administrative language, making them difficult for farmers who prefer conversational interaction.
2. **Linguistic Diversity**: India is home to hundreds of dialects and languages. Farmers think and express farm problems in their native tongue (e.g., Telugu, Hindi, Tamil, Kannada), which generic AI assistants fail to comprehend with accurate agrarian nuances.
3. **Information Delay & Misinformation**: When pests attack or sudden unseasonal rains threaten crops, farmers often lack immediate expert advice and resort to unverified local pesticide store recommendations, resulting in crop losses or excessive chemical input costs.
4. **Climate & Weather Volatility**: Rapidly shifting weather patterns, rising temperatures, and erratic monsoon cycles require real-time climate adaptability, seasonal scheduling (Kharif, Rabi, Zaid), and water management advice tailored to local field realities.

---

## 💡 The Solution: RythuMitra AI

**RythuMitra AI (రైతు మిత్ర / किसान मित्र)** is an intelligent, voice-first agricultural companion designed specifically for Indian farmers. It bridges the digital divide by allowing farmers to **speak naturally in their native language** and receive instant, science-backed agricultural and climate advice spoken back to them.

```
       🎙️ Farmer Speaks (Native Language: Telugu, Hindi, Tamil, etc.)
                                 │
                                 ▼
                     [Speech-to-Text: Gnani Prisma]
                                 │
                                 ▼
             [Agronomic Reasoning: Google Gemini 2.5]
                + Google Search Grounding (ICAR / SAUs)
                + Crop & Climate Knowledge Engine
                                 │
                                 ▼
                    [Text-to-Speech: Gnani Timbre]
                                 │
                                 ▼
       🔊 Farmer Listens to Audio Advice + Reads Visual Step-by-Step Cards
```

---

## ✨ Key Features

- 🗣️ **10 Regional Languages**: Fluent support for **Telugu (`te-IN`)**, **English (`en-IN`)**, **Hindi (`hi-IN`)**, **Tamil (`ta-IN`)**, **Kannada (`kn-IN`)**, **Malayalam (`ml-IN`)**, **Marathi (`mr-IN`)**, **Bengali (`bn-IN`)**, **Gujarati (`gu-IN`)**, and **Punjabi (`pa-IN`)**.
- 🎙️ **Voice-First Input & Audio Playback**: High-accuracy Speech-to-Text with transcript review before submission, accompanied by human-sounding regional Text-to-Speech with **Play**, **Pause**, and **Replay** audio controls.
- 🌦️ **Crop & Climate Advisory**: Actionable guidance on temperature tolerances, ideal sowing seasons (Kharif, Rabi, Zaid), moisture and rainfall risk mitigation, and heatwave/frost protection for major Indian crops.
- 🔍 **Grounded Agronomic Reasoning**: Powered by Google Gemini with live Google Search grounding prioritizing official agricultural research institutions:
  - **ICAR** (Indian Council of Agricultural Research)
  - **ANGRAU** (Acharya N.G. Ranga Agricultural University)
  - **PJTSAU** (Professor Jayashankar Telangana State Agricultural University)
  - **TNAU** (Tamil Nadu Agricultural University)
  - **Ministry of Agriculture & Farmers Welfare**
- 💬 **Persistent Conversation History**: Multi-turn dialogue context retention across sessions, allowing farmers to ask follow-up questions (e.g., *"How old should the cotton crop be before harvesting?"*).
- 🛡️ **Offline/Demo Resilience**: Seamless fallback to deterministic, curated agronomic guidance if API credentials are unconfigured or external service quotas are reached.
- 📞 **Kisan Helpline Integration**: Direct one-touch access to the Government of India **Kisan Call Center (1800-180-1551)** and state disaster helplines.

---

## 🛠️ Tech Stack & Architecture

| Layer | Technologies & Tools | Purpose |
|---|---|---|
| **Frontend** | React 18, Vite 6, React Router 6, Lucide Icons, Custom CSS | High-performance, mobile-responsive SPA deployed on **Vercel** |
| **Backend API** | FastAPI, Python 3.10+, Uvicorn, Pydantic v2 | Async REST API deployed on **Render** |
| **Database** | SQLite (development) / PostgreSQL with SQLAlchemy 2.0 | Chat history and message persistence |
| **Generative AI** | Google Gemini (`google-genai` SDK) with Google Search Grounding | Agronomic knowledge retrieval, reasoning, and multi-turn context |
| **Speech-to-Text (STT)** | Gnani Prisma REST API / Web Audio API / MediaRecorder | Converting regional spoken queries into text |
| **Text-to-Speech (TTS)** | Gnani Timbre v2.5 / PCM-to-WAV extraction | Synthesizing natural regional voices |
| **Testing & CI** | Pytest, AnyIO, Starlette TestClient | 17+ comprehensive automated backend test suites |

---

## 📁 Repository Structure

```
RythuMitraAi-voice-Assistent-/
├── frontend/                     # React 18 + Vite frontend
│   ├── public/
│   │   └── images/               # Agricultural assets & hero banners
│   ├── src/
│   │   ├── components/           # ChatBubble, Header, MicrophoneButton, LanguageSelect
│   │   ├── pages/
│   │   │   ├── Home.jsx          # Landing page with hero, features & Kisan helpline footer
│   │   │   └── Assistant.jsx     # Voice & text assistant with dedicated sidebar
│   │   ├── lib/
│   │   │   ├── api.js            # Unified API client with VITE_API_BASE_URL support
│   │   │   └── config.js         # Multilingual prompt catalog across 10 Indian languages
│   │   ├── styles.css            # Base design system & typography
│   │   └── voice.css             # Voice assistant layout & custom green scrollbar
│   ├── package.json
│   ├── vercel.json               # Vercel Single Page Application routing config
│   └── vite.config.js
│
├── backend/                      # FastAPI Python backend
│   ├── app/
│   │   ├── main.py               # FastAPI application, endpoints & CORS
│   │   ├── advisor.py            # Agronomic knowledge engine & climate/pest detectors
│   │   ├── database.py           # SQLite & PostgreSQL persistence layer
│   │   └── services.py           # Gemini, Gnani STT (Prisma), Gnani TTS (Timbre)
│   ├── tests/
│   │   ├── test_api.py           # API route & climate integration tests
│   │   └── test_services.py      # Provider mocking and voice tests
│   ├── requirements.txt          # Python dependencies
│   ├── .python-version           # Pinned to Python 3.10.12
│   └── .env.example              # Template for environment variables
│
├── render.yaml                   # Infrastructure-as-code for Render deployment
├── requirements.txt              # Root dependency manifest for cloud hosting
└── README.md
```

---

## 🚀 Getting Started Locally

### Prerequisites
- **Node.js** 18+ and `npm`
- **Python** 3.10 or 3.11
- **FFmpeg** (for audio processing): `sudo apt install ffmpeg` (Ubuntu/Debian) or `brew install ffmpeg` (macOS)

---

### 1. Backend Setup (FastAPI)

```bash
# Navigate to the backend directory
cd backend

# Create and activate a Python virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create your local environment file
cp .env.example .env
```

Configure your `.env` file:
```env
PORT=8000
DATABASE_URL=sqlite:///./data/rythumitra.sqlite3
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Optional: Add your API keys for live cloud AI capabilities
GEMINI_API_KEY=your_gemini_api_key_here
SARVAM_API_KEY=your_sarvam_api_key_here
GNANI_STT_KEY=your_gnani_stt_key_here
GNANI_TTS_KEY=your_gnani_tts_key_here
```

Start the FastAPI server:
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Interactive API docs are available at **http://localhost:8000/docs**.

---

### 2. Frontend Setup (React + Vite)

Open a new terminal:
```bash
# Navigate to the frontend directory
cd frontend

# Install npm dependencies
npm install

# Start the Vite development server
npm run dev
```
Open **http://localhost:5173** in your browser to experience the assistant.

---

### 3. Running Automated Tests

Run the backend test suite:
```bash
cd backend
PYTHONPATH=. .venv/bin/pytest tests/
```
All **17 unit and integration tests** will execute and validate:
- Language code validation across all 10 Indic locales
- Crop detection (Cotton, Paddy, Tomato, Maize, Chilli, Dragon Fruit, etc.)
- Climate & weather query routing
- Multi-crop conversation history & session persistence
- Mocked voice synthesis and transcription pipelines

---

## 🌐 Cloud Deployment Guide

### Deploying Backend on Render
1. Create a **New Web Service** connected to your repository on [Render](https://render.com).
2. Set **Root Directory** to `backend`.
3. Set **Build Command**: `pip install -r requirements.txt`.
4. Set **Start Command**: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
5. Add Environment Variables:
   - `PYTHON_VERSION`: `3.10.12`
   - `GEMINI_API_KEY`: `<your_gemini_api_key>`
   - `ALLOWED_ORIGINS`: `*`
   - `DATABASE_URL`: `sqlite:///./data/rythumitra.sqlite3`

### Deploying Frontend on Vercel
1. Import your GitHub repository on [Vercel](https://vercel.com).
2. Set **Root Directory** to `frontend`.
3. Set **Framework Preset** to `Vite`.
4. Under **Environment Variables**, add:
   - `VITE_API_BASE_URL`: `https://your-backend-service.onrender.com`
5. Click **Deploy**. Vercel will build and provide your production URL.

---

## 📡 API Reference Summary

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check, mode status (`gemini` or `demo`), and database connection |
| `GET` | `/api/conversations` | List all historical conversations for the active session |
| `POST` | `/api/conversations` | Create a new conversation session with selected language locale |
| `GET` | `/api/conversations/{id}` | Retrieve messages and context for a specific conversation |
| `DELETE`| `/api/conversations/{id}` | Delete a conversation and its messages |
| `POST` | `/api/chat` | Send a query (text/audio transcript); returns grounded agricultural advice |
| `POST` | `/api/voice/transcribe` | Transcribe multipart audio file into regional text |
| `POST` | `/api/voice/synthesize` | Convert advisory text into high-quality WAV audio stream |

---

## 🌾 Supported Indian Crops & Domains

- **Cash Crops**: Cotton (ప్రత్తి / कपास), Sugarcane (చెరకు / गन्ना), Tobacco
- **Cereals & Grains**: Paddy / Rice (వరి / धान), Maize (మొక్కజొన్న / मक्का), Wheat (గోధుమ / गेहूँ)
- **Horticulture & Vegetables**: Tomato (టమోటా / टमाटर), Chilli (మిరప / मिर्च), Onion, Potato
- **Fruits & Plantation**: Banana (అరటి / केला), Mango (మామిడి / आम), Dragon Fruit

---

## ⚠️ Agricultural Advisory Disclaimer

> **Important Notice:** The advice provided by RythuMitra AI is generated using artificial intelligence grounded on public agronomic databases and research papers. It is intended for general guidance and educational purposes only. Farmers should consult with local Agricultural Extension Officers, Krishi Vigyan Kendras (KVK), or state agriculture department scientists before purchasing high-impact chemical inputs or making critical investment decisions.

---

## 📞 Helplines for Indian Farmers

- 📞 **Kisan Call Center (Toll-Free)**: `1800-180-1551` (Available 6:00 AM to 10:00 PM in all Indian languages)
- 🌾 **PM-Kisan Helpline**: `155261` / `011-24300606`
- 🛡️ **Crop Insurance (PMFBY)**: `1800-180-2117`

---

## 📄 License & Attribution

Developed with ❤️ for Indian farmers. Distributed under the **MIT License**.
