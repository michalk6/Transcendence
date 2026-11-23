export function getCsrfToken() {
  const match = document.cookie.match(/csrftoken=([^;]+)/)
  if (match) {
    return match[1]
  } else {
    return null
  }
}