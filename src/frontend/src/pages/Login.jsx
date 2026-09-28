import { useRef, useState } from 'react'
import Form from 'react-bootstrap/Form'
import Button from 'react-bootstrap/Button'
import Alert from 'react-bootstrap/Alert'
import AuthCard from '../components/AuthCard'

export default function Login({ onNavigate, onAuthed }) {
  const usernameRef = useRef(null)
  const [formError, setFormError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  function handleSubmit(event) {
    event.preventDefault()
    const username = usernameRef.current.value

    setFormError('')
    setSubmitting(true)
    // TODO: wywolanie API
    if (onAuthed) {
      onAuthed({ username })
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
