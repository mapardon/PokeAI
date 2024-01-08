import numpy as np

from src.agents.PlayerNN import PlayerNN
from src.agents.PlayerGT import PlayerGT
from src.game.PokeGame import PokeGame


class PlayerHybrid(PlayerGT):
    """
        Use the algorithms developed in the other strategies (PlayerGT and PlayerGA) in an attempt to combine their
        strength. The principle is to use the estimation of the desirability of game states computed by the neural
        network as a payoffs for the game theory agent.
    """

    def __init__(self, role: str, network: tuple[np.array] | list[np.array], act_f: str):
        super().__init__(role)
        self.state_estimator = PlayerNN(self.role, network, act_f)

    def compute_player_payoff(self, state: PokeGame.GameStruct, player: str):
        return self.state_estimator.forward_pass(self.game.get_numeric_repr(state, player))
