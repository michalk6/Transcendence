import './Game.css'

export function Game({ onViewChange }) {
  return (
    <div className="game-screen">
      <h2 className="game-screen__title">TRANSCENDENCE</h2>
      <h3 className="game-screen__subtitle">Gra jeszcze się ładuje...</h3>
      <button className="game-screen__button" onClick={() => onViewChange('menu')}>
        Powrót do menu
      </button>
    </div>
  )
}