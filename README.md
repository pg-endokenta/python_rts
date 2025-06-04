# Python RTS Bot Arena

This repository contains a simple arena for running Python bots against
one another. Place your bot files in the `bots/` directory. Each bot
must define a `Bot` class with an `act(state)` method. The provided
`arena.py` script loads all bots from the folder and runs a small battle
where each bot has 10 HP and deals 1 damage per attack.

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
