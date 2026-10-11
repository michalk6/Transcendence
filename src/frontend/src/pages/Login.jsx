import { useRef, useState } from 'react'
import Form from 'react-bootstrap/Form'
import Button from 'react-bootstrap/Button'
import Alert from 'react-bootstrap/Alert'
import AuthCard from '../components/AuthCard'

export default function Login({ onNavigate, onAuthed }) {
  const usernameRef = useRef(null)
  const passwordRef = useRef(null)
  const [formError, setFormError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    const username = usernameRef.current.value
    const password = passwordRef.current.value

    setFormError('')
    setSubmitting(true)

    const response = await fetch('/api/auth/login/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    })

    const data = await response.json()
    if (!response.ok) {
      setFormError('Invalid username or password')
    } else {
      const meResponse = await fetch('/api/users/me/', {
        headers: { Authorization: `Bearer ${data.access}` },
      })
      const user = await meResponse.json()
      onAuthed(user, data.access)
    }

    setSubmitting(false)
  }

  let errorAlert = null
  if (formError) {
    errorAlert = <Alert variant="danger">{formError}</Alert>
  }

  return (
    <AuthCard 
      title="Sign in"
      onNavigate={onNavigate}
      footer={
        <>
          No account yet?{' '}
          <a href="#" className="accent-neon"
            onClick={(event) => {
              event.preventDefault()
              if (onNavigate) {
                onNavigate('register')
              }
            }}
          >
            Sign up
          </a>
        </>
      }
    >
      {errorAlert}

      <Form onSubmit={handleSubmit}>
        <Form.Group className="mb-3" controlId="login-username">
          <Form.Label>Username</Form.Label>
          <Form.Control
            ref={usernameRef}
            name="username"
            autoComplete="username"
          />
        </Form.Group>

        <Form.Group className="mb-4" controlId="login-password">
          <Form.Label>Password</Form.Label>
          <Form.Control
            ref={passwordRef}
            type="password"
            name="password"
            autoComplete="current-password"
          />
        </Form.Group>

        <Button type="submit" className="btn-register w-100" disabled={submitting}>
          {submitting ? 'Signing in…' : 'Sign in'}
        </Button>
      </Form>
    </AuthCard>
  )
}
