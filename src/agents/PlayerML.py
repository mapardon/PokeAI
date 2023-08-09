import random
import numpy as np
from src.agents.AbstractPlayer import AbstractPlayer


# Activation functions #
from src.game.PokeGame import PokeGame


def sigmoid(x):
    #print(x)
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

    def __init__(self, mode: str, role: str, network: tuple, ls: str, lamb: float | None, act_f: str, eps: float,
                 lr: float, mvsel: str):
        """
        ML agent for the game, using ML methods to play and learn the game.

        :param mode: tells which mode is being played ('match', 'train' or 'compare')
        :param role: "p1" or "p2"
        :param network: in train mode, both agents must share same NN object, so weights are read from GameEngine
        :param ls: As ls is fixed with a NN, it is read from database with the network
        :param lamb: lambda parameter for TD-lambda and Q-lambda
        :param act_f: activation function for the network
        :param eps: random factor
        :param lr: learning rate
        :param mvsel: mode of move selection (epsilon-greedy, softmax-exponential...)
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
            self.move_selection = {"eps-greedy": self.eps_greedy_move,
                                   "softmax-exp": self.softmax_move}[mvsel]
            self.backpropagation = {"Q-learning": self.q_learning_backpropagation,
                                    "SARSA": self.sarsa_backpropagation,
                                    "TD-lambda": self.td_lambda_backpropagation,
                                    "Q-lambda": self.q_lambda_backpropagation}[ls]

        else:  # test or match
            self.move_selection = self.eps_greedy_move
            self.ls = self.lr = self.lamb = None

    # Communication with game loop #

    def make_move(self, game: PokeGame):
        """ Generate all states reachable from current state and convert in numeric representation to choose a move

        :returns: Selected move """
        # FIXME: NaN appearing

        options = list()
        moves_name = dict()
        for m1 in game.get_moves_from_state("p1", None):
            for m2 in game.get_moves_from_state("p2", None):
                num_state = game.get_numeric_repr(game.apply_player_moves(game.get_cur_state(), m1, m2))
                options.append(num_state)
                moves_name[tuple(num_state)] = (m1, m2)
        cur_num_state = game.get_numeric_repr(state=None, player=self.role)

        new_s, best_p_out = self.move_selection(options)
        if self.mode == "train":  # Move + update weight matrices
            self.backpropagation(game, cur_num_state, new_s, best_p_out)

        new_s_name = moves_name[tuple(new_s)]
        new_s_name = new_s_name[0] if self.role == "p1" else new_s_name[1]

        return new_s_name

    def end_game(self, game, player1_won):
        """ Same as previous for the end of the game """

        self.backpropagation(game, game.get_numeric_repr(None, self.role), None, player1_won if self.role == "1" else not player1_won)

    # Moves ranking #

    def best_moves(self, moves):
        """ Returns the move evaluated as most promising

        :returns tuple containing:
                * list of the moves evaluated as most promising by the network (in case several moves are equally best)
                * the probability estimation. """

        best_moves = list()
        best_value = None
        c = 1 if self.role == "p1" else -1  # game is viewed under 1st player pov

        for m in moves:
            estimation = self.forward_pass(m)
            if best_value is None or c * estimation > c * best_value:  # opponent move, invert inequality
                best_moves = [m]
                best_value = estimation
            elif estimation == best_value:
                best_moves.append(m)

        random.shuffle(best_moves)
        return best_moves, best_value

    def eps_greedy_move(self, moves):
        """ Returns a move chosen via eps-greedy selection """

        best_moves, best_p_out = self.best_moves(moves)
        if random.random() > self.eps:  # Choose move among highest evaluated
            new_s = random.choice(best_moves)
        else:
            new_s = random.choice(moves)
        return new_s, best_p_out

    def softmax_move(self, moves):
        """ Returns a move chosen via softmax-exponential selection. """

        probs = np.array([self.forward_pass(m) for m in moves])

        softmax_vals = np.exp(probs) / np.sum(np.exp(probs), axis=0)
        new_s = moves[np.random.choice([i for i in range(len(moves))], p=softmax_vals)]
        best_p_out = self.forward_pass(moves[np.argmax(softmax_vals)])
        return new_s, best_p_out

    # forward pass and backpropagations for different learning algorithms

    def forward_pass(self, state: list):
        """ Use the knowledge of the network to make an estimation of the victory probability of the first player
        of a provided game state. """

        W_int = self.network[0]
        W_out = self.network[1]
        P_int = self.act_f(np.dot(W_int, state))
        p_out = self.act_f(P_int.dot(W_out))

        return p_out if self.act_f == sigmoid else sigmoid(p_out)

    def q_learning_backpropagation(self, game: PokeGame, cur_state: list,
                                   chosen_state: list, best_next_prob: float):
        """
        Apply backpropagation algorithm with Q-learning strategy

        :param game: Reference to current game
        :param cur_state: Numeric representation of current state
        :param chosen_state: Numeric representation of state selected for next move. Can be None if cur_state
            is an end state
        :param best_next_prob: Victory estimation of the best possible option (from cur_state)
        """

        cur_prob = self.forward_pass(cur_state)
        cmp_prob = best_next_prob
        W_int = self.network[0]
        delta = cur_prob - cmp_prob
        W_out = self.network[1]
        P_int = self.act_f(np.dot(W_int, cur_state))
        p_out = self.act_f(P_int.dot(W_out))
        grad_out = self.grad(p_out)
        grad_int = self.grad(P_int)
        Delta_int = grad_out * W_out * grad_int

        W_int -= self.lr * delta * np.outer(Delta_int, cur_state)
        W_out -= self.lr * delta * grad_out * P_int

    def sarsa_backpropagation(self, game: PokeGame, cur_state: PokeGame.GameStruct, chosen_state: PokeGame.GameStruct,
                              best_next_prob: float):
        """
        Apply backpropagation algorithm with SARSA strategy

        :param game: Reference to current game
        :param cur_state: GameStruct of current state
        :param chosen_state: GameStruct of state selected for next move. Can be None if cur_state is an end state
        :param best_next_prob: Victory estimation of the best possible option (from cur_state)
        """

        cur_prob = self.forward_pass(game.get_numeric_repr(cur_state))
        cmp_prob = self.forward_pass(game.get_numeric_repr(chosen_state)) if chosen_state is not None else best_next_prob
        W_int = self.network[0]
        delta = cur_prob - cmp_prob
        W_out = self.network[1]
        P_int = self.act_f(np.dot(W_int, cur_state))
        p_out = self.act_f(P_int.dot(W_out))
        grad_out = self.grad(p_out)
        grad_int = self.grad(P_int)
        Delta_int = grad_out * W_out * grad_int

        W_int -= self.lr * delta * np.outer(Delta_int, cur_state)
        W_out -= self.lr * delta * grad_out * P_int

    def td_lambda_backpropagation(self, game, state, cur_prob, cmp_prob):
        return

    def q_lambda_backpropagation(self, game, state, cur_prob, cmp_prob):
        return
