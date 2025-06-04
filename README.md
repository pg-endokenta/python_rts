# Python RTS Bot Arena

This repository contains a simple arena for running Python bots against
one another. Place your bot files in the `bots/` directory. Each bot
must define a `Bot` class with an `act(state)` method. The provided
`arena.py` script loads all bots from the folder and runs a small battle
where each bot has 10 HP and deals 1 damage per attack.

Run the arena with:

```
python arena.py
```

You can also specify a different bot directory:

```
python arena.py path/to/bots
```
