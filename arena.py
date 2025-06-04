from pathlib import Path
import importlib.util
import sys
try:
    import tkinter as tk
except Exception:
    tk = None

class Game:
    def __init__(self, bots, use_gui=False):
        # store hp for each bot
        self.bots = {bot.name: {'bot': bot, 'hp': 10} for bot in bots}
        self.use_gui = use_gui and tk is not None
        if self.use_gui:
            self._init_gui()

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

    def run(self):
        round_no = 0
        if self.use_gui:
            self._update_gui()
        while sum(info['hp'] > 0 for info in self.bots.values()) > 1:
            round_no += 1
            print(f"Round {round_no}")
            if self.use_gui:
                self._update_gui()
            # iterate over a copy to allow modifications during iteration
            for name, info in list(self.bots.items()):
                if info['hp'] <= 0:
                    continue
                state = {
                    'self_hp': info['hp'],
                    'enemies': {n: i['hp'] for n, i in self.bots.items() if n != name and i['hp'] > 0}
                }
                if not state['enemies']:
                    break
                try:
                    target = info['bot'].act(state)
                except Exception as exc:
                    print(f"{name} raised an error: {exc}")
                    continue
                if target not in self.bots or self.bots[target]['hp'] <= 0:
                    continue
                self.bots[target]['hp'] -= 1
                print(f"{name} attacks {target}. {target} HP: {self.bots[target]['hp']}")
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


def main(folder='bots', use_gui=False):
    bots = load_bots(folder)
    if len(bots) < 2:
        print('Need at least two bots to start the game.')
        return
    game = Game(bots, use_gui=use_gui)
    game.run()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run bot arena')
    parser.add_argument('folder', nargs='?', default='bots', help='Bot folder')
    parser.add_argument('--gui', action='store_true', help='Show GUI')
    args = parser.parse_args()
    main(args.folder, use_gui=args.gui)
