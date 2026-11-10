import { useEffect, useRef, useState } from 'react'
import Form from 'react-bootstrap/Form'
import Button from 'react-bootstrap/Button'
import Alert from 'react-bootstrap/Alert'
import { getCsrfToken } from '../csrf'
import { apiFetch } from '../api'

export default function GroupChat({ roomId, roomName, onBack }) {
  const [messages, setMessages] = useState([])
  const [error, setError] = useState('')
  const inputRef = useRef(null)

  async function fetchMessages() {
    const response = await apiFetch('/api/chat/chat-rooms/' + roomId + '/messages/')
    if (!response.ok) {
      setError('Could not load messages.')
      return
    }
    const data = await response.json()
    setMessages(data.results.slice().reverse())
  }

  useEffect(() => {
    fetchMessages()
  }, [roomId])

  async function handleLeave() {
    setError('')

    const response = await apiFetch('/api/chat/chat-rooms/' + roomId + '/leave/', {
      method: 'POST',
      headers: { 'X-CSRFToken': getCsrfToken() },
    })

    if (!response.ok) {
      setError('Could not leave the group.')
      return
    }

    onBack()
  }

  async function handleSend(event) {
    event.preventDefault()
    setError('')
    const content = inputRef.current.value

    if (content.trim() === '') {
      return
    }

    const response = await apiFetch('/api/chat/message/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify({ chat_room: roomId, content }),
    })

    if (!response.ok) {
      setError('Could not send message.')
      return
    }

    inputRef.current.value = ''
    await fetchMessages()
  }

  let errorAlert = null
  if (error) {
    errorAlert = <Alert variant="danger" className="py-2">{error}</Alert>
  }

  return (
    <div className="d-flex flex-column" style={{ height: '400px' }}>
      <div className="d-flex justify-content-between mb-2">
        <Button variant="outline-secondary" size="sm" onClick={onBack}>
          Back
        </Button>
        <Button variant="outline-danger" size="sm" onClick={handleLeave}>
          Leave chat
        </Button>
      </div>

      <div className="mb-1 text-body-secondary">{roomName}</div>

      {errorAlert}

      <div
        className="flex-grow-1 overflow-auto mb-2 p-2 rounded"
        style={{ backgroundColor: '#000', border: '1px solid #333' }}
      >
        {messages.map((message) => (
          <div key={message.id}>
            <span className="accent-neon">User #{message.sender}</span>: {message.content}
          </div>
        ))}
      </div>

      <Form onSubmit={handleSend} className="d-flex gap-2">
        <Form.Control ref={inputRef} placeholder="Message" autoComplete="off" />
        <Button type="submit">Send</Button>
      </Form>
    </div>
  )
}
