from pathlib import Path
import importlib.util
import random
import sys
try:
    import tkinter as tk
except Exception:
    tk = None

class Game:
    def __init__(self, bots, board_size=5, use_gui=False):
        # store hp and position for each bot
        self.bots = {bot.name: {'bot': bot, 'hp': 10} for bot in bots}
        self.board_size = board_size
        self.positions = self._init_positions()
        self.use_gui = use_gui and tk is not None
        if self.use_gui:
            self._init_gui()

    def _distance(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def _init_positions(self):
        coords = []
        for _ in range(len(self.bots)):
            while True:
                pos = (random.randrange(self.board_size), random.randrange(self.board_size))
                if pos not in coords:
                    coords.append(pos)
                    break
        return {name: coords[i] for i, name in enumerate(self.bots)}

    def _init_gui(self):
        try:
            self.root = tk.Tk()
        except Exception:
            # If GUI cannot be initialized (e.g., no display), fall back to console
            self.use_gui = False
            return
        self.root.title("Bot Arena")
        self.labels = {}
        for name in self.bots:
            label = tk.Label(self.root, text=f"{name}: {self.bots[name]['hp']} HP")
            label.pack()
            self.labels[name] = label
        self.root.update()

    def _update_gui(self):
        for name, label in self.labels.items():
            label.config(text=f"{name}: {self.bots[name]['hp']} HP")
        self.root.update_idletasks()
        self.root.update()

    def _handle_action(self, name, action):
        if not isinstance(action, tuple) or len(action) != 2:
            return
        kind, arg = action
        if kind == 'move':
            dir_map = {
                'up': (0, -1),
                'down': (0, 1),
                'left': (-1, 0),
                'right': (1, 0),
            }
            if arg not in dir_map:
                return
            dx, dy = dir_map[arg]
            x, y = self.positions[name]
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.board_size and 0 <= ny < self.board_size:
                if not any(
                    self.positions[n] == (nx, ny) and self.bots[n]['hp'] > 0
                    for n in self.bots
                    if n != name
                ):
                    self.positions[name] = (nx, ny)
                    print(f"{name} moves {arg} to {(nx, ny)}")
        elif kind == 'attack':
            target = arg
            if target in self.bots and self.bots[target]['hp'] > 0:
                if self._distance(self.positions[name], self.positions[target]) <= 3:
                    self.bots[target]['hp'] -= 1
                    print(
                        f"{name} shoots {target}. {target} HP: {self.bots[target]['hp']}"
                    )

    def run(self):
        round_no = 0
        if self.use_gui:
            self._update_gui()
        while sum(info['hp'] > 0 for info in self.bots.values()) > 1:
            round_no += 1
            print(f"Round {round_no}")
            if self.use_gui:
                self._update_gui()
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
                    break
                try:
                    action = info['bot'].act(state)
                except Exception as exc:
                    print(f"{name} raised an error: {exc}")
                    continue
                self._handle_action(name, action)
                if self.use_gui:
                    self._update_gui()
        winners = [n for n, i in self.bots.items() if i['hp'] > 0]
        print('Winner:', winners[0] if winners else 'None')
        if self.use_gui:
            self._update_gui()
            tk.Label(self.root, text=f"Winner: {winners[0] if winners else 'None'}").pack()
            self.root.mainloop()


def load_bots(folder):
    bots = []
    for file in Path(folder).glob('*.py'):
        module_name = file.stem
        spec = importlib.util.spec_from_file_location(module_name, file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, 'Bot'):
            bot = module.Bot()
        else:
            print(f"Skipping {file}: no Bot class found")
            continue
        if not hasattr(bot, 'name'):
            bot.name = module_name
        bots.append(bot)
    return bots


def main(folder=Path(__file__).resolve().parent / 'bots', use_gui=False):
    bots = load_bots(folder)
    if len(bots) < 2:
        print('Need at least two bots to start the game.')
        return
    game = Game(bots, use_gui=use_gui)
    game.run()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run bot arena')
    parser.add_argument('folder', nargs='?', default=str(Path(__file__).resolve().parent / 'bots'), help='Bot folder')
    parser.add_argument('--gui', action='store_true', help='Show GUI')
    args = parser.parse_args()
    main(args.folder, use_gui=args.gui)
