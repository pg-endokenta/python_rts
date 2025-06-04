"""Simple HTTP server for the Python RTS arena using FastAPI.

This server keeps the game running indefinitely. Clients can query the
current game state and add bots at runtime.
"""

import asyncio
import importlib.util
from pathlib import Path
from typing import Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from arena import Game, load_bots


class PersistentGame(Game):
    """Game that can run indefinitely one step at a time."""

    def step(self) -> None:
        """Run a single turn for all alive bots."""
        if sum(info['hp'] > 0 for info in self.bots.values()) <= 1:
            # Nothing to do if only one bot (or none) is alive
            return
        for name, info in list(self.bots.items()):
            if info['hp'] <= 0:
                continue
            state = {
                'self_hp': info['hp'],
                'self_pos': self.positions[name],
                'board_size': self.board_size,
                'enemies': {
                    n: {'hp': i['hp'], 'pos': self.positions[n]}
                    for n, i in self.bots.items()
                    if n != name and i['hp'] > 0
                },
            }
            if not state['enemies']:
                continue
            try:
                action = info['bot'].act(state)
            except Exception:
                continue
            self._handle_action(name, action)

    def get_state(self) -> Dict[str, Dict[str, int]]:
        """Return a JSON serialisable state."""
        return {
            name: {
                'hp': info['hp'],
                'pos': self.positions[name],
            }
            for name, info in self.bots.items()
        }


game: Optional[PersistentGame] = None

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=['*'])


@app.on_event('startup')
async def startup():
    global game
    bots = load_bots('bots')
    game = PersistentGame(bots)
    asyncio.create_task(game_loop())


async def game_loop():
    while True:
        await asyncio.sleep(1)
        game.step()


@app.get('/state')
async def state():
    return game.get_state()


@app.post('/bots/{bot_file}')
async def add_bot(bot_file: str):
    """Add a new bot by filename from the bots directory."""
    file_path = Path('bots') / f'{bot_file}.py'
    if not file_path.exists():
        raise HTTPException(status_code=404, detail='Bot not found')
    spec = importlib.util.spec_from_file_location(bot_file, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, 'Bot'):
        raise HTTPException(status_code=400, detail='No Bot class in file')
    bot = module.Bot()
    if not hasattr(bot, 'name'):
        bot.name = bot_file
    game.bots[bot.name] = {'bot': bot, 'hp': 10}
    # Place at random position avoiding collisions
    existing = set(game.positions.values())
    for x in range(game.board_size):
        for y in range(game.board_size):
            if (x, y) not in existing:
                game.positions[bot.name] = (x, y)
                return {'status': 'ok'}
    raise HTTPException(status_code=400, detail='Board full')

