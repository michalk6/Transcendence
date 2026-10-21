import { useEffect, useState } from 'react'
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import Spinner from 'react-bootstrap/Spinner'
import Home from './pages/Home'
import Game from './pages/Game'
import Login from './pages/Login'
import Register from './pages/Register'
import NotFound from './pages/NotFound'
import { getCsrfToken } from './csrf'

export function App() {
  const routerNavigate = useNavigate()

  const [user, setUser] = useState(null)
  const [checkingSession, setCheckingSession] = useState(true)

  useEffect(() => {
    async function checkSession() {
      const response = await fetch('/api/users/me/')
      if (response.ok) {
        const data = await response.json()
        setUser(data)
      }
      setCheckingSession(false)
    }
    checkSession()
  }, [])

  async function handleLogout() {
    await fetch('/api/auth/logout/', {
      method: 'POST',
      headers: { 'X-CSRFToken': getCsrfToken() },
    })
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
    routerNavigate('/', { replace: true })
  }

  if (checkingSession) {
    return (
      <div className="d-flex flex-column align-items-center justify-content-center" style={{ minHeight: '100vh' }}>
        <Spinner animation="border" className="accent-neon mb-3" />
        <span className="text-body-secondary">Loading…</span>
      </div>
    )
  }

  return (
    <Routes>
      <Route
        path="/"
        element={<Home onNavigate={navigate} user={user} onLogout={handleLogout} />}
      />
      <Route
        path="/login"
        element={user ? <Navigate to="/" replace /> : <Login onNavigate={navigate} onAuthed={goHome} />}
      />
      <Route
        path="/register"
        element={user ? <Navigate to="/" replace /> : <Register onNavigate={navigate} onAuthed={goHome} />}
      />
      <Route
        path="/game"
        element={
          user ? (
            <Game onNavigate={navigate} user={user} onLogout={handleLogout} />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
      <Route path="*" element={<NotFound onNavigate={navigate} user={user} />} />
    </Routes>
  )
}
