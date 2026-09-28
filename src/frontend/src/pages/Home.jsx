import { useState } from 'react'
import Container from 'react-bootstrap/Container'
import Row from 'react-bootstrap/Row'
import Col from 'react-bootstrap/Col'
import Card from 'react-bootstrap/Card'
import Button from 'react-bootstrap/Button'

// OWN COMPONENTS
import Header from '../components/Header'
import Footer from '../components/Footer'
import SidePanel from '../components/SidePanel'

export default function Home({ onNavigate, user, onLogout }) {
  const [panelOpen, setPanelOpen] = useState(false)

  return (
    <>
      <Header onNavigate={onNavigate} user={user} onOpenPanel={() => setPanelOpen(true)}/>

      <SidePanel show={panelOpen} onHide={() => setPanelOpen(false)} user={user} onLogout={onLogout}/>

      <Container fluid className="py-4">
        <Row className="g-4">
          <Col lg={3}>
            <Card bg="body-tertiary" className="h-100">
              <Card.Body>
                <Card.Title>Player Profile</Card.Title>
                {user ? (
                  <Card.Text className="mt-2">
                    Signed in as <span className="accent-neon">{user.username}</span>
                  </Card.Text>
                ) : (
                  <Card.Text className="text-body-secondary mt-2">
                    Sign in to save your stats and climb the ranks.
                  </Card.Text>
                )}
              </Card.Body>
            </Card>
          </Col>

          <Col lg={6}>
            <Card bg="body-tertiary" className="h-100">
              <Card.Body className="d-flex flex-column align-items-center justify-content-center text-center">
                <Button
                  className="btn-register px-5 py-3 fs-4"
                  onClick={() => onNavigate?.('game')}
                >
                  Play
                </Button>
              </Card.Body>
            </Card>
          </Col>

          <Col lg={3}>
            <Card bg="body-tertiary" className="h-100">
              <Card.Body>
                <Card.Title>Top 3 Ranking</Card.Title>
                <ol className="text-body-secondary mt-2 ps-3">
                  {/* <li>
                    <span className="text-body">CyberGamer</span> — 2100 ELO
                  </li>
                  <li>
                    <span className="text-body">TicTacKing</span> — 1980 ELO
                  </li>
                  <li>
                    <span className="text-body">Anonymous</span> — 1850 ELO
                  </li> */}
                </ol>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>

      <Footer />
    </>
  )
}
