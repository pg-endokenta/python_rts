# Python RTS Bot Arena

This repository contains a simple arena for running Python bots against
one another on a small grid. Place your bot files in the `bots/`
directory. Each bot must define a `Bot` class with an `act(state)`
method. The provided `arena.py` script loads all bots from the folder
and runs a battle where each bot has 10 HP and can move or shoot at
enemies within range.

## Setup

First create a Python virtual environment using
[uv](https://github.com/astral-sh/uv). Install `uv` if you don't have it
already (`pip install uv`) and then run:

```bash
uv venv
uv sync
```

After this the arena can be run with `uv run python arena.py` or by
running `python arena.py` within the created `.venv`.

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

The repository is configured to work with
[uv](https://github.com/astral-sh/uv). Once you have created the virtual
environment as shown above you can run commands inside it using
`uv run`:

```bash
uv run python arena.py
```

## Web arena

A simple web server is provided in `webarena.py` using FastAPI. It runs an
endless game loop where new bots can be added via an HTTP request and the
state is broadcast over a WebSocket.

Start the server:

```bash
uvicorn webarena:app --reload
```

Add a bot (specify the module name without `.py`):

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"bot": "random_bot"}' http://localhost:8000/add_bot
```

Connect to `ws://localhost:8000/ws` to receive game updates every second.

A basic front‑end built with Vite lives in the `frontend` directory. After
installing Node.js dependencies run:

```bash
npm install
npm run dev
```

and open the shown URL to watch the arena in your browser.
