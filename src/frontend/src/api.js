import { getCsrfToken } from './csrf'

export async function apiFetch(url, options) {
  const response = await fetch(url, options)
  if (response.status !== 401) {
    return response
  }

  const refreshResponse = await fetch('/api/auth/refresh/', {
    method: 'POST',
    headers: { 'X-CSRFToken': getCsrfToken() },
  })
  if (!refreshResponse.ok) {
    return response
  }

  return fetch(url, options)
}
