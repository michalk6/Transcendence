import { useEffect, useState } from 'react'
import Modal from 'react-bootstrap/Modal'
import Alert from 'react-bootstrap/Alert'
import { apiFetch } from '../api'

export default function UserProfile({ username, onClose, onlineUserIds }) {
  const [profile, setProfile] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    async function fetchProfile() {
      setError('')
      setProfile(null)

      const response = await apiFetch('/api/users/profile/' + username + '/')
      if (!response.ok) {
        setError('Could not load profile.')
        return
      }
      const data = await response.json()
      setProfile(data)
    }
    fetchProfile()
  }, [username])

  let errorAlert = null
  if (error) {
    errorAlert = <Alert variant="danger" className="py-2">{error}</Alert>
  }

  let profileContent = null
  if (profile) {
    let fullName = ''
    if (profile.first_name || profile.last_name) {
      fullName = (profile.first_name + ' ' + profile.last_name).trim()
    }

    let fullNameLine = null
    if (fullName) {
      fullNameLine = <p className="text-body-secondary mb-1">{fullName}</p>
    }

    let mutualFriendsLine = null
    if (profile.mutual_friends !== null) {
      mutualFriendsLine = (
        <p className="text-body-secondary mb-1">Mutual friends: {profile.mutual_friends}</p>
      )
    }

    let isOnline = false
    if (onlineUserIds) {
      isOnline = onlineUserIds.has(profile.id)
    }

    let statusIconClass = 'bi bi-circle-fill text-secondary'
    let statusLabel = 'Offline'
    if (isOnline) {
      statusIconClass = 'bi bi-circle-fill text-success'
      statusLabel = 'Online'
    }

    profileContent = (
      <div className="d-flex flex-column align-items-center">
        <img
          src={'/api/avatars/' + profile.username + '/'}
          alt={profile.username + "'s avatar"}
          width={96}
          height={96}
          className="rounded-circle mb-3"
        />
        <h5 className="accent-neon mb-1">{profile.username}</h5>
        <p className="mb-1">
          <i className={statusIconClass} style={{ fontSize: '0.6rem' }}></i> {statusLabel}
        </p>
        {fullNameLine}
        {mutualFriendsLine}
      </div>
    )
  }

  return (
    <Modal show={username !== null} onHide={onClose}>
      <Modal.Header closeButton>
        <Modal.Title>Profile</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {errorAlert}
        {profileContent}
      </Modal.Body>
    </Modal>
  )
}
