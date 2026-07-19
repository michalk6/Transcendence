export function Game({ onViewChange }) {
  const wrapperClass = "min-h-screen flex flex-col items-center justify-center gap-6 bg-[#0a0a16] text-[#00ffcc] px-6 py-10"
  const titleClass = "text-3xl uppercase tracking-[0.3em] text-[#ff0055] drop-shadow-[0_0_12px_#ff0055]"
  const subtitleClass = "text-base text-[#ffff00] drop-shadow-[0_0_5px_#ffff00]"
  const buttonClass = "mt-6 rounded border-2 border-[#00ffcc] px-5 py-3 text-sm uppercase transition hover:bg-[#00ffcc] hover:text-[#0a0a16]"

  return (
    <div className={wrapperClass}>
      <h2 className={titleClass}>TRANSCENDENCE</h2>
      <h3 className={subtitleClass}>Gra jeszcze się ładuje...</h3>
      <button className={buttonClass} onClick={() => onViewChange('menu')}>
        Powrót do menu
      </button>
    </div>
  )
}