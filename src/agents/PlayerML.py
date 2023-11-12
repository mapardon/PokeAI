import random
import numpy as np
from src.agents.AbstractPlayer import AbstractPlayer


# Activation functions #
from src.game.PokeGame import PokeGame


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def sigmoid_gradient(x):
    return x * (1 - x)


def hyperbolic_tangent(x):
    return np.tanh(x)


def h_tangent_gradient(x):
    return 1 / np.power(np.cosh(x), 2)


def relu(x):
    tmp = np.amax(x)
    if tmp > 10 ** 4:
        print(tmp)
    return x * (x > 0)


def relu_gradient(x):
    return 1 * (x > 0)


class PlayerML(AbstractPlayer):

    def __init__(self, role: str, mode: str, network: tuple, ls: str, lamb: float | None, act_f: str, eps: float,
                 lr: float, mv_sel: str = None):
        """
        ML agent for the game, using ML methods to play and learn the game.

        :param role: "p1" or "p2"
        :param mode: tells which mode is being played ('match', 'train' or 'compare')
        :param network: in train mode, both agents must share same NN object, so weights are read from GameEngine
        :param ls: As ls is fixed with a NN, it is read from database with the network
        :param lamb: lambda parameter for TD-lambda and Q-lambda
        :param act_f: activation function for the network
        :param eps: random factor
        :param lr: learning rate
        :param mv_sel: "max_low" or "max_avg", rule to select a move
        """

        super().__init__(role)

        # process game_parameters from gui and initialize adequate variables
        self.mode = mode
        self.network = network
        self.eps = eps
        self.act_f, self.grad = {"sigmoid": (sigmoid, sigmoid_gradient),
                                 "hyperbolic tangent": (hyperbolic_tangent, h_tangent_gradient),
                                 "ReLU": (relu, relu_gradient)}[act_f]

        if mode == "train":
            self.lamb = lamb
            self.lr = lr
            self.move_selection = self.move_selector
            self.backpropagation = {"SARSA": self.sarsa_backpropagation,
                                    "TD-lambda": self.td_lambda_backpropagation}[ls]
            # save computed information to reuse for backtracking after receiving new state
            self.cur_state = None

        else:  # test or match
            self.move_selection = self.move_selector
            self.ls = self.lr = self.lamb = None

    # Communication with game loop #

    def make_move(self, game: PokeGame):
        """ Generate all states reachable from current state and convert in numeric representation to choose a move

        :returns: Selected move """

        # opponent down, must not move
        if (not game.player1_view.on_field2.cur_hp and self.role == "p1" or
                not game.player2_view.on_field1.cur_hp and self.role == "p2"):
            return None

        # ourselves or no one down, select a possible move using move selection strategy and save state for backtracking
        move = self.move_selection(game)
        self.cur_state = game.get_numeric_repr(player=self.role)

        return move

    # Moves ranking #

    def move_selector(self, game: PokeGame) -> str:
        """ Returns the move evaluated as most promising (or a random one at a frequency of self.eps)

        :returns: action of the player """

        cur_move = None

        # random move
        if random.random() < self.eps:
            options = list()
            pl, opp = ["p1", "p2"][::(-1) ** (self.role == "p2")]
            view = game.get_player_view(self.role)
            for pmv in game.get_moves_from_state(pl, view):
                for omv in game.get_moves_from_state(opp, view):
                    options.append((pmv, omv))
            cur_move = random.choice(options)[0]

        # best move
        p2f = (-1) ** (self.role == "p2")  # if agent is player2, estimations are interpreted inversely
        min_lines = list()  # worst outcome for each player option (depending on opponent options)
        pl, opp = ["p1", "p2"][::(-1) ** (self.role == "p2")]
        view = game.player1_view if self.role == "p1" else game.player2_view

        # iterate through possible options for the player and keep the "least bad"
        for pmv in game.get_moves_from_state(pl, view):
            min_lines += [(None, 1)]
            for omv in game.get_moves_from_state(opp, view):
                p1mv, p2mv = (pmv, omv) if self.role == "p1" else (omv, pmv)
                s = game.get_numeric_repr(game.apply_player_moves(game.get_player_view(self.role), p1mv, p2mv))
                p = p2f * self.forward_pass(s)
                # TODO: average estimation
                if p < min_lines[-1][1]:
                    min_lines[-1] = (pmv, p)

        # TODO: random draw if several best values?
        best_move = max(min_lines, key=lambda x: x[1])[0]
        if cur_move is None:
            cur_move = best_move

        return cur_move

    # forward pass and backpropagation for different learning algorithms

    def forward_pass(self, state: list):
        """ Use the knowledge of the network to make an estimation of the victory probability of the first player
        of a provided game state. """

        W_int = self.network[0]
        W_out = self.network[1]
        P_int = self.act_f(np.dot(W_int, state))
        p_out = self.act_f(P_int.dot(W_out))

        return p_out if self.act_f == sigmoid else sigmoid(p_out)

    def sarsa_backpropagation(self, game_state: list[int], game_finished: bool, p1_victory: bool):
        """
        Apply backpropagation algorithm with SARSA strategy

        :param game_state: numeric representation of game state (after player moves)
        :param game_finished: indicates if game_state is an end state
        :param p1_victory: if game_state is an end state, indicates the victory of player 1
        """

        cur_prob = self.forward_pass(self.cur_state)
        cmp_prob = self.forward_pass(game_state) if not game_finished else p1_victory
        delta = cur_prob - cmp_prob
        W_int = self.network[0]
        W_out = self.network[1]
        P_int = self.act_f(np.dot(W_int, self.cur_state))
        p_out = self.act_f(P_int.dot(W_out))
        grad_out = self.grad(p_out)
        grad_int = self.grad(P_int)
        Delta_int = grad_out * W_out * grad_int

        W_int -= self.lr * delta * np.outer(Delta_int, self.cur_state)
        W_out -= self.lr * delta * grad_out * P_int

    def td_lambda_backpropagation(self, game, state, cur_prob, cmp_prob):
        return
