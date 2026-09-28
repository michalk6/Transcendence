import Container from 'react-bootstrap/Container'
import Row from 'react-bootstrap/Row'
import Col from 'react-bootstrap/Col'
import Card from 'react-bootstrap/Card'
import Header from './Header'
import Footer from './Footer'

export default function AuthCard({ title, onNavigate, footer, children }) {
  return (
    <>
      <Header onNavigate={onNavigate} />

      <Container className="py-5">
        <Row className="justify-content-center">
          <Col md={6} lg={5}>
            <Card bg="body-secondary">
              <Card.Body className="p-4">
                <Card.Title className="mb-4 fs-4">{title}</Card.Title>
                {children}
                {footer && (
                  <p className="text-body-secondary mt-3 mb-0 text-center">{footer}</p>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>

      <Footer />
    </>
  )
}
