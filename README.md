# Python RTS Bot Arena

This repository contains a simple arena for running Python bots against one another on a small grid. Place your bot files in the `bots/` directory. Each bot must define a `Bot` class with an `act(state)` method. The provided scripts allow running matches in the terminal or via a small web server.

## Running with Docker

The recommended way to try the arena is using Docker Compose. Make sure you have Docker and Docker Compose installed then build the image:

```bash
docker compose build
```

Start the web arena server:

```bash
docker compose up
```

The API will be available on `http://localhost:8000`.

You can also run a single match in the terminal:

```bash
docker compose run --rm app python arena.py
```

Bots placed inside the `bots/` directory on the host are mounted into the container automatically.

## Writing your own bots

Place a Python file in the `bots/` directory defining a class `Bot` with an `act(state)` method. The `state` dictionary passed to `act` contains your current HP and position as well as information about the enemies:

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

- `('move', direction)` moves one tile in the given direction (`up`, `down`, `left` or `right`). A move that would leave the board or bump into another bot is ignored.
- `('attack', enemy_name)` shoots at the given enemy if it is within a Manhattan distance of 3 tiles.

If anything else is returned, the bot simply skips its turn.

## Web arena

A simple FastAPI server lives in `webarena.py`. It runs an endless game loop where new bots can be added via an HTTP request and the state is broadcast over a WebSocket. When started through Docker Compose, it is already running.

Add a bot (specify the module name without `.py`):

```bash
curl -X POST -H "Content-Type: application/json" -d '{"bot": "random_bot"}' http://localhost:8000/add_bot
```

Connect to `ws://localhost:8000/ws` to receive game updates every second.

A basic front‑end built with Vite lives in the `frontend` directory. After installing Node.js dependencies run:

```bash
npm install
npm run dev
```

and open the shown URL to watch the arena in your browser.

When running inside GitHub Codespaces the API is exposed on a different URL. Set `VITE_API_URL` to the forwarded address before starting the dev server:

```bash
echo "VITE_API_URL=$(gp url 8000)" > frontend/.env
npm run dev
```
