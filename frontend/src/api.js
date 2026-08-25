const API_BASE = import.meta.env.VITE_API_URL || '/api'

export async function sendChat(message, conversationHistory = []) {
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      conversation_history: conversationHistory,
    }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `Server error: ${res.status}`)
  }
  return res.json()
}

export async function refreshData() {
  const res = await fetch(`${API_BASE}/refresh`, { method: 'POST' })
  if (!res.ok) throw new Error(`Refresh failed: ${res.status}`)
  return res.json()
}

export async function getHealth() {
  const res = await fetch(`${API_BASE}/health`)
  if (!res.ok) throw new Error('Health check failed')
  return res.json()
}
