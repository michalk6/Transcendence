import { useEffect, useRef, useState } from 'react'
import ListGroup from 'react-bootstrap/ListGroup'
import Button from 'react-bootstrap/Button'
import Alert from 'react-bootstrap/Alert'
import Pagination from 'react-bootstrap/Pagination'
import { getCsrfToken } from '../csrf'
import { apiFetch } from '../api'
import UserProfile from './UserProfile'

const MATCHES_PAGE_SIZE = 10

export default function GameLobby({ userId, onSelectMatch }) {
  const [matches, setMatches] = useState([])
  const [matchesPage, setMatchesPage] = useState(1)
  const [matchesCount, setMatchesCount] = useState(0)
  const [myMatch, setMyMatch] = useState(null)
  const [error, setError] = useState('')
  const [profileUsername, setProfileUsername] = useState(null)
  const socketRef = useRef(null)

  const totalMatchesPages = Math.ceil(matchesCount / MATCHES_PAGE_SIZE)

  async function fetchMatches(pageNumber) {
    const params = new URLSearchParams({
      page_size: MATCHES_PAGE_SIZE,
      page: pageNumber,
    })
    const response = await apiFetch('/api/games/tic_tac_toe_ultimate/matches/?' + params)
    if (!response.ok) {
      setError('Could not load matches.')
      return
    }
    const data = await response.json()
    setMatches(data.results.filter((match) => match.player_x !== userId))
    setMatchesCount(data.count)
    setMatchesPage(pageNumber)
  }

  async function fetchMyMatch() {
    const response = await apiFetch('/api/games/tic_tac_toe_ultimate/matches/?mine=true')
    if (!response.ok) {
      return
    }
    const data = await response.json()
    setMyMatch(data.results[0] || null)
  }

  useEffect(() => {
    fetchMatches(1)
    fetchMyMatch()

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const socket = new WebSocket(protocol + '//' + window.location.host + '/ws/games/tictactoe/lobby/')
    socketRef.current = socket

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'matches_updated') {
        fetchMatches(1)
        fetchMyMatch()
      }
    }

    return () => {
      socket.close()
    }
  }, [])

  async function handleCreateMatch() {
    setError('')

    const response = await apiFetch('/api/games/tic_tac_toe_ultimate/matches/', {
      method: 'POST',
      headers: { 'X-CSRFToken': getCsrfToken() },
    })

    if (!response.ok) {
      const data = await response.json()
      if (data.detail) {
        setError(data.detail)
      } else {
        setError('Could not create match.')
      }
      return
    }

    const data = await response.json()
    onSelectMatch(data.id, 'X')
  }

  let errorAlert = null
  if (error) {
    errorAlert = <Alert variant="danger" className="py-2">{error}</Alert>
  }

  let myMatchContent = null
  if (myMatch) {
    const mySymbol = myMatch.player_x === userId ? 'X' : 'O'
    let actionLabel = 'Resume match'
    if (myMatch.status === 'waiting') {
      actionLabel = 'Resume (waiting for opponent)'
    }
    myMatchContent = (
      <ListGroup className="mb-3">
        <ListGroup.Item className="d-flex justify-content-between align-items-center">
          <span>Match #{myMatch.id} - your active match</span>
          <Button
            size="sm"
            className="btn-register ms-3"
            onClick={() => onSelectMatch(myMatch.id, mySymbol)}
          >
            {actionLabel}
          </Button>
        </ListGroup.Item>
      </ListGroup>
    )
  }

  let matchesPagination = null
  if (totalMatchesPages > 1) {
    matchesPagination = (
      <Pagination size="sm" className="mb-2 justify-content-center">
        <Pagination.Prev
          disabled={matchesPage <= 1}
          onClick={() => fetchMatches(matchesPage - 1)}
        />
        <Pagination.Item disabled>
          {matchesPage} / {totalMatchesPages}
        </Pagination.Item>
        <Pagination.Next
          disabled={matchesPage >= totalMatchesPages}
          onClick={() => fetchMatches(matchesPage + 1)}
        />
      </Pagination>
    )
  }

  let matchesContent = null
  if (matches.length === 0) {
    if (!myMatch) {
      matchesContent = <p className="text-body-secondary">No open matches. Create one!</p>
    }
  } else {
    matchesContent = (
      <ListGroup className="mb-3">
        {matches.map((match) => (
          <ListGroup.Item
            key={match.id}
            className="d-flex justify-content-between align-items-center"
          >
            <span>
              Match #{match.id} (
              <Button
                variant="link"
                className="p-0 border-0 text-decoration-none username-truncate"
                onClick={() => setProfileUsername(match.player_x_username)}
              >
                {match.player_x_username}
              </Button>
              )
            </span>
            <Button
              size="sm"
              className="btn-register"
              disabled={Boolean(myMatch)}
              onClick={() => onSelectMatch(match.id, 'O')}
            >
              Join
            </Button>
          </ListGroup.Item>
        ))}
      </ListGroup>
    )
  }

  return (
    <div>
      {errorAlert}

      <Button
        className="btn-register mb-3"
        disabled={Boolean(myMatch)}
        onClick={handleCreateMatch}
      >
        Create match
      </Button>

      {myMatchContent}
      {matchesContent}
      {matchesPagination}

      <UserProfile
        username={profileUsername}
        onClose={() => setProfileUsername(null)}
      />
    </div>
  )
}
