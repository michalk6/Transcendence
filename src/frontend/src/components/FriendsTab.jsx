import { useState } from 'react'
import Form from 'react-bootstrap/Form'
import Button from 'react-bootstrap/Button'
import ListGroup from 'react-bootstrap/ListGroup'
import Alert from 'react-bootstrap/Alert'

export default function FriendsTab({ username, onChanged }) {
  const [friends] = useState([])
  const [requests] = useState([])
  const [term, setTerm] = useState('')
  const [results] = useState([])
  const [message, setMessage] = useState('')
  const [error] = useState('')

  function handleSearch(event) {
    event.preventDefault()
    // TODO: searchUsers
    setMessage('Search will be available once the API is connected.')
  }

  let messageAlert = null
  if (message) {
    messageAlert = <Alert variant="success" className="py-2">{message}</Alert>
  }

  let errorAlert = null
  if (error) {
    errorAlert = <Alert variant="danger" className="py-2">{error}</Alert>
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
        <ListGroup className="mb-3">
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
