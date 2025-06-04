def _dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


class Bot:
    def __init__(self):
        self.name = 'WeakestBot'

    def act(self, state):
        enemies = state['enemies']
        if not enemies:
            return ('move', 'up')

        in_range = {
            n: info
            for n, info in enemies.items()
            if _dist(state['self_pos'], info['pos']) <= 3
        }
        if in_range:
            target = min(in_range, key=lambda n: in_range[n]['hp'])
            return ('attack', target)

        target = min(enemies, key=lambda n: enemies[n]['hp'])
        tx, ty = enemies[target]['pos']
        sx, sy = state['self_pos']
        if abs(tx - sx) > abs(ty - sy):
            return ('move', 'right' if tx > sx else 'left')
        return ('move', 'down' if ty > sy else 'up')
