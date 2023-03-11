import random

from src.game.agents.AbstractPlayer import AbstractPlayer


class PlayerRandom(AbstractPlayer):
    def __init__(self, role):
        super(PlayerRandom, self).__init__(role)

    def make_move(self, game):
        """ :returns Random move among playable moves """

        options = game.get_player1_moves() if self.role == "1" else game.get_player2_moves()
        return random.choice(options)
