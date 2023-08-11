import random

from src.agents.AbstractPlayer import AbstractPlayer


class PlayerRandom(AbstractPlayer):
    """
        Random move among playable moves
    """

    def __init__(self, role):
        super(PlayerRandom, self).__init__(role)

    def make_move(self, game):

        return random.choice(game.get_moves_from_state(self.role, None))
