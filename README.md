# Python RTS Bot Arena

This repository provides a simple RTS style game where bots battle on a small grid. A FastAPI server runs the game logic and a React front‑end visualises the board. Both the back‑end and the front‑end run directly on the host without Docker.

The development environment requires Python 3.11 and Node.js 20 to be available on your system. Python packages are installed into a `.venv` virtual environment using [uv](https://github.com/astral-sh/uv).

## Usage

Start the back‑end server:

```bash
make backend
```
The command creates `.venv` and installs the required Python packages automatically if needed.

Start the front‑end server. The command installs the required JavaScript dependencies if needed and then runs the dev server:

```bash
make frontend
```

The front‑end reads the API location from a `.env` file. Copy the provided
`frontend/.env.example` to `frontend/.env` and adjust the URL if your back‑end
is not running on `http://localhost:8000`.

Run the test suite:

```bash
make test
```
This command uses the same `.venv` environment, creating it if necessary.
