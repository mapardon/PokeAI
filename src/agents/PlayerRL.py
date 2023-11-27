import random
import numpy as np
from src.agents.PlayerNN import PlayerNN
from src.game.PokeGame import PokeGame


class PlayerRL(PlayerNN):

    def __init__(self, role: str, mode: str, network: tuple, ls: str, act_f: str, eps: float, lr: float):
        """
        ML agent for the game, using ML methods to play and learn the game.

        :param role: "p1" or "p2"
        :param mode: tells which mode is being played ('match', 'train' or 'compare')
        :param network: in train mode, both agents must share same NN object, so weights are read from GameEngine
        :param ls: As ls is fixed with a NN, it is read from database with the network
        :param act_f: activation function for the network
        :param eps: random factor
        :param lr: learning rate
        """

        super().__init__(role, network, act_f)

        self.eps = eps
        self.move_selection = self.move_selector

        if mode == "train":
            self.lr = lr
            self.backpropagation = {"SARSA": self.sarsa_backpropagation}[ls]
            # save computed information to reuse for backtracking after receiving new state
            self.cur_state = None

        else:  # test or match
            self.ls = self.lr = None

    # Communication with game loop #

    def make_move(self, game: PokeGame) -> str | None:
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
        """ Returns the move evaluated as most promising or a random one at a frequency of self.eps (epsilon-greedy)

        :returns: action of the player """

        # random move
        if random.random() < self.eps:
            options = list()
            pl, opp = ["p1", "p2"][::(-1) ** (self.role == "p2")]
            view = game.get_player_view(self.role)
            for pmv in game.get_moves_from_state(pl, view):
                for omv in game.get_moves_from_state(opp, view):
                    options.append((pmv, omv))
            move = random.choice(options)[0]

        else:
            move = super().move_selector(game)

        return move

    # Learning algorithms #

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
