/**
 * In development, use same origin + Vite proxy → /api and /ws forward to FastAPI (port 8000).
 * Calling http://localhost:8000 directly from the browser causes CORS failures with POST actions.
 */
const trimTrailingSlash = (value = '') => value.replace(/\/+$/, '')

export const API_BASE_URL = (() => {
  if (import.meta.env.DEV) {
    return ''
  }

  const explicitApiUrl = trimTrailingSlash(import.meta.env.VITE_API_URL ?? '')
  if (explicitApiUrl) {
    return explicitApiUrl
  }

  // In production, default to same-origin routes (for Netlify redirects/proxies).
  return ''
})()

export function getWebSocketUrl() {
  const explicitWsUrl = trimTrailingSlash(import.meta.env.VITE_WS_URL ?? '')
  if (explicitWsUrl) {
    return explicitWsUrl
  }

  const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:'

  if (import.meta.env.DEV) {
    return `${proto}//${window.location.host}/ws`
  }
  return `${proto}//${window.location.host}/ws`
}

export async function getStatus() {
  const response = await fetch(`${API_BASE_URL}/api/status`)
  if (!response.ok) throw new Error('Failed to fetch status')
  return response.json()
}

export async function getAlerts(limit = 50, threatLevel = null) {
  let url = `${API_BASE_URL}/api/alerts?limit=${limit}`
  if (threatLevel) url += `&threat_level=${threatLevel}`

  const response = await fetch(url)
  if (!response.ok) throw new Error('Failed to fetch alerts')
  return response.json()
}

export async function getStatistics() {
  const response = await fetch(`${API_BASE_URL}/api/statistics`)
  if (!response.ok) throw new Error('Failed to fetch statistics')
  return response.json()
}

async function readErrorMessage(response, fallback) {
  try {
    const data = await response.json()
    if (data?.detail) {
      return typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)
    }
  } catch {
    /* ignore */
  }
  return fallback
}

export async function startDetection() {
  const response = await fetch(`${API_BASE_URL}/api/control/start`, {
    method: 'POST',
  })
  if (!response.ok) {
    const msg = await readErrorMessage(response, 'Failed to start detection')
    throw new Error(msg)
  }
  return response.json()
}

export async function stopDetection() {
  const response = await fetch(`${API_BASE_URL}/api/control/stop`, {
    method: 'POST',
  })
  if (!response.ok) {
    const msg = await readErrorMessage(response, 'Failed to stop detection')
    throw new Error(msg)
  }
  return response.json()
}

export async function testAlert() {
  const response = await fetch(`${API_BASE_URL}/api/alerts/test`, {
    method: 'POST',
  })
  if (!response.ok) throw new Error('Failed to send test alert')
  return response.json()
}

export async function createAlert(alertData) {
  const response = await fetch(`${API_BASE_URL}/api/alerts/create`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(alertData),
  })
  if (!response.ok) throw new Error('Failed to create alert')
  return response.json()
}
