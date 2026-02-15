const API_BASE = '/api';

async function request(url, options = {}) {
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  // Remove Content-Type for FormData
  if (options.body instanceof FormData) {
    delete config.headers['Content-Type'];
  }

  const response = await fetch(`${API_BASE}${url}`, config);
  
  let data;
  const contentType = response.headers.get("content-type");
  if (contentType && contentType.includes("application/json")) {
    data = await response.json();
  } else {
    // If Vite proxy returns HTML/Empty string because backend isn't ready
    const text = await response.text();
    throw new Error(
      response.status === 504 || text.includes('Vite') 
      ? 'Backend server is still starting up. Please wait ~15 seconds and try again.' 
      : 'Unexpected response from server.'
    );
  }

  if (!response.ok) {
    throw new Error(data.detail || 'Something went wrong');
  }

  return data;
}

// ── Auth ────────────────────────────────────────────────
export async function login(username, password) {
  return request('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  });
}

export async function register(username, password) {
  return request('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  });
}

// ── Prescriptions ───────────────────────────────────────
export async function listPrescriptions(username) {
  return request(`/prescriptions/list?username=${encodeURIComponent(username)}`);
}

export async function uploadPrescription(file, username) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('username', username);
  return request('/prescriptions/upload', {
    method: 'POST',
    body: formData,
  });
}

// ── Sessions ────────────────────────────────────────────
export async function getSession(prescriptionId, username) {
  return request(`/sessions/${prescriptionId}?username=${encodeURIComponent(username)}`);
}

// ── Chat ────────────────────────────────────────────────
export async function getChatHistory(sessionId) {
  return request(`/chat/history/${sessionId}`);
}

export async function sendMessage(question, prescriptionId, sessionId, language = 'English') {
  return request('/chat', {
    method: 'POST',
    body: JSON.stringify({ question, prescription_id: prescriptionId, session_id: sessionId, language }),
  });
}

// ── OTC ─────────────────────────────────────────────────
export async function getOTCList() {
  return request('/otc/list');
}

export async function searchOTC(query) {
  return request(`/otc/search?q=${encodeURIComponent(query)}`);
}

export async function checkOTC(sessionId, prescriptionId, detailsText) {
  return request('/otc/check', {
    method: 'POST',
    body: JSON.stringify({ session_id: sessionId, prescription_id: prescriptionId, details_text: detailsText }),
  });
}

export async function getOTCResult(sessionId) {
  return request(`/otc/result/${sessionId}`);
}
