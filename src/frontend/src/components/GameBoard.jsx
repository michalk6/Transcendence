import { useEffect, useRef, useState } from 'react'
import Button from 'react-bootstrap/Button'
import Alert from 'react-bootstrap/Alert'
import ConfirmModal from './ConfirmModal'
import UserProfile from './UserProfile'
import { refreshAccessToken, triggerAuthExpired } from '../api'

const WIN_LINES = [
  [0, 1, 2], [3, 4, 5], [6, 7, 8],
  [0, 3, 6], [1, 4, 7], [2, 5, 8],
  [0, 4, 8], [2, 4, 6],
]

function findWinningLine(values) {
  for (const line of WIN_LINES) {
    const [a, b, c] = line
    if (values[a] && values[a] === values[b] && values[a] === values[c]) {
      return line
    }
  }
  return null
}

function findLastMove(oldBoard, newBoard) {
  if (!oldBoard) {
    return null
  }
  for (let boardIndex = 0; boardIndex < newBoard.length; boardIndex++) {
    const oldCells = oldBoard[boardIndex].cells
    const newCells = newBoard[boardIndex].cells
    for (let cellIndex = 0; cellIndex < newCells.length; cellIndex++) {
      if (oldCells[cellIndex] !== newCells[cellIndex]) {
        return { boardIndex, cellIndex }
      }
    }
  }
  return null
}

export default function GameBoard({ matchId, mySymbol, userId, onBack }) {
  const [board, setBoard] = useState(null)
  const [currentPlayer, setCurrentPlayer] = useState(null)
  const [nextBoard, setNextBoard] = useState(null)
  const [winner, setWinner] = useState(null)
  const [turnDeadline, setTurnDeadline] = useState(null)
  const [secondsLeft, setSecondsLeft] = useState(null)
  const [error, setError] = useState('')
  const [resultMessage, setResultMessage] = useState('')
  const [showForfeitConfirm, setShowForfeitConfirm] = useState(false)
  const [profileUsername, setProfileUsername] = useState(null)
  const [players, setPlayers] = useState({ X: null, O: null })
  const [lastMove, setLastMove] = useState(null)
  const [reconnectKey, setReconnectKey] = useState(0)
  const socketRef = useRef(null)
  const boardRef = useRef(null)
  const playersRef = useRef({ X: null, O: null })

  const opponentSymbol = mySymbol === 'X' ? 'O' : 'X'
  const opponentJoined = Boolean(players[opponentSymbol])

  function updatePlayers(newPlayers) {
    playersRef.current = newPlayers
    setPlayers(newPlayers)
  }

  function applyBoardState(boardState, deadline) {
    const newLastMove = findLastMove(boardRef.current, boardState.board)
    if (newLastMove) {
      setLastMove(newLastMove)
    }
    boardRef.current = boardState.board
    setBoard(boardState.board)
    setCurrentPlayer(boardState.current_player)
    setNextBoard(boardState.next_board)
    setWinner(boardState.winner)
    setTurnDeadline(deadline)
  }

  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const socket = new WebSocket(
      protocol + '//' + window.location.host + '/ws/games/tictactoe/' + matchId + '/'
    )
    socketRef.current = socket

    socket.onopen = () => {
      if (mySymbol === 'O') {
        socket.send(JSON.stringify({ action: 'join' }))
      }
    }

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'game_state') {
        updatePlayers(data.players)
        applyBoardState(data.board_state, data.turn_deadline)
      } else if (data.type === 'move_result') {
        applyBoardState(data.board_state, data.turn_deadline)
        if (data.detail === 'winner_X' || data.detail === 'winner_O') {
          const winningSymbol = data.detail.slice(-1)
          if (winningSymbol === mySymbol) {
            setResultMessage('You won!')
          } else {
            setResultMessage('You lost.')
          }
        } else if (data.detail === 'draw') {
          setResultMessage("It's a draw.")
        }
      } else if (data.type === 'player_joined') {
        updatePlayers(data.players)
        setCurrentPlayer(data.current_player)
        setTurnDeadline(data.turn_deadline)
      } else if (data.type === 'already_in_match') {
        // already connected as a player, nothing to do
      } else if (data.type === 'user_forfeit') {
        setTurnDeadline(null)
        if (!playersRef.current[opponentSymbol]) {
          setResultMessage('Match cancelled.')
        } else if (data.user_id === userId) {
          setResultMessage('You forfeited. Opponent wins.')
        } else {
          setResultMessage('Opponent forfeited. You win!')
        }
      } else if (data.type === 'error') {
        if (data.code === 'unauthorized') {
          refreshAccessToken().then((refreshResponse) => {
            if (refreshResponse.ok) {
              setReconnectKey((key) => key + 1)
            } else {
              triggerAuthExpired()
            }
          })
        } else {
          setError(data.detail)
        }
      }
    }

    return () => {
      socket.close()
    }
  }, [matchId, reconnectKey])

  useEffect(() => {
    if (!turnDeadline) {
      setSecondsLeft(null)
      return
    }

    function updateSecondsLeft() {
      const remaining = Math.max(0, Math.round(turnDeadline - Date.now() / 1000))
      setSecondsLeft(remaining)
    }

    updateSecondsLeft()
    const interval = setInterval(updateSecondsLeft, 1000)

    return () => {
      clearInterval(interval)
    }
  }, [turnDeadline])

  function handleCellClick(boardIndex, cellIndex) {
    if (!board) {
      return
    }
    socketRef.current.send(JSON.stringify({
      action: 'make_move',
      next_board: boardIndex,
      next_cell: cellIndex,
    }))
  }

  async function handleConfirmForfeit() {
    setShowForfeitConfirm(false)
    socketRef.current.send(JSON.stringify({ action: 'forfeit' }))
  }

  function isCellPlayable(boardIndex, cellIndex, smallBoard) {
    if (!opponentJoined) {
      return false
    }
    if (winner) {
      return false
    }
    if (currentPlayer !== mySymbol) {
      return false
    }
    if (nextBoard !== null && nextBoard !== boardIndex) {
      return false
    }
    if (smallBoard.winner) {
      return false
    }
    if (smallBoard.cells[cellIndex]) {
      return false
    }
    return true
  }

  let errorAlert = null
  if (error) {
    errorAlert = <Alert variant="danger" className="py-2 mb-0">{error}</Alert>
  }

  let resultAlert = null
  if (resultMessage) {
    resultAlert = <Alert variant="warning" className="py-2 mb-0">{resultMessage}</Alert>
  }

  let statusLine = 'Loading…'
  if (board && !opponentJoined) {
    statusLine = 'Waiting for opponent to join…'
  } else if (winner === 'draw') {
    statusLine = 'Game over - draw'
  } else if (winner) {
    statusLine = 'Game over - ' + winner + ' won'
  }

  let turnSwitch = null
  if (board && opponentJoined && !winner) {
    const isMyTurn = currentPlayer === mySymbol
    const opponent = players[opponentSymbol]
    const myName = 'YOU'
    let opponentLabel = <span className="turn-switch-name">?</span>
    if (opponent) {
      opponentLabel = (
        <button
          type="button"
          className="turn-switch-name turn-switch-link"
          onClick={() => setProfileUsername(opponent.username)}
        >
          {opponent.username}
        </button>
      )
    }
    turnSwitch = (
      <div className="turn-switch">
        <div className={'turn-switch-side' + (isMyTurn ? ' turn-switch-active' : '')}>
          <span className="turn-switch-name">{myName}</span> ({mySymbol})
        </div>
        <div className="turn-switch-vs">vs</div>
        <div className={'turn-switch-side' + (!isMyTurn ? ' turn-switch-active' : '')}>
          {opponentLabel} ({opponentSymbol})
        </div>
      </div>
    )
  }

  let timerBox = null
  if (secondsLeft !== null && !winner) {
    let timerBoxClass = 'timer-box'
    if (secondsLeft <= 10) {
      timerBoxClass += ' timer-box-urgent'
    }
    timerBox = <div className={timerBoxClass}>{secondsLeft}s</div>
  }

  let boardContent = null
  if (board) {
    let boardWinningLine = null
    if (winner && winner !== 'draw') {
      boardWinningLine = findWinningLine(board.map((smallBoard) => smallBoard.winner))
    }

    boardContent = (
      <div className="ultimate-board">
        {board.map((smallBoard, boardIndex) => {
          let smallBoardClass = 'small-board'
          let isActiveBoard = nextBoard === boardIndex
          if (nextBoard === null && !smallBoard.winner) {
            isActiveBoard = true
          }
          if (isActiveBoard && !winner) {
            smallBoardClass += ' small-board-active'
          }
          if (smallBoard.winner) {
            smallBoardClass += ' small-board-finished'
          }
          if (boardWinningLine && boardWinningLine.includes(boardIndex)) {
            smallBoardClass += winner === mySymbol ? ' small-board-win-mine' : ' small-board-win-opponent'
          }

          let smallBoardWinningLine = null
          if (smallBoard.winner && smallBoard.winner !== 'draw') {
            smallBoardWinningLine = findWinningLine(smallBoard.cells)
          }

          return (
            <div key={boardIndex} className={smallBoardClass}>
              {smallBoard.cells.map((cellValue, cellIndex) => {
                let cellClass = 'board-cell'
                if (smallBoardWinningLine && smallBoardWinningLine.includes(cellIndex)) {
                  cellClass += smallBoard.winner === mySymbol ? ' board-cell-win-mine' : ' board-cell-win-opponent'
                }
                if (lastMove && lastMove.boardIndex === boardIndex && lastMove.cellIndex === cellIndex) {
                  cellClass += ' board-cell-last-move'
                }
                return (
                  <button
                    key={cellIndex}
                    type="button"
                    className={cellClass}
                    disabled={!isCellPlayable(boardIndex, cellIndex, smallBoard)}
                    onClick={() => handleCellClick(boardIndex, cellIndex)}
                  >
                    {cellValue}
                  </button>
                )
              })}
            </div>
          )
        })}
      </div>
    )
  }

  return (
    <div className="d-flex flex-column align-items-center">
      <div className="d-flex justify-content-between w-100 mb-3">
        <Button variant="outline-secondary" size="sm" onClick={onBack}>
          ← Back to lobby
        </Button>
        {!winner && !resultMessage && board && (
          <Button
            variant="outline-danger"
            size="sm"
            onClick={() => setShowForfeitConfirm(true)}
          >
            {opponentJoined ? 'Forfeit' : 'Cancel match'}
          </Button>
        )}
      </div>

      <div className="text-body-secondary small">Match #{matchId}</div>

      {turnSwitch ? (
        <div className="d-flex align-items-center gap-2 mb-1">
          {turnSwitch}
          {timerBox}
        </div>
      ) : (
        <div className="fs-5 fw-bold mb-1">{statusLine}</div>
      )}

      {resultAlert}
      {errorAlert}

      {boardContent}

      <ConfirmModal
        show={showForfeitConfirm}
        title={opponentJoined ? 'Forfeit match' : 'Cancel match'}
        body={
          opponentJoined
            ? <p>Give up this match? The other player will win.</p>
            : <p>Cancel this match? Nobody has joined yet.</p>
        }
        confirmLabel={opponentJoined ? 'Forfeit' : 'Cancel match'}
        onConfirm={handleConfirmForfeit}
        onCancel={() => setShowForfeitConfirm(false)}
      />

      <UserProfile
        username={profileUsername}
        onClose={() => setProfileUsername(null)}
      />
    </div>
  )
}
