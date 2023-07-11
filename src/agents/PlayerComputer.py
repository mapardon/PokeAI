import random
import statistics

from src.agents.AbstractPlayer import AbstractPlayer


def hp_based_desirability(game_state, player):
    """ Returns an estimation of the desirability of the provided state for the specified player """
    return random.random()


class PlayerComputer(AbstractPlayer):
    """ Implementation of the game playing algorithm with different steps (as described in the paper) """

    def __init__(self, role, state_eval):
        super().__init__(role)
        self.state_eval = state_eval  # input a state and output probability

    def make_move(self, game):
        # Step 1: generate possible outcomes of current turn and evaluate the desirability
        view = game.get_player1_view if self.role == "p1" else game.get_player2_view
        player_moves = game.get_moves_from_state(self.role, view())
        opponent_moves = game.get_moves_from_state("p2", view())

        possible_outcomes = dict()
        for p1m in player_moves:
            possible_outcomes[p1m] = list()
            for i, p2m in zip(range(len(opponent_moves)), opponent_moves):
                bin_state = game.get_numeric_repr(game.apply_player_moves(view(), p1m, p2m, 1)[0])
                possible_outcomes[p1m].append(self.state_eval(bin_state))

        # Step 2: select the least risky move (for now: best average)
        best_name, best_score = str(), -1
        for m in possible_outcomes.keys():
            tmp = statistics.mean(possible_outcomes[m])
            if tmp > best_score:
                best_name = m
                best_score = tmp

        if random.random() < 0.001:
            pass
        return best_name
