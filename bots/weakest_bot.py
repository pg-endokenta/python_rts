class Bot:
    def __init__(self):
        self.name = 'WeakestBot'

    def act(self, state):
        enemies = state['enemies']
        if not enemies:
            return None
        return min(enemies, key=enemies.get)
