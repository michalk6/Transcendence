import { useState } from 'react'
import Offcanvas from 'react-bootstrap/Offcanvas'
import Tab from 'react-bootstrap/Tab'
import Nav from 'react-bootstrap/Nav'
import Button from 'react-bootstrap/Button'
import FriendsTab from './FriendsTab'
import GeneralChat from './GeneralChat'
import GroupRoomList from './GroupRoomList'
import PrivateChat from './PrivateChat'
import GroupChat from './GroupChat'

export default function SidePanel({ show, onHide, user, onLogout }) {
  const [reloadKey, setReloadKey] = useState(0)
  const [activeTab, setActiveTab] = useState('profile')
  const [chatPartner, setChatPartner] = useState(null)
  const [openGroupRoom, setOpenGroupRoom] = useState(null)
  const bump = () => setReloadKey(reloadKey + 1)

  function handleMessage(friend) {
    setChatPartner(friend)
  }

  function handleOpenGroup(room) {
    setOpenGroupRoom({ id: room.id, name: room.name })
    setActiveTab('group')
  }

  let friendsContent = null
  if (chatPartner) {
    friendsContent = (
      <PrivateChat
        otherUserId={chatPartner.id}
        otherUsername={chatPartner.username}
        onBack={() => setChatPartner(null)}
      />
    )
  } else if (user) {
    friendsContent = (
      <FriendsTab
        username={user.username}
        onChanged={bump}
        onMessage={handleMessage}
        reloadKey={reloadKey}
      />
    )
  }

  let groupContent = null
  if (openGroupRoom) {
    groupContent = (
      <GroupChat
        roomId={openGroupRoom.id}
        roomName={openGroupRoom.name}
        onBack={() => setOpenGroupRoom(null)}
      />
    )
  } else if (user) {
    groupContent = (
      <GroupRoomList username={user.username} onOpenRoom={handleOpenGroup} />
    )
  }

  return (
    <Offcanvas show={show} onHide={onHide} placement="end" className="bg-body-tertiary">
      <Offcanvas.Header closeButton closeVariant="white">
        <Offcanvas.Title>{user ? user.username : 'Menu'}</Offcanvas.Title>
      </Offcanvas.Header>

      <Offcanvas.Body>
        {!user ? (
          <p className="text-body-secondary">Sign in to see the panel.</p>
        ) : (
          <Tab.Container activeKey={activeTab} onSelect={(key) => setActiveTab(key)}>
            <Nav
              variant="tabs"
              className="mb-3"
              style={{ display: 'grid', gridTemplateColumns: '1fr 1fr' }}
            >
              <Nav.Item>
                <Nav.Link eventKey="profile" className="text-center">Profile</Nav.Link>
              </Nav.Item>
              <Nav.Item>
                <Nav.Link eventKey="friends" className="text-center">Friends</Nav.Link>
              </Nav.Item>
              <Nav.Item>
                <Nav.Link eventKey="chat" className="text-center">General Chat</Nav.Link>
              </Nav.Item>
              <Nav.Item>
                <Nav.Link eventKey="group" className="text-center">Group Chats</Nav.Link>
              </Nav.Item>
            </Nav>

            <Tab.Content>
              <Tab.Pane eventKey="profile">
                <p className="mb-1">
                  Username: <span className="accent-neon">{user.username}</span>
                </p>
                <Button variant="outline-secondary" className="mt-2" onClick={() => onLogout?.()}>
                  Log out
                </Button>
              </Tab.Pane>

              <Tab.Pane eventKey="friends">
                {friendsContent}
              </Tab.Pane>

              <Tab.Pane eventKey="chat">
                <GeneralChat />
              </Tab.Pane>

              <Tab.Pane eventKey="group">
                {groupContent}
              </Tab.Pane>
            </Tab.Content>
          </Tab.Container>
        )}
      </Offcanvas.Body>
    </Offcanvas>
  )
}
