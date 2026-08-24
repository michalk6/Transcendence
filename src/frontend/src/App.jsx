import { useState } from 'react'
import GameMainMenu from './components/GameMainMenu'
import { Game } from './components/Game'


export function App() {
  const [currentView, setCurrentView] = useState('menu')

  // Renders the currently selected view based on the app state
  let content

  switch (currentView) {
    case 'menu':
      content = <GameMainMenu onViewChange={setCurrentView} />
      break
    case 'game':
      content = (
          <Game onViewChange={setCurrentView} />
      )
      break
    default:
      content = <div>Nieznany widok</div>
  }

  return <div>{content}</div>
}