import { useState } from 'react'
import Container from 'react-bootstrap/Container'
import Card from 'react-bootstrap/Card'
import Button from 'react-bootstrap/Button'

import Header from '../components/Header'
import Footer from '../components/Footer'
import SidePanel from '../components/SidePanel'
import GameLobby from '../components/GameLobby'
import GameBoard from '../components/GameBoard'

export default function Game({ onNavigate, user, onLogout, onUserUpdated }) {
  const [panelOpen, setPanelOpen] = useState(false)
  const [selectedMatch, setSelectedMatch] = useState(null)

  let gameContent = null
  if (selectedMatch) {
    gameContent = (
      <Card bg="body-tertiary">
        <Card.Body>
          <GameBoard
            matchId={selectedMatch.id}
            mySymbol={selectedMatch.mySymbol}
            userId={user.id}
            onBack={() => setSelectedMatch(null)}
          />
        </Card.Body>
      </Card>
    )
  } else {
    gameContent = (
      <Card bg="body-tertiary" style={{ minWidth: '400px' }}>
        <Card.Body>
          <GameLobby
            userId={user.id}
            onSelectMatch={(id, mySymbol) => setSelectedMatch({ id, mySymbol })}
          />
        </Card.Body>
      </Card>
    )
  }

  return (
    <>
      <Header onNavigate={onNavigate} user={user} onOpenPanel={() => setPanelOpen(true)} />

      <SidePanel
        show={panelOpen}
        onHide={() => setPanelOpen(false)}
        user={user}
        onLogout={onLogout}
        onUserUpdated={onUserUpdated}
      />

      <Container className="py-4 d-flex flex-column align-items-center">
        <Button
          variant="outline-secondary" className="align-self-start mb-3"
          onClick={() => onNavigate?.('home')}
        >
          ← Back
        </Button>

        {gameContent}
      </Container>

      <Footer />
    </>
  )
}
