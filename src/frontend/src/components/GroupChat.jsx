import { useEffect, useRef, useState } from 'react'
import Form from 'react-bootstrap/Form'
import Button from 'react-bootstrap/Button'
import Alert from 'react-bootstrap/Alert'
import Pagination from 'react-bootstrap/Pagination'
import { getCsrfToken } from '../csrf'
import { apiFetch } from '../api'
import SearchBox from './SearchBox'
import ConfirmModal from './ConfirmModal'

const FRIENDS_PAGE_SIZE = 10

export default function GroupChat({ roomId, roomName, memberIds, onBack, socket, lastMessage, lastError, username }) {
  const [currentMemberIds, setCurrentMemberIds] = useState(memberIds)
  const [messages, setMessages] = useState([])
  const [displayName, setDisplayName] = useState(roomName)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const inputRef = useRef(null)
  const nameRef = useRef(null)

  const [showRenameForm, setShowRenameForm] = useState(false)
  const [showLeaveConfirm, setShowLeaveConfirm] = useState(false)

  const [showAddMembersForm, setShowAddMembersForm] = useState(false)
  const [friends, setFriends] = useState([])
  const [friendsTerm, setFriendsTerm] = useState('')
  const [friendsPage, setFriendsPage] = useState(1)
  const [friendsCount, setFriendsCount] = useState(0)
  const [selectedMemberIds, setSelectedMemberIds] = useState([])

  const totalFriendsPages = Math.ceil(friendsCount / FRIENDS_PAGE_SIZE)

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

  useEffect(() => {
    if (lastMessage && lastMessage.chat_room === roomId) {
      setMessages((prev) => [...prev, lastMessage])
    }
  }, [lastMessage])

  useEffect(() => {
    if (lastError) {
      setError(lastError)
    }
  }, [lastError])

  async function handleRename(event) {
    event.preventDefault()
    setError('')
    const name = nameRef.current.value

    if (name.trim() === '') {
      setError('New name cannot be blank.')
      return
    }

    const response = await apiFetch('/api/chat/chat-rooms/' + roomId + '/rename/', {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify({ name }),
    })

    const data = await response.json()
    if (!response.ok) {
      setError(extractErrorMessage(data, 'Could not rename the group.'))
      return
    }

    setDisplayName(data.name)
    setShowRenameForm(false)
  }

  async function fetchFriends(pageNumber) {
    const params = new URLSearchParams({
      search: friendsTerm,
      page_size: FRIENDS_PAGE_SIZE,
      page: pageNumber,
    })
    const response = await apiFetch('/api/users/profile/' + username + '/friends/?' + params)
    if (!response.ok) {
      setError('Could not load friends.')
      return
    }
    const data = await response.json()
    setFriends(data.results)
    setFriendsCount(data.count)
    setFriendsPage(pageNumber)
  }

  async function handleFriendsSearch(event) {
    event.preventDefault()
    await fetchFriends(1)
  }

  async function handleToggleAddMembersForm() {
    if (!showAddMembersForm) {
      await fetchFriends(1)
    }
    setShowAddMembersForm(!showAddMembersForm)
    setSelectedMemberIds([])
  }

  function toggleMember(userId) {
    if (selectedMemberIds.includes(userId)) {
      setSelectedMemberIds(selectedMemberIds.filter((id) => id !== userId))
    } else {
      setSelectedMemberIds([...selectedMemberIds, userId])
    }
  }

  async function handleAddMembers(event) {
    event.preventDefault()
    setError('')
    setMessage('')

    if (selectedMemberIds.length === 0) {
      setError('Pick at least one friend.')
      return
    }

    const response = await apiFetch('/api/chat/chat-rooms/' + roomId + '/members/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify({ members: selectedMemberIds }),
    })

    const data = await response.json()
    if (!response.ok) {
      setError(extractErrorMessage(data, 'Could not add members.'))
      return
    }

    setCurrentMemberIds(data.members)

    const warningMessages = Object.values(data.warnings || {}).map((warning) => warning.message)
    if (warningMessages.length > 0) {
      setError(warningMessages.join(' '))
    } else {
      setMessage('Members added.')
    }

    setSelectedMemberIds([])
    setShowAddMembersForm(false)
  }

  async function handleConfirmLeave() {
    setError('')
    setShowLeaveConfirm(false)

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

  function handleSend(event) {
    event.preventDefault()
    setError('')

    if (!socket) {
      setError('Not connected yet, try again in a moment.')
      return
    }

    const content = inputRef.current.value

    if (content.trim() === '') {
      return
    }

    socket.send(JSON.stringify({
      action: 'send_message',
      message: { chat_room: roomId, content },
    }))

    inputRef.current.value = ''
  }

  let errorAlert = null
  if (error) {
    errorAlert = <Alert variant="danger" className="py-2">{error}</Alert>
  }

  let messageAlert = null
  if (message) {
    messageAlert = <Alert variant="success" className="py-2">{message}</Alert>
  }

  let addMembersButtonLabel = 'Add members'
  if (showAddMembersForm) {
    addMembersButtonLabel = 'Cancel'
  }

  let friendsPagination = null
  if (totalFriendsPages > 1) {
    friendsPagination = (
      <Pagination size="sm" className="mb-2 justify-content-center">
        <Pagination.Prev
          disabled={friendsPage <= 1}
          onClick={() => fetchFriends(friendsPage - 1)}
        />
        <Pagination.Item disabled>
          {friendsPage} / {totalFriendsPages}
        </Pagination.Item>
        <Pagination.Next
          disabled={friendsPage >= totalFriendsPages}
          onClick={() => fetchFriends(friendsPage + 1)}
        />
      </Pagination>
    )
  }

  let renameFormContent = null
  if (showRenameForm) {
    renameFormContent = (
      <Form onSubmit={handleRename} className="d-flex gap-2 mb-2">
        <Form.Control ref={nameRef} placeholder="New name" defaultValue={displayName} />
        <Button type="submit" size="sm" className="btn-register">
          Save
        </Button>
      </Form>
    )
  }

  let addMembersFormContent = null
  if (showAddMembersForm) {
    addMembersFormContent = (
      <div className="mb-2">
        <SearchBox
          value={friendsTerm}
          onChange={setFriendsTerm}
          onSubmit={handleFriendsSearch}
          placeholder="Search friends…"
        />

        {friendsPagination}

        <Form onSubmit={handleAddMembers}>
          {friends.filter((friend) => !currentMemberIds.includes(friend.id)).map((friend) => (
            <Form.Check
              key={friend.id}
              type="checkbox"
              label={friend.username}
              checked={selectedMemberIds.includes(friend.id)}
              onChange={() => toggleMember(friend.id)}
            />
          ))}

          <Button type="submit" size="sm" className="btn-register mt-2">
            Add
          </Button>
        </Form>
      </div>
    )
  }

  return (
    <div className="d-flex flex-column">
      <div className="d-flex justify-content-between mb-2">
        <Button variant="outline-secondary" size="sm" onClick={onBack}>
          Back
        </Button>
        <Button variant="outline-danger" size="sm" onClick={() => setShowLeaveConfirm(true)}>
          Leave chat
        </Button>
      </div>

      <div className="d-flex justify-content-between align-items-center mb-2">
        <span className="text-body-secondary">{displayName}</span>
        <span className="d-flex gap-2">
          <Button
            variant="outline-secondary"
            size="sm"
            onClick={() => setShowRenameForm(!showRenameForm)}
          >
            Rename
          </Button>
          <Button variant="outline-secondary" size="sm" onClick={handleToggleAddMembersForm}>
            {addMembersButtonLabel}
          </Button>
        </span>
      </div>

      {renameFormContent}
      {addMembersFormContent}

      {messageAlert}
      {errorAlert}

      <div
        className="overflow-auto mb-2 p-2 rounded"
        style={{ height: '250px', backgroundColor: '#000', border: '1px solid #333' }}
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

      <ConfirmModal
        show={showLeaveConfirm}
        title="Leave chat"
        body={<p>Leave <strong>{displayName}</strong>? You can only rejoin if someone adds you back.</p>}
        confirmLabel="Leave"
        onConfirm={handleConfirmLeave}
        onCancel={() => setShowLeaveConfirm(false)}
      />
    </div>
  )
}
