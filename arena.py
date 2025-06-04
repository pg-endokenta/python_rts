from pathlib import Path
import importlib.util
import sys

class Game:
    def __init__(self, bots):
        # store hp for each bot
        self.bots = {bot.name: {'bot': bot, 'hp': 10} for bot in bots}

    def run(self):
        round_no = 0
        while sum(info['hp'] > 0 for info in self.bots.values()) > 1:
            round_no += 1
            print(f"Round {round_no}")
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
        winners = [n for n, i in self.bots.items() if i['hp'] > 0]
        print('Winner:', winners[0] if winners else 'None')


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


def main(folder='bots'):
    bots = load_bots(folder)
    if len(bots) < 2:
        print('Need at least two bots to start the game.')
        return
    game = Game(bots)
    game.run()


if __name__ == '__main__':
    folder = sys.argv[1] if len(sys.argv) > 1 else 'bots'
    main(folder)
