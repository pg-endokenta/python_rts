import asyncio
import importlib.util
import random
from pathlib import Path
from typing import Dict, Tuple, Any, Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


class BotWrapper:
    def __init__(self, bot):
        self.bot = bot
        self.hp = 10


class WebGame:
    def __init__(self, board_size: int = 5):
        self.board_size = board_size
        self.bots: Dict[str, BotWrapper] = {}
        self.positions: Dict[str, Tuple[int, int]] = {}
        self.round_no = 0
        self._lock = asyncio.Lock()

    def _distance(self, a: Tuple[int, int], b: Tuple[int, int]) -> int:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def _random_position(self) -> Tuple[int, int]:
        while True:
            pos = (
                random.randrange(self.board_size),
                random.randrange(self.board_size),
            )
            if pos not in self.positions.values():
                return pos

    async def add_bot(self, bot: Any):
        async with self._lock:
            name = getattr(bot, "name", bot.__class__.__name__)
            if name in self.bots:
                # ensure unique name by appending number
                i = 1
                while f"{name}_{i}" in self.bots:
                    i += 1
                name = f"{name}_{i}"
                bot.name = name
            self.bots[name] = BotWrapper(bot)
            self.positions[name] = self._random_position()

    async def _handle_action(self, name: str, action: Tuple[str, Any]):
        if not isinstance(action, tuple) or len(action) != 2:
            return
        kind, arg = action
        if kind == "move":
            dir_map = {
                "up": (0, -1),
                "down": (0, 1),
                "left": (-1, 0),
                "right": (1, 0),
            }
            if arg not in dir_map:
                return
            dx, dy = dir_map[arg]
            x, y = self.positions[name]
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.board_size and 0 <= ny < self.board_size:
                if not any(
                    self.positions[n] == (nx, ny) and self.bots[n].hp > 0
                    for n in self.bots
                    if n != name
                ):
                    self.positions[name] = (nx, ny)
        elif kind == "attack":
            target = arg
            if target in self.bots and self.bots[target].hp > 0:
                if (
                    self._distance(self.positions[name], self.positions[target])
                    <= 3
                ):
                    self.bots[target].hp -= 1

    async def step(self) -> Dict[str, Any]:
        async with self._lock:
            self.round_no += 1
            names = list(self.bots.keys())
            for name in names:
                bw = self.bots[name]
                if bw.hp <= 0:
                    continue
                state = {
                    "self_hp": bw.hp,
                    "self_pos": self.positions[name],
                    "board_size": self.board_size,
                    "enemies": {
                        n: {"hp": self.bots[n].hp, "pos": self.positions[n]}
                        for n in names
                        if n != name and self.bots[n].hp > 0
                    },
                }
                if not state["enemies"]:
                    continue
                try:
                    action = bw.bot.act(state)
                except Exception:
                    continue
                await self._handle_action(name, action)
            return self.state()

    def state(self) -> Dict[str, Any]:
        return {
            "round": self.round_no,
            "bots": {
                name: {"hp": bw.hp, "pos": self.positions[name]}
                for name, bw in self.bots.items()
            },
            "board_size": self.board_size,
        }


def load_bot(module_name: str):
    file = Path("bots") / f"{module_name}.py"
    if not file.exists():
        raise FileNotFoundError(file)
    spec = importlib.util.spec_from_file_location(module_name, file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore
    if hasattr(module, "Bot"):
        return module.Bot()
    raise ValueError("No Bot class found")


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

game = WebGame(board_size=5)
clients: Set[WebSocket] = set()


class AddBotRequest(BaseModel):
    bot: str


@app.post("/add_bot")
async def add_bot(req: AddBotRequest):
    bot = load_bot(req.bot)
    await game.add_bot(bot)
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.add(ws)
    await ws.send_json(game.state())
    try:
        while True:
            await ws.receive_text()  # keep connection open
    except WebSocketDisconnect:
        clients.remove(ws)


async def ticker():
    while True:
        state = await game.step()
        for ws in list(clients):
            try:
                await ws.send_json(state)
            except WebSocketDisconnect:
                clients.discard(ws)
        await asyncio.sleep(1)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(ticker())

