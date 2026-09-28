import { useState } from 'react'
import Button from 'react-bootstrap/Button'
import ListGroup from 'react-bootstrap/ListGroup'
import Alert from 'react-bootstrap/Alert'

export default function BlocklistTab({ reloadKey, onChanged }) {
  const [blocked] = useState([])
  const [error] = useState('')

  let errorAlert = null
  if (error) {
    errorAlert = <Alert variant="danger" className="py-2">{error}</Alert>
  }

  return (
    <>
      {errorAlert}

      <div className="text-body-secondary mb-1">Blocked ({blocked.length})</div>
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
            <Button size="sm" variant="outline-secondary">
              Unblock
            </Button>
          </ListGroup.Item>
        ))}
      </ListGroup>
    </>
  )
}
