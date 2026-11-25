import { useEffect, useRef, useState } from 'react'
import ListGroup from 'react-bootstrap/ListGroup'
import Alert from 'react-bootstrap/Alert'
import Form from 'react-bootstrap/Form'
import Button from 'react-bootstrap/Button'
import Pagination from 'react-bootstrap/Pagination'
import { getCsrfToken } from '../csrf'
import { apiFetch } from '../api'
import SearchBox from './SearchBox'

const FRIENDS_PAGE_SIZE = 10
const ROOMS_PAGE_SIZE = 10

export default function GroupRoomList({ username, onOpenRoom }) {
  const [rooms, setRooms] = useState([])
  const [roomsLoaded, setRoomsLoaded] = useState(false)
  const [roomsTerm, setRoomsTerm] = useState('')
  const [appliedRoomsTerm, setAppliedRoomsTerm] = useState('')
  const [roomsPage, setRoomsPage] = useState(1)
  const [friends, setFriends] = useState([])
  const [friendsTerm, setFriendsTerm] = useState('')
  const [friendsPage, setFriendsPage] = useState(1)
  const [friendsCount, setFriendsCount] = useState(0)
  const [selectedMemberIds, setSelectedMemberIds] = useState([])
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [error, setError] = useState('')
  const nameRef = useRef(null)

  const totalFriendsPages = Math.ceil(friendsCount / FRIENDS_PAGE_SIZE)
  const filteredRooms = rooms.filter((room) =>
    room.name.toLowerCase().includes(appliedRoomsTerm.toLowerCase())
  )
  const totalRoomsPages = Math.ceil(filteredRooms.length / ROOMS_PAGE_SIZE)
  const roomsPageStart = (roomsPage - 1) * ROOMS_PAGE_SIZE
  const visibleRooms = filteredRooms.slice(roomsPageStart, roomsPageStart + ROOMS_PAGE_SIZE)

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

  async function fetchRooms() {
    const params = new URLSearchParams({
      room_type: 'GROUP',
      page_size: 100,
    })
    const response = await apiFetch('/api/chat/chat-rooms/?' + params)
    if (!response.ok) {
      setError('Could not load chat rooms.')
      return
    }
    const data = await response.json()
    setRooms(data.results)
    setRoomsLoaded(true)
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

  function handleRoomsSearch(event) {
    event.preventDefault()
    setAppliedRoomsTerm(roomsTerm)
    setRoomsPage(1)
  }

  useEffect(() => {
    fetchRooms()
  }, [])

  async function handleToggleCreateForm() {
    if (!showCreateForm) {
      await fetchFriends(1)
    }
    setShowCreateForm(!showCreateForm)
  }

  function toggleMember(userId) {
    if (selectedMemberIds.includes(userId)) {
      setSelectedMemberIds(selectedMemberIds.filter((id) => id !== userId))
    } else {
      setSelectedMemberIds([...selectedMemberIds, userId])
    }
  }

  async function handleCreateRoom(event) {
    event.preventDefault()
    setError('')

    if (selectedMemberIds.length === 0) {
      setError('Pick at least one friend.')
      return
    }

    const response = await apiFetch('/api/chat/chat-rooms/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify({
        name: nameRef.current.value,
        members: selectedMemberIds,
      }),
    })

    const data = await response.json()
    if (!response.ok) {
      setError(extractErrorMessage(data, 'Could not create chat room.'))
      return
    }

    nameRef.current.value = ''
    setSelectedMemberIds([])
    setShowCreateForm(false)
    await fetchRooms()
  }

  let errorAlert = null
  if (error) {
    errorAlert = <Alert variant="danger" className="py-2">{error}</Alert>
  }

  let roomsEmptyText = 'No group conversations yet.'
  if (rooms.length > 0 && filteredRooms.length === 0) {
    roomsEmptyText = 'No matching group conversations.'
  }

  let roomsContent = null
  if (roomsLoaded) {
    if (filteredRooms.length === 0) {
      roomsContent = <p className="text-body-secondary">{roomsEmptyText}</p>
    } else {
      roomsContent = (
        <ListGroup className="mb-3">
          {visibleRooms.map((room) => (
            <ListGroup.Item
              key={room.id}
              action
              onClick={() => onOpenRoom(room)}
              className="bg-body-tertiary"
            >
              <div>{room.name}</div>
              <div className="text-body-secondary small">
                {room.last_message || 'No messages yet'}
              </div>
            </ListGroup.Item>
          ))}
        </ListGroup>
      )
    }
  }

  let roomsPagination = null
  if (totalRoomsPages > 1) {
    roomsPagination = (
      <Pagination size="sm" className="mb-2 justify-content-center">
        <Pagination.Prev
          disabled={roomsPage <= 1}
          onClick={() => setRoomsPage(roomsPage - 1)}
        />
        <Pagination.Item disabled>
          {roomsPage} / {totalRoomsPages}
        </Pagination.Item>
        <Pagination.Next
          disabled={roomsPage >= totalRoomsPages}
          onClick={() => setRoomsPage(roomsPage + 1)}
        />
      </Pagination>
    )
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

  let createFormContent = null
  if (showCreateForm) {
    createFormContent = (
      <>
        <SearchBox
          value={friendsTerm}
          onChange={setFriendsTerm}
          onSubmit={handleFriendsSearch}
          placeholder="Search friends…"
        />

        {friendsPagination}

        <Form onSubmit={handleCreateRoom} className="mb-3">
          {friends.map((friend) => (
            <Form.Check
              key={friend.id}
              type="checkbox"
              label={friend.username}
              checked={selectedMemberIds.includes(friend.id)}
              onChange={() => toggleMember(friend.id)}
            />
          ))}

          <Form.Control ref={nameRef} placeholder="Chat name (optional)" className="mt-2 mb-2" />

          <Button type="submit" className="btn-register" size="sm">
            Create
          </Button>
        </Form>
      </>
    )
  }

  let toggleButtonLabel = 'New group chat'
  if (showCreateForm) {
    toggleButtonLabel = 'Cancel'
  }

  return (
    <div>
      {errorAlert}

      <Button
        variant="outline-secondary"
        size="sm"
        className="mb-2"
        onClick={handleToggleCreateForm}
      >
        {toggleButtonLabel}
      </Button>

      {createFormContent}

      <SearchBox
        value={roomsTerm}
        onChange={setRoomsTerm}
        onSubmit={handleRoomsSearch}
        placeholder="Search group chats…"
      />

      {roomsContent}
      {roomsPagination}
    </div>
  )
}
