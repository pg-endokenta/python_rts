import random

class Bot:
    def __init__(self):
        self.name = 'RandomBot'

    def act(self, state):
        enemies = list(state['enemies'])
        return random.choice(enemies) if enemies else None
