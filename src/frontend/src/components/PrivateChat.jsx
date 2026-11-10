import { useEffect, useRef, useState } from 'react'
import Form from 'react-bootstrap/Form'
import Button from 'react-bootstrap/Button'
import Alert from 'react-bootstrap/Alert'
import { getCsrfToken } from '../csrf'
import { apiFetch } from '../api'

export default function PrivateChat({ otherUserId, otherUsername, onBack }) {
  const [roomId, setRoomId] = useState(null)
  const [messages, setMessages] = useState([])
  const [error, setError] = useState('')
  const inputRef = useRef(null)

  async function fetchMessages(id) {
    const response = await apiFetch('/api/chat/chat-rooms/' + id + '/messages/')
    if (!response.ok) {
      setError('Could not load messages.')
      return
    }
    const data = await response.json()
    setMessages(data.results.slice().reverse())
  }

  async function fetchRoom() {
    const response = await apiFetch('/api/chat/chat-rooms/user/' + otherUserId + '/')
    if (response.status === 404) {
      setRoomId(null)
      setMessages([])
      return
    }
    if (!response.ok) {
      setError('Could not load conversation.')
      return
    }
    const data = await response.json()
    setRoomId(data.id)
    await fetchMessages(data.id)
  }

  useEffect(() => {
    fetchRoom()
  }, [otherUserId])

  async function handleSend(event) {
    event.preventDefault()
    setError('')
    const content = inputRef.current.value

    if (content.trim() === '') {
      return
    }

    let body = { receiver: otherUserId, content }
    if (roomId) {
      body = { chat_room: roomId, content }
    }

    const response = await apiFetch('/api/chat/message/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify(body),
    })

    if (!response.ok) {
      setError('Could not send message.')
      return
    }

    inputRef.current.value = ''
    await fetchRoom()
  }

  let errorAlert = null
  if (error) {
    errorAlert = <Alert variant="danger" className="py-2">{error}</Alert>
  }

  return (
    <div className="d-flex flex-column" style={{ height: '400px' }}>
      <Button variant="outline-secondary" size="sm" className="mb-2 align-self-start" onClick={onBack}>
        Back
      </Button>

      <div className="mb-1 text-body-secondary">{otherUsername}</div>

      {errorAlert}

      <div
        className="flex-grow-1 overflow-auto mb-2 p-2 rounded"
        style={{ backgroundColor: '#000', border: '1px solid #333' }}
      >
        {messages.map((message) => {
          let senderLabel = 'Me'
          if (message.sender === otherUserId) {
            senderLabel = otherUsername
          }
          return (
            <div key={message.id}>
              <span className="accent-neon">{senderLabel}</span>: {message.content}
            </div>
          )
        })}
      </div>

      <Form onSubmit={handleSend} className="d-flex gap-2">
        <Form.Control ref={inputRef} placeholder="Message" autoComplete="off" />
        <Button type="submit">Send</Button>
      </Form>
    </div>
  )
}
