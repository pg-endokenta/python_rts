import random


def _dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


class Bot:
    def __init__(self):
        self.name = 'RandomBot'

    def act(self, state):
        enemies = list(state['enemies'].items())
        in_range = [n for n, info in enemies if _dist(state['self_pos'], info['pos']) <= 3]
        if in_range and random.random() < 0.5:
            return ('attack', random.choice(in_range))
        return ('move', random.choice(['up', 'down', 'left', 'right']))
