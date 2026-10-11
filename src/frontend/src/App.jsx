import { useState } from 'react'
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import Home from './pages/Home'
import Game from './pages/Game'
import Login from './pages/Login'
import Register from './pages/Register'

export function App() {
  const routerNavigate = useNavigate()

  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('user')
    return saved ? JSON.parse(saved) : null
  })
  const [accessToken, setAccessToken] = useState(() => localStorage.getItem('accessToken'))

  function handleLogout() {
    setUser(null)
    setAccessToken(null)
    localStorage.removeItem('user')
    localStorage.removeItem('accessToken')
    routerNavigate('/')
  }

  function navigate(view) {
    if (view === 'home') {
      routerNavigate('/')
    } else {
      routerNavigate('/' + view)
    }
  }

  function goHome(nextUser, nextToken) {
    if (nextUser) {
      setUser(nextUser)
      localStorage.setItem('user', JSON.stringify(nextUser))
    }
    if (nextToken) {
      setAccessToken(nextToken)
      localStorage.setItem('accessToken', nextToken)
    }
    routerNavigate('/', { replace: true })
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
    </Routes>
  )
}
