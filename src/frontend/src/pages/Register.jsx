import { useRef, useState } from 'react'
import Form from 'react-bootstrap/Form'
import Button from 'react-bootstrap/Button'
import Alert from 'react-bootstrap/Alert'
import AuthCard from '../components/AuthCard'

export default function Register({ onNavigate, onAuthed }) {
  const usernameRef = useRef(null)
  const emailRef = useRef(null)
  const passwordRef = useRef(null)
  const repeatPasswordRef = useRef(null)
  const [errors, setErrors] = useState({})
  const [formError, setFormError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  function handleSubmit(event) {
    event.preventDefault()
    const username = usernameRef.current.value
    const email = emailRef.current.value
    const password = passwordRef.current.value
    const repeatPassword = repeatPasswordRef.current.value

    setErrors({})
    setFormError('')

    if (password !== repeatPassword) {
      setErrors({ repeat_password: 'Passwords do not match.' })
      return
    }

    setSubmitting(true)
    // TODO: wywolanie API
    if (onAuthed) {
      onAuthed({ username, email })
    }
    setSubmitting(false)
  }

  let errorAlert = null
  if (formError) {
    errorAlert = <Alert variant="danger">{formError}</Alert>
  }

  return (
    <AuthCard
      title="Create an account"
      onNavigate={onNavigate}
      footer={
        <>
          Already have an account?{' '}
          <a
            href="#"
            className="accent-neon"
            onClick={(event) => {
              event.preventDefault()
              if (onNavigate) {
                onNavigate('login')
              }
            }}
          >
            Sign in
          </a>
        </>
      }
    >
      {errorAlert}

      <Form noValidate onSubmit={handleSubmit}>
        <Form.Group className="mb-3" controlId="register-username">
          <Form.Label>Username</Form.Label>
          <Form.Control
            ref={usernameRef}
            type="text"
            name="username"
            isInvalid={!!errors.username}
            autoComplete="username"
          />
          <Form.Control.Feedback type="invalid">{errors.username}</Form.Control.Feedback>
        </Form.Group>

        <Form.Group className="mb-3" controlId="register-email">
          <Form.Label>Email</Form.Label>
          <Form.Control
            ref={emailRef}
            type="email"
            name="email"
            isInvalid={!!errors.email}
            autoComplete="email"
          />
          <Form.Control.Feedback type="invalid">{errors.email}</Form.Control.Feedback>
        </Form.Group>

        <Form.Group className="mb-3" controlId="register-password">
          <Form.Label>Password</Form.Label>
          <Form.Control
            ref={passwordRef}
            type="password"
            name="password"
            isInvalid={!!errors.password}
            autoComplete="new-password"
          />
          <Form.Control.Feedback type="invalid">{errors.password}</Form.Control.Feedback>
        </Form.Group>

        <Form.Group className="mb-4" controlId="register-repeat-password">
          <Form.Label>Repeat password</Form.Label>
          <Form.Control
            ref={repeatPasswordRef}
            type="password"
            name="repeat_password"
            isInvalid={!!errors.repeat_password}
            autoComplete="new-password"
          />
          <Form.Control.Feedback type="invalid">{errors.repeat_password}</Form.Control.Feedback>
        </Form.Group>

        <Button type="submit" className="btn-register w-100" disabled={submitting}>
          {submitting ? 'Creating account…' : 'Sign up'}
        </Button>
      </Form>
    </AuthCard>
  )
}
