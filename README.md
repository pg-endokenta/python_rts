# Python RTS Bot Arena

This repository contains a simple arena for running Python bots against
one another on a small grid. Place your bot files in the `bots/`
directory. Each bot must define a `Bot` class with an `act(state)`
method. The provided `arena.py` script loads all bots from the folder
and runs a battle where each bot has 10 HP and can move or shoot at
enemies within range.

Run the arena with:

```bash
python arena.py
```

You can also specify a different bot directory:

```bash
python arena.py path/to/bots
```

## GUI mode

If `tkinter` is available on your system you can run the arena with a
simple GUI by passing `--gui`:

```bash
python arena.py --gui
```

The flag can be combined with a custom bot directory as well.

## Writing your own bots

Place a Python file in the `bots/` directory defining a class `Bot` with
an `act(state)` method. The `state` dictionary passed to `act` contains
your current HP and position as well as information about the enemies:

```
state = {
    'self_hp': 10,
    'self_pos': (x, y),
    'board_size': 5,
    'enemies': {
        'OtherBot': {'hp': 9, 'pos': (2, 3)},
        ...
    }
}
```

Return a tuple to describe your action:

- `('move', direction)` moves one tile in the given direction (`up`,
  `down`, `left` or `right`). A move that would leave the board or bump
  into another bot is ignored.
- `('attack', enemy_name)` shoots at the given enemy if it is within a
  Manhattan distance of 3 tiles.

If anything else is returned, the bot simply skips its turn.

## Environment management with uv

The project includes a `pyproject.toml` and `uv.lock` so that the
environment can be managed with [uv](https://github.com/astral-sh/uv).
Install uv (e.g. `pip install uv`) and then create the virtual
environment and install dependencies:

```bash
uv venv
uv sync
```

After this the arena can be run with `uv run python arena.py` or by
running `python arena.py` within the created `.venv`.

## Web server and frontend

To watch battles in the browser start the FastAPI server:

```bash
uvicorn server:app --reload
```

The server keeps the game running indefinitely. New bots can be added
by POSTing to `/bots/{bot_name}` where `bot_name` is a Python file in
the `bots/` directory without the extension. The current board state is
available at `/state`.

The `frontend/` folder contains a minimal [Vite](https://vitejs.dev)
setup. Start it with:

```bash
npm install
npm run dev --prefix frontend
```

This opens a page that polls the server every second and renders the
board on screen.
