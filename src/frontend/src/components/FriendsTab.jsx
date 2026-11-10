import { useEffect, useState } from 'react'
import Form from 'react-bootstrap/Form'
import Button from 'react-bootstrap/Button'
import ListGroup from 'react-bootstrap/ListGroup'
import Alert from 'react-bootstrap/Alert'
import Pagination from 'react-bootstrap/Pagination'
import ConfirmModal from './ConfirmModal'
import { getCsrfToken } from '../csrf'
import { apiFetch } from '../api'
import BlocklistTab from './BlocklistTab'
import SearchBox from './SearchBox'

const RESULTS_PAGE_SIZE = 10
const FRIENDS_PAGE_SIZE = 10

export default function FriendsTab({ username, onChanged, onMessage, reloadKey }) {
  const [showBlocked, setShowBlocked] = useState(false)
  const [removeTarget, setRemoveTarget] = useState(null)
  const [alsoBlock, setAlsoBlock] = useState(false)
  const [blockTarget, setBlockTarget] = useState(null)
  const [friends, setFriends] = useState([])
  const [friendsTerm, setFriendsTerm] = useState('')
  const [friendsPage, setFriendsPage] = useState(1)
  const [friendsCount, setFriendsCount] = useState(0)
  const [receivedRequests, setReceivedRequests] = useState([])
  const [sentRequests, setSentRequests] = useState([])
  const [term, setTerm] = useState('')
  const [results, setResults] = useState([])
  const [resultsPage, setResultsPage] = useState(1)
  const [resultsCount, setResultsCount] = useState(0)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const totalFriendsPages = Math.ceil(friendsCount / FRIENDS_PAGE_SIZE)

  const totalResultsPages = Math.ceil(resultsCount / RESULTS_PAGE_SIZE)

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

  async function fetchFriendsPage(pageNumber) {
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

  async function fetchReceivedRequests() {
    const response = await apiFetch('/api/relations/friend-requests/received/')
    if (!response.ok) {
      setError('Could not load friend requests.')
      return
    }
    const data = await response.json()
    setReceivedRequests(data.results)
  }

  async function fetchSentRequests() {
    const response = await apiFetch('/api/relations/friend-requests/sent/')
    if (!response.ok) {
      setError('Could not load sent friend requests.')
      return
    }
    const data = await response.json()
    setSentRequests(data.results)
  }

  useEffect(() => {
    fetchFriendsPage(1)
    fetchReceivedRequests()
    fetchSentRequests()
  }, [])

  async function handleAcceptRequest(requestId) {
    setMessage('')
    setError('')

    const response = await apiFetch('/api/relations/friend-requests/' + requestId + '/accept/', {
      method: 'POST',
      headers: { 'X-CSRFToken': getCsrfToken() },
    })

    if (!response.ok) {
      const data = await response.json()
      setError(extractErrorMessage(data, 'Could not accept friend request.'))
      return
    }

    setReceivedRequests((prev) => prev.filter((request) => request.id !== requestId))
    await fetchFriendsPage(1)
    setMessage('Friend request accepted.')
  }

  async function handleRejectRequest(requestId) {
    setMessage('')
    setError('')

    const response = await apiFetch('/api/relations/friend-requests/' + requestId + '/reject/', {
      method: 'POST',
      headers: { 'X-CSRFToken': getCsrfToken() },
    })

    if (!response.ok) {
      const data = await response.json()
      setError(extractErrorMessage(data, 'Could not reject friend request.'))
      return
    }

    setReceivedRequests((prev) => prev.filter((request) => request.id !== requestId))
    setMessage('Friend request rejected.')
  }

  async function handleCancelRequest(requestId) {
    setMessage('')
    setError('')

    const response = await apiFetch('/api/relations/friend-requests/' + requestId + '/', {
      method: 'DELETE',
      headers: { 'X-CSRFToken': getCsrfToken() },
    })

    if (!response.ok) {
      setError('Could not cancel friend request.')
      return
    }

    const cancelledRequest = sentRequests.find((request) => request.id === requestId)
    setSentRequests((prev) => prev.filter((request) => request.id !== requestId))

    if (cancelledRequest) {
      setResults((prev) =>
        prev.map((user) =>
          user.id === cancelledRequest.receiver ? { ...user, friendship_status: 'none' } : user
        )
      )
    }

    setMessage('Friend request cancelled.')
  }

  async function removeFriend(userId) {
    const response = await apiFetch('/api/relations/friends/' + userId + '/remove/', {
      method: 'POST',
      headers: { 'X-CSRFToken': getCsrfToken() },
    })

    if (!response.ok) {
      const data = await response.json()
      setError(extractErrorMessage(data, 'Could not remove friend.'))
      return false
    }

    await fetchFriendsPage(friendsPage)
    return true
  }

  async function blockUser(userId) {
    const response = await apiFetch('/api/relations/blocklist/' + userId + '/add/', {
      method: 'POST',
      headers: { 'X-CSRFToken': getCsrfToken() },
    })

    if (!response.ok) {
      const data = await response.json()
      setError(extractErrorMessage(data, 'Could not block user.'))
      return false
    }

    if (onChanged) {
      onChanged()
    }
    return true
  }

  function handleOpenRemoveModal(friend) {
    setRemoveTarget(friend)
    setAlsoBlock(false)
  }

  async function handleConfirmRemove() {
    setMessage('')
    setError('')

    const removed = await removeFriend(removeTarget.id)
    if (!removed) {
      return
    }

    if (alsoBlock) {
      const blocked = await blockUser(removeTarget.id)
      if (blocked) {
        setMessage('Friend removed and blocked.')
      }
    } else {
      setMessage('Friend removed.')
    }

    setRemoveTarget(null)
  }

  async function fetchResultsPage(pageNumber) {
    const params = new URLSearchParams({
      q: term,
      page_size: RESULTS_PAGE_SIZE,
      page: pageNumber,
    })
    const response = await apiFetch('/api/users/search/?' + params)
    if (!response.ok) {
      setError('Could not search users.')
      return
    }

    const data = await response.json()
    setResults(data.results)
    setResultsCount(data.count)
    setResultsPage(pageNumber)
  }

  async function handleSearch(event) {
    event.preventDefault()
    setMessage('')
    setError('')
    await fetchResultsPage(1)
  }

  async function handleFriendsSearch(event) {
    event.preventDefault()
    await fetchFriendsPage(1)
  }

  async function handleSendRequest(userId) {
    setMessage('')
    setError('')

    const response = await apiFetch('/api/relations/friend-requests/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify({ receiver: userId }),
    })

    const data = await response.json()
    if (!response.ok) {
      setError(extractErrorMessage(data, 'Could not send friend request.'))
      return
    }

    setResults((prev) =>
      prev.map((user) =>
        user.id === userId ? { ...user, friendship_status: 'request_sent' } : user
      )
    )
    setMessage('Friend request sent.')
  }

  async function handleUnblock(userId) {
    setMessage('')
    setError('')

    const response = await apiFetch('/api/relations/blocklist/' + userId + '/remove/', {
      method: 'POST',
      headers: { 'X-CSRFToken': getCsrfToken() },
    })

    if (!response.ok) {
      setError('Could not unblock user.')
      return
    }

    setResults((prev) =>
      prev.map((user) =>
        user.id === userId ? { ...user, friendship_status: 'none' } : user
      )
    )
    setMessage('User unblocked.')

    if (onChanged) {
      onChanged()
    }
  }

  async function handleConfirmBlock() {
    setMessage('')
    setError('')

    const blocked = await blockUser(blockTarget.id)
    if (blocked) {
      setResults((prev) => prev.filter((user) => user.id !== blockTarget.id))
      setMessage('User blocked.')
    }

    setBlockTarget(null)
  }

  function renderResultActions(user) {
    if (user.friendship_status === 'self') {
      return null
    }
    if (user.friendship_status === 'friends') {
      return <Button size="sm" variant="outline-secondary" disabled>Friends</Button>
    }
    if (user.friendship_status === 'blocked') {
      return (
        <Button size="sm" variant="outline-secondary" onClick={() => handleUnblock(user.id)}>
          Unblock
        </Button>
      )
    }

    let addOrStatusButton = (
      <Button size="sm" className="btn-register" onClick={() => handleSendRequest(user.id)}>
        Add
      </Button>
    )
    if (user.friendship_status === 'request_sent') {
      const matchingSentRequest = sentRequests.find(
        (request) => request.receiver === user.id
      )
      if (matchingSentRequest) {
        addOrStatusButton = (
          <Button
            size="sm"
            variant="outline-secondary"
            onClick={() => handleCancelRequest(matchingSentRequest.id)}
          >
            Cancel request
          </Button>
        )
      } else {
        addOrStatusButton = <Button size="sm" variant="outline-secondary" disabled>Request sent</Button>
      }
    } else if (user.friendship_status === 'request_received') {
      addOrStatusButton = <Button size="sm" variant="outline-secondary" disabled>Request received</Button>
    }

    return (
      <span className="d-flex gap-2">
        {addOrStatusButton}
        <Button size="sm" variant="outline-danger" onClick={() => setBlockTarget(user)}>
          Block
        </Button>
      </span>
    )
  }

  let messageAlert = null
  if (message) {
    messageAlert = <Alert variant="success" className="py-2">{message}</Alert>
  }

  let errorAlert = null
  if (error) {
    errorAlert = <Alert variant="danger" className="py-2">{error}</Alert>
  }

  let resultsPagination = null
  if (totalResultsPages > 1) {
    resultsPagination = (
      <Pagination size="sm" className="mb-2 justify-content-center">
        <Pagination.Prev
          disabled={resultsPage <= 1}
          onClick={() => fetchResultsPage(resultsPage - 1)}
        />
        <Pagination.Item disabled>
          {resultsPage} / {totalResultsPages}
        </Pagination.Item>
        <Pagination.Next
          disabled={resultsPage >= totalResultsPages}
          onClick={() => fetchResultsPage(resultsPage + 1)}
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
          onClick={() => fetchFriendsPage(friendsPage - 1)}
        />
        <Pagination.Item disabled>
          {friendsPage} / {totalFriendsPages}
        </Pagination.Item>
        <Pagination.Next
          disabled={friendsPage >= totalFriendsPages}
          onClick={() => fetchFriendsPage(friendsPage + 1)}
        />
      </Pagination>
    )
  }

  let toggleBlockedLabel = 'Blocked list'
  if (showBlocked) {
    toggleBlockedLabel = 'Back to friends'
  }

  if (showBlocked) {
    return (
      <>
        <Button
          variant="outline-secondary"
          size="sm"
          className="mb-2"
          onClick={() => setShowBlocked(false)}
        >
          {toggleBlockedLabel}
        </Button>

        <BlocklistTab reloadKey={reloadKey} />
      </>
    )
  }

  return (
    <>
      {messageAlert}
      {errorAlert}

      <Button
        variant="outline-secondary"
        size="sm"
        className="mb-2"
        onClick={() => setShowBlocked(true)}
      >
        {toggleBlockedLabel}
      </Button>

      <SearchBox
        value={term}
        onChange={setTerm}
        onSubmit={handleSearch}
        placeholder="Search for a user…"
      />

      {results.length > 0 && (
        <>
          {resultsPagination}

          <ListGroup className="mb-2">
            {results.map((user) => (
              <ListGroup.Item
                key={user.id}
                className="d-flex justify-content-between align-items-center"
              >
                <span>{user.username}</span>
                {renderResultActions(user)}
              </ListGroup.Item>
            ))}
          </ListGroup>
        </>
      )}

      {receivedRequests.length > 0 && (
        <>
          <div className="text-body-secondary mb-1">
            Friend requests ({receivedRequests.length})
          </div>
          <ListGroup className="mb-3">
            {receivedRequests.map((request) => (
              <ListGroup.Item
                key={request.id}
                className="d-flex justify-content-between align-items-center"
              >
                <span>{request.sender.username}</span>
                <span className="d-flex gap-2">
                  <Button
                    size="sm"
                    className="btn-register"
                    onClick={() => handleAcceptRequest(request.id)}
                  >
                    Accept
                  </Button>
                  <Button
                    size="sm"
                    variant="outline-secondary"
                    onClick={() => handleRejectRequest(request.id)}
                  >
                    Decline
                  </Button>
                </span>
              </ListGroup.Item>
            ))}
          </ListGroup>
        </>
      )}

      <div className="text-body-secondary mb-1">Your friends ({friendsCount})</div>

      <SearchBox
        value={friendsTerm}
        onChange={setFriendsTerm}
        onSubmit={handleFriendsSearch}
        placeholder="Search your friends…"
      />

      {friendsPagination}

      <ListGroup>
        {friends.length === 0 && (
          <ListGroup.Item className="text-body-secondary">
            No friends found.
          </ListGroup.Item>
        )}
        {friends.map((friend) => (
          <ListGroup.Item
            key={friend.id}
            className="d-flex justify-content-between align-items-center"
          >
            <span>{friend.username}</span>
            <span className="d-flex gap-2">
              <Button
                size="sm"
                className="btn-register"
                onClick={() => onMessage(friend)}
              >
                Message
              </Button>
              <Button
                size="sm"
                variant="outline-secondary"
                onClick={() => handleOpenRemoveModal(friend)}
              >
                Remove
              </Button>
            </span>
          </ListGroup.Item>
        ))}
      </ListGroup>

      <ConfirmModal
        show={removeTarget !== null}
        title="Remove friend"
        body={
          <>
            <p>
              Remove <strong>{removeTarget && removeTarget.username}</strong> from your friends?
            </p>
            <Form.Check
              type="checkbox"
              label="Also block this user"
              checked={alsoBlock}
              onChange={(event) => setAlsoBlock(event.target.checked)}
            />
          </>
        }
        confirmLabel="Remove"
        onConfirm={handleConfirmRemove}
        onCancel={() => setRemoveTarget(null)}
      />

      <ConfirmModal
        show={blockTarget !== null}
        title="Block user"
        body={<p>Block <strong>{blockTarget && blockTarget.username}</strong>?</p>}
        confirmLabel="Block"
        onConfirm={handleConfirmBlock}
        onCancel={() => setBlockTarget(null)}
      />
    </>
  )
}
