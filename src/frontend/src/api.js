import { getCsrfToken } from './csrf'

let onAuthExpired = null
let refreshPromise = null

export function setOnAuthExpired(fn) {
  onAuthExpired = fn
}

export function triggerAuthExpired() {
  if (onAuthExpired) {
    onAuthExpired()
  }
}

export function refreshAccessToken() {
  if (!refreshPromise) {
    refreshPromise = fetch('/api/auth/refresh/', {
      method: 'POST',
      headers: { 'X-CSRFToken': getCsrfToken() },
    }).finally(() => {
      refreshPromise = null
    })
  }
  return refreshPromise
}

export async function apiFetch(url, options) {
  const response = await fetch(url, options)
  if (response.status !== 401) {
    return response
  }

  const refreshResponse = await refreshAccessToken()
  if (!refreshResponse.ok) {
    triggerAuthExpired()
    return response
  }

  return fetch(url, options)
}
