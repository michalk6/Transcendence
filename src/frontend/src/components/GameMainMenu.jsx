import { useState } from 'react'

export default function GameMainMenu({ onViewChange }) {
  const [displayedStatus, setDisplayedStatus] = useState('Oczekiwanie na gracza...')

  const handleStartGame = () => {
    setDisplayedStatus('Szukanie przeciwnika w sieci...')
    if (onViewChange) {
      onViewChange('game')
    }
  }

  const wrapperClass = "min-h-screen flex flex-col items-center justify-center gap-6 bg-[#0a0a16] text-[#00ffcc] px-6 py-10"
  const titleClass = "text-3xl uppercase text-[#ff0055]"
  const subtitleClass = "text-base text-[#00ffcc]"
  const buttonClass = "rounded border-2 border-[#00ffcc] px-6 py-3 text-lg uppercase text-[#00ffcc] transition hover:bg-[#00ffcc] hover:text-[#0a0a16]"
  const statusClass = "text-sm text-[#ffff00]"

  return (
    <div className={wrapperClass}>
      <h1 className={titleClass}>TRANSCENDENCE</h1>
      <p className={subtitleClass}>Transcendence</p>

      <div className="flex w-full max-w-xs justify-center">
        <button className={buttonClass} onClick={handleStartGame}>
          Graj
        </button>
      </div>

      <div className={statusClass}>
        STATUS: {displayedStatus}
      </div>
    </div>
  )
}
