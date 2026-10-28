import { useEffect, useState } from 'react'
import Button from 'react-bootstrap/Button'
import ListGroup from 'react-bootstrap/ListGroup'
import Alert from 'react-bootstrap/Alert'
import Pagination from 'react-bootstrap/Pagination'
import { getCsrfToken } from '../csrf'
import { apiFetch } from '../api'

const BLOCKED_PAGE_SIZE = 10

export default function BlocklistTab({ reloadKey }) {
  const [blocked, setBlocked] = useState([])
  const [blockedPage, setBlockedPage] = useState(1)
  const [blockedCount, setBlockedCount] = useState(0)
  const [error, setError] = useState('')

  const totalBlockedPages = Math.ceil(blockedCount / BLOCKED_PAGE_SIZE)

  async function fetchBlockedPage(pageNumber) {
    const params = new URLSearchParams({
      page_size: BLOCKED_PAGE_SIZE,
      page: pageNumber,
    })
    const response = await apiFetch('/api/users/me/blocklist/?' + params)
    if (!response.ok) {
      setError('Could not load blocklist.')
      return
    }

    const data = await response.json()
    setBlocked(data.results)
    setBlockedCount(data.count)
    setBlockedPage(pageNumber)
  }

  useEffect(() => {
    fetchBlockedPage(1)
  }, [reloadKey])

  async function handleUnblock(userId) {
    setError('')

    const response = await apiFetch('/api/relations/blocklist/' + userId + '/remove/', {
      method: 'POST',
      headers: { 'X-CSRFToken': getCsrfToken() },
    })

    if (!response.ok) {
      setError('Could not unblock user.')
      return
    }

    await fetchBlockedPage(blockedPage)
  }

  let errorAlert = null
  if (error) {
    errorAlert = <Alert variant="danger" className="py-2">{error}</Alert>
  }

  let blockedPagination = null
  if (totalBlockedPages > 1) {
    blockedPagination = (
      <Pagination size="sm" className="mb-2 justify-content-center">
        <Pagination.Prev
          disabled={blockedPage <= 1}
          onClick={() => fetchBlockedPage(blockedPage - 1)}
        />
        <Pagination.Item disabled>
          {blockedPage} / {totalBlockedPages}
        </Pagination.Item>
        <Pagination.Next
          disabled={blockedPage >= totalBlockedPages}
          onClick={() => fetchBlockedPage(blockedPage + 1)}
        />
      </Pagination>
    )
  }

  return (
    <>
      {errorAlert}

      <div className="text-body-secondary mb-1">Blocked ({blockedCount})</div>

      {blockedPagination}

      <ListGroup>
        {blocked.length === 0 && (
          <ListGroup.Item className="text-body-secondary">
            You haven't blocked anyone.
          </ListGroup.Item>
        )}
        {blocked.map((user) => (
          <ListGroup.Item
            key={user.id}
            className="d-flex justify-content-between align-items-center"
          >
            <span>{user.username}</span>
            <Button
              size="sm"
              variant="outline-secondary"
              onClick={() => handleUnblock(user.id)}
            >
              Unblock
            </Button>
          </ListGroup.Item>
        ))}
      </ListGroup>
    </>
  )
}
