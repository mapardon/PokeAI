import random
import warnings
from statistics import stdev
from copy import deepcopy

import numpy as np
import nashpy as nash

from src.agents.AbstractPlayer import AbstractPlayer
from src.game.GameEstimation import fill_game_with_estimation
from src.game.PokeGame import PokeGame


warnings.filterwarnings("ignore")


class PlayerGT(AbstractPlayer):
    """
        Implementation of the Game Theory approach

        Construct payoff matrix based on the knowledge of the given game state and select a move corresponding to a
        Nash equilibrium of the game
    """

    def __init__(self, role: str):
        super().__init__(role)
        self.game = None
        self.payoff_mat = None

    @staticmethod
    def compute_player_payoff(state: PokeGame.GameStruct, player: str):
        """
            Compute the utility of the given game state for the given player.
        """

        p1_hp, p2_hp = sum([p.cur_hp for p in state.team1]), sum([p.cur_hp for p in state.team2])
        p1_max, p2_max = sum([p.hp for p in state.team1]), sum([p.hp for p in state.team2])
        p1_alive, p2_alive = sum([p.is_alive() for p in state.team1]), sum([p.is_alive() for p in state.team2])

        payoff = (-1) ** (player == "p2") * ((5 * p1_hp / p1_max) + (5 * p1_alive / len(state.team1))) + \
                 (-1) ** (player == "p1") * ((5 * p2_hp / p2_max) + (5 * p2_alive / len(state.team2)))

        return payoff

    def build_payoff_matrix(self):
        """
            Build a payoff matrix with payoffs related to possible actions of the player
            Matrix format: dict[p1 action][p2 action]: (p1 payoff, p2 payoff).
        """

        p1_view, p2_view = self.game.player1_view, self.game.player2_view
        if self.role == "p1":
            p2_view_p1_of, p2_view_p2_of = p2_view.on_field1, p2_view.on_field2
        else:
            p1_view_p1_of, p1_view_p2_of = p1_view.on_field1, p1_view.on_field2

        force_order = self.role != "p1"
        self.payoff_mat = dict()

        p1_ops = [m for m in self.game.get_moves_from_state("p1", p1_view) if m is not None]
        p2_ops = [m for m in self.game.get_moves_from_state("p2", p2_view) if m is not None]

        for p1_mv in p1_ops:
            if p1_mv not in self.payoff_mat.keys():
                self.payoff_mat[p1_mv] = dict()

            for p2_mv in p2_ops:

                # our moves that opponent doesn't know are considered generic moves ("notype") for them
                if self.role == "p1":
                    m1_for_p1, m2_for_p1, m2_for_p2 = p1_mv, p2_mv, p2_mv
                    m1_for_p2 = p1_mv if "switch" in p1_mv or p1_mv in (m.name for m in
                                                                        p2_view_p1_of.moves) else "light_notype"
                else:
                    m1_for_p2, m2_for_p2, m1_for_p1 = p1_mv, p2_mv, p1_mv
                    m2_for_p1 = p2_mv if "switch" in p2_mv or p2_mv in (m.name for m in
                                                                        p1_view_p2_of.moves) else "light_notype"

                # force_order: pessimistic estimation for both sides
                p1_po = self.compute_player_payoff(self.game.apply_player_moves(deepcopy(p1_view), m1_for_p1,
                                                                                m2_for_p1, 0.95, force_order), "p1")
                p2_po = self.compute_player_payoff(self.game.apply_player_moves(deepcopy(p2_view), m1_for_p2,
                                                                                m2_for_p2, 0.95, not force_order), "p2")

                self.payoff_mat[p1_mv][p2_mv] = (round(p1_po, 3), round(p2_po, 3))

    def remove_strictly_dominated_strategies(self):
        """
            [old]
            From the payoff matrix previously built, search for strictly dominated strategies and remove them from
            the matrix. Dominated strategies are removed for player and opponent (suppose the opponent won't play such
            moves). Only remove strategies dominated by other pure strategy.
        """

        dominated_rows, dominated_columns = [None], [None]

        while dominated_columns or dominated_rows:
            p1_moves = list(self.payoff_mat.keys())
            p2_moves = list(self.payoff_mat[p1_moves[0]].keys())
            dominated_columns.clear()
            dominated_rows.clear()

            # dominated moves for p1, line eliminations
            for own_move in p1_moves:
                if any(all(self.payoff_mat[own_move][opponent_move][0] < self.payoff_mat[m2][opponent_move][0]
                           for opponent_move in p2_moves) for m2 in p1_moves if m2 != own_move):
                    dominated_rows.append(own_move)

            # dominated moves for p2, column elimination
            for opp_move in p2_moves:
                if any(all(self.payoff_mat[player_move][opp_move][1] < self.payoff_mat[player_move][m2][1]
                           for player_move in p1_moves) for m2 in p2_moves if
                       m2 != p2_moves.index(opp_move)):
                    dominated_columns.append(opp_move)

            # Update the payoff matrix by removing dominated rows and columns
            tmp = {own_move: {opp_move: self.payoff_mat[own_move][opp_move]
                              for opp_move in p2_moves if opp_move not in dominated_columns}
                   for own_move in p1_moves if own_move not in dominated_rows}
            self.payoff_mat = tmp

    def remove_dominated_strategies(self) -> None:
        """
            From the payoff matrix previously built, search for strictly or weakly dominated strategies and remove them
            from the matrix. Dominated strategies are removed for player and opponent (suppose the opponent won't play
            such moves). Only remove strategies dominated by other pure strategy.
        """

        dominated_rows, dominated_columns = [None], [None]

        while dominated_columns or dominated_rows:
            p1_moves = list(self.payoff_mat)
            p2_moves = list(self.payoff_mat[p1_moves[0]])
            dominated_columns.clear()
            dominated_rows.clear()

            # dominated moves for p1, line eliminations
            for p1_move in p1_moves:
                if any(all(self.payoff_mat[p1_move][opponent_move][0] <= self.payoff_mat[m2][opponent_move][0] for
                           opponent_move in p2_moves) for m2 in p1_moves if m2 != p1_move):
                    dominated_rows.append(p1_move)

            if len(dominated_rows) == len(self.payoff_mat):  # all moves removable, keep 1
                dominated_rows = dominated_rows[1:]

            # dominated moves for p2, column elimination
            for p2_move in p2_moves:
                if any(all(self.payoff_mat[player_move][p2_move][1] <= self.payoff_mat[player_move][m2][1]
                           for player_move in p1_moves) for m2 in p2_moves if m2 != p2_moves.index(p2_move)):
                    dominated_columns.append(p2_move)

            if len(dominated_columns) == len(self.payoff_mat[p1_moves[0]]):
                dominated_columns = dominated_columns[1:]

            # Update the payoff matrix by removing dominated rows and columns
            tmp = {p1_move: {p2_move: self.payoff_mat[p1_move][p2_move]
                             for p2_move in p2_moves if p2_move not in dominated_columns}
                   for p1_move in p1_moves if p1_move not in dominated_rows}
            self.payoff_mat = tmp

    def nash_equilibrium_for_move(self) -> tuple[tuple[np.array, np.array], np.array]:
        """
            Search the Nash equilibria of the game in self.payoff_mat and return the most promising with its expected
            payoffs.
            If the game has multiple Nash equilibria, check if some are Pareto optimal (and discard others). If several
            moves are Pareto optimal (or none of them are), a selection is made based on the standard deviations of
            players' expected payoffs. The stdev is used to favor strategies where payoffs are similar for both
            players to strategies where one of them has significantly larger payoff than the other. Ex.: if the NE are
            (1, 0), (0, 1), (0.5, 0.5), they all have same arithmetic mean but only the last one has null stdev,
            and it is reasonable to consider that last choice as a good compromise between the individually best and
            worst possible outcomes. Finally, if several NE still remain, a random selection is performed.

            :return: probability distribution over the choices of each player corresponding to the NE and the related
                expected payoffs
        """

        # Find Nash equilibria
        mat = self.payoff_mat
        p1_poffs = np.array([[mat[k1][k2][0] for k2 in mat[k1].keys()] for k1 in mat.keys()])
        p2_poffs = np.array([[mat[k1][k2][1] for k2 in mat[k1].keys()] for k1 in mat.keys()])
        game = nash.Game(p1_poffs, p2_poffs)
        neq = list(game.support_enumeration())

        if not len(neq) % 2:  # if game is degenerate, remove dominated strategies
            self.remove_dominated_strategies()
            mat = self.payoff_mat
            p1_poffs = np.array([[mat[k1][k2][0] for k2 in mat[k1].keys()] for k1 in mat.keys()])
            p2_poffs = np.array([[mat[k1][k2][1] for k2 in mat[k1].keys()] for k1 in mat.keys()])
            game = nash.Game(p1_poffs, p2_poffs)
            neq = list(game.support_enumeration())
        exp_payoffs = [game[p1_po, p2_po] for p1_po, p2_po in neq]

        # If no NE returned, rest of this function will consider all pure strategies in place of equilibria
        if not neq:
            nb_mv_p1 = len(mat.keys())
            nb_mv_p2 = len(mat[[k for k in mat.keys()][0]].keys())
            for i, p1m in enumerate(self.payoff_mat.keys()):
                for j, p2m in enumerate(self.payoff_mat[p1m].keys()):
                    p1_mv_idx = [0] * i + [1] + [0] * (nb_mv_p1 - i)
                    p2_mv_idx = [0] * j + [1] + [0] * (nb_mv_p2 - j)
                    neq.append((np.array(p1_mv_idx), np.array(p2_mv_idx)))
                    exp_payoffs.append(mat[p1m][p2m])

        # If there are several NE, try to discard some via Pareto optimality
        non_pareto_idx = list()
        if len(neq) > 1:
            for ne1_idx in range(len(neq)):
                for ne2_idx in range(len(neq)):
                    if ne1_idx != ne2_idx:
                        # check if exists other NE whose payoffs are always >= and > for at least one
                        ne1_better = exp_payoffs[ne1_idx][0] >= exp_payoffs[ne2_idx][0] and exp_payoffs[ne1_idx][1] >= \
                                     exp_payoffs[ne2_idx][1]
                        ne1_better &= exp_payoffs[ne1_idx][0] > exp_payoffs[ne2_idx][0] or exp_payoffs[ne1_idx][1] > \
                                      exp_payoffs[ne2_idx][1]
                        if ne1_better and ne2_idx not in non_pareto_idx:
                            non_pareto_idx.append(ne2_idx)

            if len(non_pareto_idx) < len(neq):
                for idx in sorted(non_pareto_idx, reverse=True):
                    del neq[idx]
                    del exp_payoffs[idx]

        # If still several NE, keep the one with the lowest stdev for both player's payoffs
        if len(neq) > 1:
            std = list()
            min_std = float('inf')
            for po in exp_payoffs:
                cur_std = stdev(po)
                std.append(cur_std)
                max_avg = min(min_std, cur_std)

            for idx in range(len(neq) - 1, -1, -1):
                if std[idx] > min_std:
                    del neq[idx]
                    del exp_payoffs[idx]

        # If still several NE, choose one randomly (otherwise, selection allows to remove useless remaining list shape)
        idx = random.randrange(len(neq))
        neq, exp_payoffs = neq[idx], exp_payoffs[idx]

        return neq, exp_payoffs

    def regular_move(self):
        """
            Considering the current payoff matrix, choose an action for the player normal condition (not a post-faint
            replacement)

            :return: Selected move
        """

        fill_game_with_estimation(self.role, self.game)
        self.build_payoff_matrix()
        probs, po = self.nash_equilibrium_for_move()
        probs = probs[0] if self.role == "p1" else probs[1]

        # choose random move considering prob distribution
        pick = 1 - random.random()  # ensure it's never 0
        for i, p in enumerate(probs):
            if pick <= p:
                break

        # corresponding move name in payoff matrix
        return [k for k in self.payoff_mat.keys()][i] if self.role == "p1" else \
            [k2 for k2 in self.payoff_mat[[k1 for k1 in self.payoff_mat.keys()][0]].keys()][i]

    def post_faint_move(self):
        """
            Considering the current payoff matrix, choose a post-faint replacement for the player. The selection is
            performed based on games induced by the different possible switches (the one offering the most promising
            situation determines the switch).

            :return: Selected move
        """

        save_game = deepcopy(self.game)
        mvs_and_expo = list()

        # generate games induced by possible switches
        for m in self.game.get_moves_from_state(self.role, self.game.get_player_view(self.role)):
            p1m, p2m = [m, None][::(-1) ** (self.role == "p2")]
            self.game.play_round(p1m, p2m, 0.95, None)
            fill_game_with_estimation(self.role, self.game)
            self.build_payoff_matrix()

            # see actions possible from induced game state
            mvs_and_expo.append((m, self.nash_equilibrium_for_move()[1][int(self.role == "p2")]))

            self.game = deepcopy(save_game)

        # check which switch allows most promising payoff
        return max(mvs_and_expo, key=lambda x: x[1])[0]

    def make_move(self, game: PokeGame):

        self.game = deepcopy(game)  # this agent modifies game state so local copy is made

        # opponent down
        if (not self.game.player1_view.on_field2.cur_hp and self.role == "p1" or
                not self.game.player2_view.on_field1.cur_hp and self.role == "p2"):
            move = None

        # ourselves down
        elif (not self.game.player1_view.on_field1.cur_hp and self.role == "p1" or
              not self.game.player2_view.on_field2.cur_hp and self.role == "p2"):
            move = self.post_faint_move()

        # regular conditions
        else:
            move = self.regular_move()

        return move
