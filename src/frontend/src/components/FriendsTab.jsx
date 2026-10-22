import { useState } from 'react'
import Form from 'react-bootstrap/Form'
import Button from 'react-bootstrap/Button'
import ListGroup from 'react-bootstrap/ListGroup'
import Alert from 'react-bootstrap/Alert'
import Pagination from 'react-bootstrap/Pagination'

const RESULTS_PAGE_SIZE = 10

export default function FriendsTab({ username, onChanged }) {
  const [friends] = useState([])
  const [requests] = useState([])
  const [term, setTerm] = useState('')
  const [results, setResults] = useState([])
  const [resultsPage, setResultsPage] = useState(1)
  const [resultsCount, setResultsCount] = useState(0)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const totalResultsPages = Math.ceil(resultsCount / RESULTS_PAGE_SIZE)

  async function fetchResultsPage(pageNumber) {
    const params = new URLSearchParams({
      q: term,
      page_size: RESULTS_PAGE_SIZE,
      page: pageNumber,
    })
    const response = await fetch('/api/users/search/?' + params)
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

  return (
    <>
      {messageAlert}
      {errorAlert}

      <Form onSubmit={handleSearch} className="d-flex gap-2 mb-2">
        <Form.Control
          size="sm"
          placeholder="Search for a user…"
          value={term}
          onChange={(event) => setTerm(event.target.value)}
        />
        <Button size="sm" type="submit" variant="outline-secondary">
          Search
        </Button>
      </Form>

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
                <Button size="sm" className="btn-register">
                  Add
                </Button>
              </ListGroup.Item>
            ))}
          </ListGroup>
        </>
      )}

      {requests.length > 0 && (
        <>
          <div className="text-body-secondary mb-1">
            Friend requests ({requests.length})
          </div>
          <ListGroup className="mb-3">
            {requests.map((request) => (
              <ListGroup.Item
                key={request.id}
                className="d-flex justify-content-between align-items-center"
              >
                <span>{request.username}</span>
                <span className="d-flex gap-2">
                  <Button size="sm" className="btn-register">
                    Accept
                  </Button>
                  <Button size="sm" variant="outline-secondary">
                    Decline
                  </Button>
                </span>
              </ListGroup.Item>
            ))}
          </ListGroup>
        </>
      )}

      <div className="text-body-secondary mb-1">Your friends ({friends.length})</div>
      <ListGroup>
        {friends.length === 0 && (
          <ListGroup.Item className="text-body-secondary">
            No friends yet.
          </ListGroup.Item>
        )}
        {friends.map((friend) => (
          <ListGroup.Item
            key={friend.id}
            className="d-flex justify-content-between align-items-center"
          >
            <span>{friend.username}</span>
            <span className="d-flex gap-2">
              <Button size="sm" variant="outline-secondary">
                Remove
              </Button>
              <Button size="sm" variant="outline-danger">
                Block
              </Button>
            </span>
          </ListGroup.Item>
        ))}
      </ListGroup>
    </>
  )
}
