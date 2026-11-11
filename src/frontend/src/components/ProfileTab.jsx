import { useRef, useState } from 'react'
import Form from 'react-bootstrap/Form'
import Button from 'react-bootstrap/Button'
import Alert from 'react-bootstrap/Alert'
import { getCsrfToken } from '../csrf'
import { apiFetch } from '../api'

export default function ProfileTab({ user, onLogout, onUserUpdated }) {
  const [showEditForm, setShowEditForm] = useState(false)
  const [showAvatarForm, setShowAvatarForm] = useState(false)
  const [showPasswordForm, setShowPasswordForm] = useState(false)
  const [avatarVersion, setAvatarVersion] = useState(0)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [selectedFileName, setSelectedFileName] = useState('')

  const usernameRef = useRef(null)
  const emailRef = useRef(null)
  const firstNameRef = useRef(null)
  const lastNameRef = useRef(null)
  const avatarInputRef = useRef(null)
  const currentPasswordRef = useRef(null)
  const newPasswordRef = useRef(null)
  const repeatPasswordRef = useRef(null)

  function extractErrorMessage(data, fallback) {
    if (!data) {
      return fallback
    }
    if (typeof data.detail === 'string') {
      return data.detail
    }
    const firstArray = Object.values(data).find(
      (value) => Array.isArray(value) && value.length > 0
    )
    return firstArray ? firstArray[0] : fallback
  }

  async function handleSaveProfile(event) {
    event.preventDefault()
    setError('')
    setMessage('')

    const response = await apiFetch('/api/users/me/', {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify({
        username: usernameRef.current.value,
        email: emailRef.current.value,
        first_name: firstNameRef.current.value,
        last_name: lastNameRef.current.value,
      }),
    })

    const data = await response.json()
    if (!response.ok) {
      setError(extractErrorMessage(data, 'Could not update profile.'))
      return
    }

    onUserUpdated(data)
    setMessage('Profile updated.')
    setShowEditForm(false)
  }

  async function handleAvatarUpload(event) {
    event.preventDefault()
    setError('')
    setMessage('')

    const file = avatarInputRef.current.files[0]
    if (!file) {
      setError('Pick a file first.')
      return
    }

    const formData = new FormData()
    formData.append('avatar', file)

    const response = await apiFetch('/api/avatars/me/', {
      method: 'PUT',
      headers: { 'X-CSRFToken': getCsrfToken() },
      body: formData,
    })

    if (!response.ok) {
      const data = await response.json()
      setError(extractErrorMessage(data, 'Could not upload avatar.'))
      return
    }

    avatarInputRef.current.value = ''
    setSelectedFileName('')
    setAvatarVersion(avatarVersion + 1)
    setMessage('Avatar updated.')
    setShowAvatarForm(false)
  }

  function handleFileSelected(event) {
    const file = event.target.files[0]
    if (file) {
      setSelectedFileName(file.name)
    } else {
      setSelectedFileName('')
    }
  }

  async function handleChangePassword(event) {
    event.preventDefault()
    setError('')
    setMessage('')

    const response = await apiFetch('/api/users/me/password/', {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify({
        current_password: currentPasswordRef.current.value,
        new_password: newPasswordRef.current.value,
        repeat_password: repeatPasswordRef.current.value,
      }),
    })

    const data = await response.json()
    if (!response.ok) {
      setError(extractErrorMessage(data, 'Could not change password.'))
      return
    }

    setMessage('Password changed. You have been logged out, please sign in again.')
    setTimeout(onLogout, 3000)
  }

  async function handleDeleteAvatar() {
    setError('')
    setMessage('')

    const response = await apiFetch('/api/avatars/me/', {
      method: 'DELETE',
      headers: { 'X-CSRFToken': getCsrfToken() },
    })

    if (!response.ok) {
      setError('Could not remove avatar.')
      return
    }

    setAvatarVersion(avatarVersion + 1)
    setMessage('Avatar removed.')
  }

  let errorAlert = null
  if (error) {
    errorAlert = <Alert variant="danger" className="py-2">{error}</Alert>
  }

  let messageAlert = null
  if (message) {
    messageAlert = <Alert variant="success" className="py-2">{message}</Alert>
  }

  let fullNameLine = null
  if (user.first_name || user.last_name) {
    fullNameLine = <p className="mb-1">{(user.first_name + ' ' + user.last_name).trim()}</p>
  }

  let editButtonLabel = 'Edit profile'
  if (showEditForm) {
    editButtonLabel = 'Cancel'
  }

  let avatarButtonLabel = 'Update avatar'
  if (showAvatarForm) {
    avatarButtonLabel = 'Cancel'
  }

  let passwordButtonLabel = 'Change password'
  if (showPasswordForm) {
    passwordButtonLabel = 'Cancel'
  }

  let avatarFormContent = null
  if (showAvatarForm) {
    avatarFormContent = (
      <>
        <p className="text-body-secondary small mb-1">
          Allowed formats: JPEG, PNG, WEBP. Max size: 2 MB.
        </p>

        <Form onSubmit={handleAvatarUpload} className="d-flex align-items-center gap-2 mb-3">
          <Form.Control
            ref={avatarInputRef}
            type="file"
            id="avatar-file-input"
            accept="image/jpeg,image/png,image/webp"
            onChange={handleFileSelected}
            className="d-none"
          />
          <label htmlFor="avatar-file-input" className="btn btn-outline-secondary btn-sm mb-0">
            Choose file
          </label>
          <span
            className="text-body-secondary small text-truncate"
            style={{ minWidth: 0, maxWidth: '120px' }}
          >
            {selectedFileName || 'No file selected'}
          </span>
          <Button type="submit" size="sm" variant="outline-secondary">
            Upload
          </Button>
          <Button type="button" size="sm" variant="outline-danger" onClick={handleDeleteAvatar}>
            Remove
          </Button>
        </Form>
      </>
    )
  }

  let editFormContent = null
  if (showEditForm) {
    editFormContent = (
      <Form onSubmit={handleSaveProfile} className="mb-3">
        <Form.Group className="mb-2">
          <Form.Label className="small text-body-secondary mb-1">Username</Form.Label>
          <Form.Control ref={usernameRef} defaultValue={user.username} />
        </Form.Group>
        <Form.Group className="mb-2">
          <Form.Label className="small text-body-secondary mb-1">Email</Form.Label>
          <Form.Control ref={emailRef} defaultValue={user.email} />
        </Form.Group>
        <Form.Group className="mb-2">
          <Form.Label className="small text-body-secondary mb-1">First name</Form.Label>
          <Form.Control ref={firstNameRef} defaultValue={user.first_name} />
        </Form.Group>
        <Form.Group className="mb-2">
          <Form.Label className="small text-body-secondary mb-1">Last name</Form.Label>
          <Form.Control ref={lastNameRef} defaultValue={user.last_name} />
        </Form.Group>
        <Button type="submit" size="sm" className="btn-register">
          Save
        </Button>
      </Form>
    )
  }

  let passwordFormContent = null
  if (showPasswordForm) {
    passwordFormContent = (
      <Form onSubmit={handleChangePassword} className="mb-3">
        <Form.Group className="mb-2">
          <Form.Label className="small text-body-secondary mb-1">Current password</Form.Label>
          <Form.Control ref={currentPasswordRef} type="password" />
        </Form.Group>
        <Form.Group className="mb-2">
          <Form.Label className="small text-body-secondary mb-1">New password</Form.Label>
          <Form.Control ref={newPasswordRef} type="password" />
        </Form.Group>
        <Form.Group className="mb-2">
          <Form.Label className="small text-body-secondary mb-1">Repeat new password</Form.Label>
          <Form.Control ref={repeatPasswordRef} type="password" />
        </Form.Group>
        <Button type="submit" size="sm" className="btn-register">
          Change password
        </Button>
      </Form>
    )
  }

  return (
    <div>
      <div className="d-flex flex-column align-items-center mb-3">
        <img
          src={'/api/avatars/' + user.username + '/?v=' + avatarVersion}
          alt={user.username + "'s avatar"}
          width={96}
          height={96}
          className="rounded-circle mb-3"
        />
        <h5 className="accent-neon mb-1">{user.username}</h5>
        {fullNameLine}
        <p className="text-body-secondary mb-1">{user.email}</p>
      </div>

      {messageAlert}
      {errorAlert}

      <div className="mb-3">
        <Button
          variant="outline-secondary"
          size="sm"
          onClick={() => setShowAvatarForm(!showAvatarForm)}
        >
          {avatarButtonLabel}
        </Button>

        {avatarFormContent}
      </div>

      <div className="mb-3">
        <Button
          variant="outline-secondary"
          size="sm"
          onClick={() => setShowEditForm(!showEditForm)}
        >
          {editButtonLabel}
        </Button>

        {editFormContent}
      </div>

      <div className="mb-3">
        <Button
          variant="outline-secondary"
          size="sm"
          className="mb-2"
          onClick={() => setShowPasswordForm(!showPasswordForm)}
        >
          {passwordButtonLabel}
        </Button>

        {passwordFormContent}
      </div>

      <Button variant="outline-danger" className="mt-2" onClick={() => onLogout()}>
        Log out
      </Button>
    </div>
  )
}
