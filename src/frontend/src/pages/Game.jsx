import Container from 'react-bootstrap/Container'
import Card from 'react-bootstrap/Card'
import Button from 'react-bootstrap/Button'

import Header from '../components/Header'
import Footer from '../components/Footer'

export default function Game({ onNavigate, user }) {
  return (
    <>
      <Header onNavigate={onNavigate} user={user} />

      <Container className="py-4 d-flex flex-column align-items-center">
        <Button
          variant="outline-secondary" className="align-self-start mb-3"
          onClick={() => onNavigate?.('home')}
        >
          ← Back
        </Button>

        <Card bg="body-tertiary">
          <Card.Body className="d-flex flex-column align-items-center text-center">
            <div className="fs-5 fw-bold mb-3">
              Turn: <span className="accent-neon">Player X</span>
            </div>
            <div className="board-placeholder">
              {Array.from({ length: 9 }).map((_, index) => (
                <div key={index} className="sub-board" />
              ))}
            </div>
            <p className="text-body-secondary mt-3">The board will appear here.</p>
          </Card.Body>
        </Card>
      </Container>

      <Footer />
    </>
  )
}
