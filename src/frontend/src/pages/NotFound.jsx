import Container from 'react-bootstrap/Container'
import Card from 'react-bootstrap/Card'
import Button from 'react-bootstrap/Button'

import Header from '../components/Header'
import Footer from '../components/Footer'

export default function NotFound({ onNavigate, user }) {
  return (
    <>
      <Header onNavigate={onNavigate} user={user} />

      <Container className="py-5 d-flex justify-content-center">
        <Card bg="body-tertiary" className="text-center p-4">
          <Card.Body>
            <Card.Title className="fs-1 accent-neon">404</Card.Title>
            <Card.Text className="text-body-secondary mb-3">
              This page doesn't exist.
            </Card.Text>
            <Button
              className="btn-register"
              onClick={() => {
                if (onNavigate) {
                  onNavigate('home')
                }
              }}
            >
              Back to home
            </Button>
          </Card.Body>
        </Card>
      </Container>

      <Footer />
    </>
  )
}
