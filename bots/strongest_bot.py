class Bot:
    def __init__(self):
        self.name = 'StrongestBot'

    def act(self, state):
        enemies = state['enemies']
        if not enemies:
            return None
        return max(enemies, key=enemies.get)
