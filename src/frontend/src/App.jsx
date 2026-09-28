import { useState } from 'react'
import { Routes, Route, useNavigate } from 'react-router-dom'
import Home from './pages/Home'
import Game from './pages/Game'
import Login from './pages/Login'
import Register from './pages/Register'

export function App() {
  const routerNavigate = useNavigate()

  const [user, setUser] = useState(null)

  function handleLogout() {
    setUser(null)
    routerNavigate('/')
  }

  function navigate(view) {
    if (view === 'home') {
      routerNavigate('/')
    } else {
      routerNavigate('/' + view)
    }
  }

  function goHome(nextUser) {
    if (nextUser) {
      setUser(nextUser)
    }
    routerNavigate('/')
  }

  return (
    <Routes>
      <Route
        path="/"
        element={<Home onNavigate={navigate} user={user} onLogout={handleLogout} />}
      />
      <Route path="/login" element={<Login onNavigate={navigate} onAuthed={goHome} />} />
      <Route path="/register" element={<Register onNavigate={navigate} onAuthed={goHome} />} />
      <Route path="/game" element={<Game onNavigate={navigate} user={user} />} />
    </Routes>
  )
}
