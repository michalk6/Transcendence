import Offcanvas from 'react-bootstrap/Offcanvas'
import Tab from 'react-bootstrap/Tab'
import Tabs from 'react-bootstrap/Tabs'
import Button from 'react-bootstrap/Button'
import FriendsTab from './FriendsTab'
import BlocklistTab from './BlocklistTab'

export default function SidePanel({ show, onHide, user, onLogout }) {
  return (
    <Offcanvas show={show} onHide={onHide} placement="end" className="bg-body-tertiary">
      <Offcanvas.Header closeButton closeVariant="white">
        <Offcanvas.Title>{user ? user.username : 'Menu'}</Offcanvas.Title>
      </Offcanvas.Header>

      <Offcanvas.Body>
        {!user ? (
          <p className="text-body-secondary">Sign in to see the panel.</p>
        ) : (
          <Tabs defaultActiveKey="profile" className="mb-3" justify>
            <Tab eventKey="profile" title="Profile">
              <p className="mb-1">
                Username: <span className="accent-neon">{user.username}</span>
              </p>
              <Button variant="outline-secondary" className="mt-2" onClick={() => onLogout?.()}>
                Log out
              </Button>
            </Tab>

            <Tab eventKey="friends" title="Friends">
              <FriendsTab username={user.username} />
            </Tab>

            <Tab eventKey="blocked" title="Blocked">
              <BlocklistTab />
            </Tab>

            <Tab eventKey="chat" title="Chat">
              <p className="text-body-secondary">Chat is coming soon.</p>
            </Tab>
          </Tabs>
        )}
      </Offcanvas.Body>
    </Offcanvas>
  )
}
