import numpy as np

from src.agents.PlayerGA import PlayerGA
from src.agents.PlayerGT import PlayerGT
from src.game.PokeGame import PokeGame


class PlayerHybrid(PlayerGT):
    """
        Use the algorithms developed in the other strategies (PlayerGT and PlayerGA) in an attempt to combine their
        strength. The principle will be to use the estimation of the desirability of game states computed by the neural
        network as a payoffs for the game theory-based agent.
    """
    def __init__(self, role: str, network: tuple[np.array] | list[np.array], act_f: str):
        super().__init__(role)
        self.state_estimator = PlayerGA(self.role, network, act_f)

    def compute_player_payoff(self, state: PokeGame.GameStruct, player: str):
        PokeGame.get_numeric_repr()
        payoff = self.state_estimator.forward_pass()

        return payoff
