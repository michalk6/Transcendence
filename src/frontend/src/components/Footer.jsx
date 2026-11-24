import Container from 'react-bootstrap/Container'
import { Link } from 'react-router-dom'

export default function Footer() {
  return (
    <footer className="bg-body-tertiary border-top mt-auto py-3 text-center text-body-secondary">
      <Container fluid className="d-flex flex-wrap justify-content-center gap-3">
        <span>&copy; {new Date().getFullYear()} ft_transcendence</span>
        <Link className="text-body-secondary" to="/privacy">Privacy Policy</Link>
        <Link className="text-body-secondary" to="/terms">Terms of Service</Link>
      </Container>
    </footer>
  )
}
