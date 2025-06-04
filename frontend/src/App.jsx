import { useState, useEffect } from 'react'
import './App.css'

export default function App() {
  const [game, setGame] = useState({ bots: {}, board_size: 5, round: 0 })
  const [newBot, setNewBot] = useState('random_bot')

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws')
    ws.onmessage = (ev) => {
      const data = JSON.parse(ev.data)
      setGame(data)
    }
    return () => ws.close()
  }, [])

  const addBot = async () => {
    await fetch('http://localhost:8000/add_bot', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ bot: newBot })
    })
  }

  const cells = []
  for (let y = 0; y < game.board_size; y++) {
    for (let x = 0; x < game.board_size; x++) {
      const bot = Object.entries(game.bots).find(([, info]) => info.pos[0] === x && info.pos[1] === y)
      cells.push(
        <div key={x + ',' + y} className='cell'>
          {bot ? `${bot[0]} (${bot[1].hp})` : ''}
        </div>
      )
    }
  }

  return (
    <div className='container'>
      <h1>Round {game.round}</h1>
      <div className='board' style={{ gridTemplateColumns: `repeat(${game.board_size}, 40px)` }}>
        {cells}
      </div>
      <div className='controls'>
        <input value={newBot} onChange={e => setNewBot(e.target.value)} />
        <button onClick={addBot}>Add Bot</button>
      </div>
    </div>
  )
}
