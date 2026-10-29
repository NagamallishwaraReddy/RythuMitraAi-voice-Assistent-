const API_PREFIX = '/api';

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_PREFIX}${path}`, {
      headers: {
        ...(typeof FormData !== 'undefined' && options.body instanceof FormData ? {} : { 'Content-Type': 'application/json' }),
        ...options.headers,
      },
      ...options,
    });
  } catch {
    throw new Error('Cannot connect to the backend. Start FastAPI at http://localhost:8000.');
  }
  if (!response.ok) {
    let error = `Request failed (${response.status})`;
    try { error = (await response.json()).detail || error; } catch { /* ignored */ }
    throw new Error(error);
  }
  return response.json();
}

async function requestAudio(path, options) {
  let response;
  try {
    response = await fetch(`${API_PREFIX}${path}`, {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      ...options,
    });
  } catch {
    throw new Error('Cannot connect to the backend. Start FastAPI at http://localhost:8000.');
  }
  if (!response.ok) {
    let error = `Request failed (${response.status})`;
    try { error = (await response.json()).detail || error; } catch { /* ignored */ }
    throw new Error(error);
  }
  return response.blob();
}

export const api = {
  health: () => request('/health'),
  listConversations: () => request('/conversations'),
  getConversation: id => request(`/conversations/${id}`),
  createConversation: (language_code) => request('/conversations', { method: 'POST', body: JSON.stringify({ language_code }) }),
  deleteConversation: id => request(`/conversations/${id}`, { method: 'DELETE' }),
  sendMessage: data => request('/chat', { method: 'POST', body: JSON.stringify(data) }),
  transcribe: (audio, language_code) => {
    const form = new FormData();
    const extension = audio.type.includes('ogg') ? 'ogg' : audio.type.includes('mp4') ? 'mp4' : audio.type.includes('wav') ? 'wav' : 'webm';
    form.append('audio_file', audio, `recording.${extension}`);
    form.append('language_code', language_code);
    return request('/voice/transcribe', { method: 'POST', body: form });
  },
  synthesize: (text, language_code) => requestAudio('/voice/synthesize', {
    method: 'POST', body: JSON.stringify({ text, language_code }),
  }),
};
