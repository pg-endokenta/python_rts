# Python RTS Bot Arena

This repository provides a simple RTS style game where bots battle on a small grid. A FastAPI server runs the game logic and a React front‑end visualises the board. Both parts are started through Docker Compose.

## Usage

Start the development containers (backend and front‑end). The command builds the
images if necessary and then runs them with Docker Compose:

```bash
make dev
```

Run the test suite:

```bash
make test
```

Place your own bots inside the `bots/` directory. They will automatically be mounted into the backend container.
