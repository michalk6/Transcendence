import { useState } from 'react'
import './GameMainMenu.css'

export default function GameMainMenu({ onViewChange }) {
  const [displayedStatus, setDisplayedStatus] = useState('Oczekiwanie na gracza...')

  const handleStartGame = () => {
    setDisplayedStatus('Szukanie przeciwnika w sieci...')
    if (onViewChange) {
      onViewChange('game')
    }
  }

  return (
    <div className="game-main-menu">
      <h1 className="game-main-menu__title">TRANSCENDENCE</h1>
      <p className="game-main-menu__subtitle">Transcendence</p>

      <div className="game-main-menu__menu-box">
        <button className="game-main-menu__button" onClick={handleStartGame}>
          Graj
        </button>
      </div>

      <div className="game-main-menu__status">
        STATUS: {displayedStatus}
      </div>
    </div>
  )
}
