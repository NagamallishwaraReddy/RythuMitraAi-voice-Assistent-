const API_PREFIX = '/api';

async function request(path, options = {}) {
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
  return response.json();
}

export const api = {
  health: () => request('/health'),
  listConversations: () => request('/conversations'),
  getConversation: id => request(`/conversations/${id}`),
  createConversation: (language_code) => request('/conversations', { method: 'POST', body: JSON.stringify({ language_code }) }),
  deleteConversation: id => request(`/conversations/${id}`, { method: 'DELETE' }),
  sendMessage: data => request('/chat', { method: 'POST', body: JSON.stringify(data) }),
};
