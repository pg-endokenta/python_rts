import { useState, useEffect } from 'react'
import './App.css'

export default function App() {
  const [game, setGame] = useState({ bots: {}, board_size: 20, round: 0 })
  const [newBot, setNewBot] = useState('random_bot')
  const [apiStatus, setApiStatus] = useState('')

  // remove trailing slash so fetch(`${apiBase}/foo`) doesn't produce //foo
  const rawApiBase = import.meta.env.VITE_API_URL || ''
  const apiBase = rawApiBase.replace(/\/+$/, '')

  useEffect(() => {
    const wsUrl = apiBase
      ? apiBase.replace(/^http/, 'ws') + '/ws'
      : `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/ws`
    const ws = new WebSocket(wsUrl)
    ws.onmessage = (ev) => {
      const data = JSON.parse(ev.data)
      console.debug('ws message', data)
      setGame(data)
    }
    return () => ws.close()
  }, [apiBase])

  const checkApi = async () => {
    try {
      const res = await fetch(`${apiBase}/health`)
      setApiStatus(res.ok ? 'ok' : 'error')
      console.debug('health check', res.status)
    } catch (err) {
      console.error('health check failed', err)
      setApiStatus('error')
    }
  }

  useEffect(() => {
    checkApi()
  }, [apiBase])

  const addBot = async () => {
    try {
      const res = await fetch(`${apiBase}/add_bot`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ bot: newBot })
      })
      console.debug('add bot response', res.status)
      if (!res.ok) {
        console.error('failed to add bot', await res.text())
      }
    } catch (err) {
      console.error('add bot failed', err)
    }
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
        <button onClick={checkApi}>Check API</button>
        <span className='status'>API: {apiStatus}</span>
      </div>
    </div>
  )
}
