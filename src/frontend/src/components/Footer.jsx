import Container from 'react-bootstrap/Container'

export default function Footer() {
  return (
    <footer className="bg-body-tertiary border-top mt-auto py-3 text-center text-body-secondary">
      <Container fluid className="d-flex flex-wrap justify-content-center gap-3">
        <span>&copy; {new Date().getFullYear()} ft_transcendence</span>
        <a className="text-body-secondary" href="#">Privacy Policy</a>
        <a className="text-body-secondary" href="#">Terms of Service</a>
      </Container>
    </footer>
  )
}
