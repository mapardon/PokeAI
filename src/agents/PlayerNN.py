import numpy as np

from src.agents.AbstractPlayer import AbstractPlayer
from src.agents.nn_utils import sigmoid, sigmoid_gradient, hyperbolic_tangent, h_tangent_gradient, relu, relu_gradient
from src.game.PokeGame import PokeGame


class PlayerNN(AbstractPlayer):
    """
        Base class for strategies using neural network (reinforcement learning and genetic algorithm agents). Also
        implements a greedy move selection algorithm.
    """

    def __init__(self, role, network: tuple[np.array] | list[np.array], act_f: str):
        super().__init__(role)

        self.network = network
        self.act_f, self.grad = {"sigmoid": (sigmoid, sigmoid_gradient),
                                 "hyperbolic tangent": (hyperbolic_tangent, h_tangent_gradient),
                                 "ReLU": (relu, relu_gradient)}[act_f]

    # Communication with game loop #
    def make_move(self, game: PokeGame) -> str | None:
        """
            Use knowledge of the network to select a move in a greedy strategy.
        """

        # opponent down, must not move
        if (not game.player1_view.on_field2.cur_hp and self.role == "p1" or
                not game.player2_view.on_field1.cur_hp and self.role == "p2"):
            return None

        # ourselves or no one down, select a possible move using move selection strategy and save state for backtracking
        move = self.move_selector(game)

        return move

    # Moves ranking #

    def forward_pass(self, state: list):
        """ Use the knowledge of the network to make an estimation of the victory probability of the first player
        for a provided game state. """

        w_int = self.network[0]
        w_out = self.network[1]
        p_int = self.act_f(np.dot(w_int, state))
        p_out = sigmoid(p_int.dot(w_out))

        return p_out

    def move_selector(self, game: PokeGame) -> str:
        """ Returns the move evaluated as most promising

        :returns: action of the player """

        min_lines = list()  # worst outcome for each player option (depending on opponent options)
        pl, opp = ["p1", "p2"][::(-1) ** (self.role == "p2")]
        view = game.player1_view if self.role == "p1" else game.player2_view

        # iterate through possible options for the player and keep the "least bad"
        for pmv in game.get_moves_from_state(pl, view):
            min_lines += [(None, 1)]
            for omv in game.get_moves_from_state(opp, view):
                p1mv, p2mv = (pmv, omv) if self.role == "p1" else (omv, pmv)
                s = game.get_numeric_repr(game.apply_player_moves(game.get_player_view(self.role), p1mv, p2mv))
                p = self.forward_pass(s)
                if p < min_lines[-1][1]:
                    min_lines[-1] = (pmv, p)

        best_move = max(min_lines, key=lambda x: x[1])[0]

        return best_move
