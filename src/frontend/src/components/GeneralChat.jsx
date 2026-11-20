import { useEffect, useRef, useState } from 'react'
import Form from 'react-bootstrap/Form'
import Button from 'react-bootstrap/Button'
import Alert from 'react-bootstrap/Alert'

export default function GeneralChat() {
  const [messages, setMessages] = useState([])
  const [error, setError] = useState('')
  const socketRef = useRef(null)
  const inputRef = useRef(null)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const socket = new WebSocket(protocol + '//' + window.location.host + '/ws/chat/general/')
    socketRef.current = socket

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'general_message_list') {
        setMessages(data.message_list)
      } else if (data.type === 'general_message') {
        setMessages((prev) => [...prev, data.message])
      } else if (data.type === 'error') {
        setError(data.detail)
      }
    }

    return () => {
      socket.close()
    }
  }, [])

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView()
    }
  }, [messages])

  function handleSubmit(event) {
    event.preventDefault()
    const content = inputRef.current.value

    if (content.trim() === '') {
      return
    }

    socketRef.current.send(JSON.stringify({ action: 'send_message', content }))
    inputRef.current.value = ''
  }

  let errorAlert = null
  if (error) {
    errorAlert = <Alert variant="danger" className="py-2">{error}</Alert>
  }

  return (
    <div className="d-flex flex-column" style={{ height: '400px' }}>
      <div
        className="flex-grow-1 overflow-auto mb-2 p-2 rounded"
        style={{ backgroundColor: '#000', border: '1px solid #333' }}
      >
        {messages.map((message, index) => (
          <div key={index}>
            <span className="accent-neon">{message.sender.username}</span>: {message.content}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {errorAlert}

      <Form onSubmit={handleSubmit} className="d-flex gap-2">
        <Form.Control ref={inputRef} placeholder="Message" autoComplete="off" />
        <Button type="submit">Send</Button>
      </Form>
    </div>
  )
}
