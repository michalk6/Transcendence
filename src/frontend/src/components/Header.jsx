import Container from 'react-bootstrap/Container'
import Navbar from 'react-bootstrap/Navbar'
import Button from 'react-bootstrap/Button'

export default function Header({ onNavigate, user, onLogout, onOpenPanel }) {
  return (
    <Navbar bg="body-tertiary" className="border-bottom px-4 py-2">
      
      <Container fluid>
        
        <Navbar.Brand className="brand-logo" role="button"
        onClick={() => {
            if (onNavigate) {
              onNavigate('home');
            }
            }}
        >
          ULTIMATE.TTT
        </Navbar.Brand>

        <div className="d-flex gap-2 align-items-center">
          {user ? (
            <Button variant="outline-secondary"
              onClick={() => {
                if (onOpenPanel) {
                  onOpenPanel();
                }
              }}
            >
              Menu
            </Button>
          ) : (
            <>
              <Button variant="outline-secondary"
                onClick={() => {
                  if (onNavigate) {
                    onNavigate('login');
                  }
                }}
              >
                Sign in
              </Button>
              <Button className="btn-register"
                onClick={() => {
                  if (onNavigate) {
                    onNavigate('register');
                  }
                }}
              >
                Sign up
              </Button>
            </>
          )}
        </div>

      </Container>

    </Navbar>
  )
}
