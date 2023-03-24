import random

from src.agents.AbstractPlayer import AbstractPlayer


P_INF = 100000
M_INF = -100000


def evaluation_hp_based(state):
    """ Returns an evaluation of the provided state (GameStruct) for the minimax algorithm. This evaluation is based
     on the hp percentage of both teams."""

    opponent_hp = sum([100 * p.cur_hp / p.hp if p is not None else 100 for p in state.team2]) / len(state.team2)
    agent_hp = sum([100 * p.cur_hp / p.hp if p is not None else 100 for p in state.team1]) / len(state.team1)
    return agent_hp / opponent_hp


class PlayerMinimax(AbstractPlayer):

    def __init__(self, role, max_depth, state_evaluation):
        """
        Minimax agent for the game

        """

        super().__init__(role)
        self.max_depth = max_depth
        self.state_evaluation = state_evaluation

    def make_move(self, game):

        best_move = None
        if self.max_depth == 0:
            return random.choice(game.playable_moves(self.role))

        best_eval = M_INF - 1000
        for move in game.get_moves_from_state(self.role, None):
            move_eval = self.minimax(game, move, self.max_depth - 1, self.role, M_INF, P_INF)
            if move_eval > best_eval:
                best_eval = move_eval
                best_move = move

        return best_move

    def minimax(self, game, state, cur_depth, player, alpha, beta):
        if cur_depth == 0 or game.is_end_state(state):
            state_eval = self.state_evaluation(state)  # gives a numeric evaluation of this state
            return state_eval

        if player:  # max
            max_eval = M_INF - 1000
            for m in game.get_moves_from_state(player, state):
                state_eval = self.minimax(m, cur_depth - 1, (player + 1) % 2, alpha,
                                          beta)  # next_state is not used, except for the last return (which is played)
                max_eval = max(max_eval, state_eval)
                alpha = max(alpha, state_eval)
                if beta <= alpha:
                    return max_eval
            return max_eval
        else:  # min
            min_eval = P_INF + 1000
            for m in possible_moves(state, player):
                state_eval = self.minimax(m, cur_depth - 1, (player + 1) % 2, alpha, beta)
                min_eval = min(min_eval, state_eval)
                beta = min(beta, state_eval)
                if beta <= alpha:
                    return min_eval
            return min_eval
