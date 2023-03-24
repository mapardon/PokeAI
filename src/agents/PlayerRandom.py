import random

from src.agents.AbstractPlayer import AbstractPlayer


class PlayerRandom(AbstractPlayer):
    def __init__(self, role):
        super(PlayerRandom, self).__init__(role)

    def make_move(self, game):
        """ :returns Random move among playable moves """

        options = game.get_moves_from_state(self.role, None)
        return random.choice(options)
