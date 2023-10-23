import copy
import random

from src.agents.AbstractPlayer import AbstractPlayer
from src.game.PokeGame import PokeGame
from src.game.Pokemon import Move
from src.game.constants import MIN_POW, MIN_STAT, MAX_STAT, MIN_HP, MAX_HP

team_specs_for_game = [[(("p1", "FIRE", 100, 100, 100, 100),
                         (("light_psychic", "PSYCHIC", 50), ("light_fire", "FIRE", 50), ("light_bug", "BUG", 50))),
                        (("p2", "ELECTRIC", 100, 100, 100, 100),
                         (("light_grass", "GRASS", 50), ("light_electric", "ELECTRIC", 50),
                          ("light_ghost", "GHOST", 50))),
                        (("p3", "GRASS", 100, 100, 100, 100),
                         (("light_grass", "GRASS", 50), ("light_ice", "ICE", 50), ("light_fighting", "FIGHTING", 50)))],
                       [(("d1", "WATER", 100, 100, 100, 100),
                         (("light_steel", "STEEL", 50), ("light_water", "WATER", 50), ("light_fairy", "FAIRY", 50))),
                        (("d2", "DRAGON", 100, 100, 100, 100),
                         (("light_bug", "BUG", 50), ("light_dragon", "DRAGON", 50), ("light_ground", "GROUND", 50))),
                        (("d3", "BUG", 100, 100, 100, 100),
                         (("light_bug", "BUG", 50), ("light_normal", "NORMAL", 50), ("light_dark", "DARK", 50)))]]


class PlayerGT(AbstractPlayer):
    """
        Construct payoff matrix based on the knowledge of the given state and apply game theory algorithms (strictly
        dominated strategies elimination, Nash equilibrium search) to select most promising move
    """

    def __init__(self, role: str):
        super().__init__(role)
        self.game = None
        self.payoff_mat = None

    def fill_game_with_estimation(self):
        """
            Local copy of the game is filled with estimations (this is done to have a slightly better approximation than
            simply discard actions concerning unknown Pokémon)
        """

        own_view, opp_view = [self.game.player1_view, self.game.player2_view][::(-1) ** (self.role == "p2")]
        own_view_own_team, own_view_opp_team = [own_view.team1, own_view.team2][::(-1) ** (self.role == "p2")]
        opp_view_own_team, opp_view_opp_team = [opp_view.team1, opp_view.team2][::(-1) ** (self.role == "p2")]

        # Give names of one team to the other (this reveals no sensitive info and allows to be coherent in the switches)
        for p, q in zip(own_view_own_team + opp_view_opp_team, opp_view_own_team + own_view_opp_team):
            q.name = p.name

        # Unknown opponent Pokémon are default "NOTYPE" + average stat
        for p in own_view_opp_team:
            if p.poke_type is None:
                p.poke_type = "NOTYPE"

            if p.hp is None:
                p.cur_hp = p.hp = (MIN_HP + MAX_HP) // 2
            if p.atk is None:
                p.atk = (MIN_STAT + MAX_STAT) // 2
            if p.des is None:
                p.des = (MIN_STAT + MAX_STAT) // 2
            if p.spe is None:
                p.spe = (MIN_STAT + MAX_STAT) // 2

            # All Pokémon have at least 1 STAB of MIN_POW
            if p.poke_type not in (m.move_type for m in p.moves):
                unknown_idx = [m.move_type for m in p.moves].index(None)
                p.moves[unknown_idx] = Move("light_" + p.poke_type.lower(), p.poke_type, MIN_POW)

            # Remaining unknown move: consider 1 neutral move
            if "light_notype" not in (m.name for m in p.moves):
                for i, m in enumerate(p.moves):
                    if m.name is None:
                        p.moves[i] = Move("light_notype", "NOTYPE", MIN_POW)
                        break

        # Own Pokémons unknown to opponent are set to default, real stats are provided for Pokémon already seen
        for p, q in zip(opp_view_own_team, own_view_own_team):
            if p.poke_type is None:
                p.poke_type = "NOTYPE"
                p.cur_hp, p.hp, p.atk, p.des, p.spe = ((MIN_HP + MAX_HP) // 2, (MIN_HP + MAX_HP) // 2,
                                    (MIN_STAT + MAX_STAT) // 2, (MIN_STAT + MAX_STAT) // 2, (MIN_STAT + MAX_STAT) // 2)

            else:
                p.cur_hp, p.hp, p.atk, p.des, p.spe = q.cur_hp, q.hp, q.atk, q.des, q.spe

            # All Pokémon have at least 1 STAB of MIN_POW
            if p.poke_type not in (m.move_type for m in p.moves):
                unknown_idx = [m.move_type for m in p.moves].index(None)
                p.moves[unknown_idx] = Move("light_" + p.poke_type.lower(), p.poke_type, MIN_POW)

            # Remaining unknown moves: consider 1 neutral move
            if "light_notype" not in (m.name for m in p.moves):
                for i, m in enumerate(p.moves):
                    if m.name is None:
                        p.moves[i] = Move("light_notype", "NOTYPE", MIN_POW)
                        break

        # Team of the opponent is considered our view of it: we're not supposed to know its real choices and configs
        if self.role == "p1":
            opp_view.team2 = copy.deepcopy(own_view.team2)
            opp_view.on_field2 = opp_view.team2[
                [i for i, p in enumerate(opp_view.team2) if p.name == opp_view.on_field2.name][0]]
        else:
            opp_view.team1 = copy.deepcopy(own_view.team1)
            opp_view.on_field1 = opp_view.team1[
                [i for i, p in enumerate(opp_view.team1) if p.name == opp_view.on_field1.name][0]]

    @staticmethod
    def compute_player_payoff(state: PokeGame.GameStruct, player: str):
        p1_hp, p2_hp = sum([p.cur_hp for p in state.team1]), sum([p.cur_hp for p in state.team2])
        p1_max, p2_max = sum([p.hp for p in state.team1]), sum([p.hp for p in state.team2])
        p1_alive, p2_alive = sum([p.is_alive() for p in state.team1]), sum([p.is_alive() for p in state.team2])

        payoff = (-1) ** (player == "p2") * ((5 * p1_hp / p1_max) + (5 * p1_alive / len(state.team1))) + \
                 (-1) ** (player == "p1") * ((5 * p2_hp / p2_max) + (5 * p2_alive / len(state.team2)))

        return payoff

    def build_payoff_matrix(self):
        """
            Shape: [player action][opponent action]: (player payoff, opponent payoff)
                player is considered the same as in self.role
        """

        own_view, opp_view = [self.game.player1_view, self.game.player2_view][::(-1) ** (self.role == "p2")]
        opp_view_own_of, opp_view_opp_of = [opp_view.on_field1, opp_view.on_field2][::(-1) ** (self.role == "p2")]
        self.payoff_mat = dict()

        own_ops = [v for v in self.game.get_moves_from_state(self.role, own_view) if v is not None]
        opp_ops = [v for v in self.game.get_moves_from_state(list({"p1", "p2"} - {self.role})[0], opp_view) if
                   v is not None]

        for own_mv in own_ops:
            if own_mv not in self.payoff_mat.keys():
                self.payoff_mat[own_mv] = dict()

            for opp_mv in opp_ops:
                p1_mv, p2_mv = [own_mv, opp_mv][::(-1) ** (self.role == "p2")]

                eff_mv = own_mv if "switch" in own_mv or own_mv in (m.name for m in
                                                                    opp_view_own_of.moves) else "light_notype"
                # opponent might not know all player options

                own_po = self.compute_player_payoff(self.game.apply_player_moves(copy.deepcopy(own_view),
                                                                                 p1_mv, p2_mv, 0.95, False), self.role)
                p1_mv, p2_mv = (eff_mv, p2_mv) if self.role == "p1" else (p1_mv, eff_mv)
                opp_po = self.compute_player_payoff(self.game.apply_player_moves(copy.deepcopy(opp_view),
                                                                                 p1_mv, p2_mv, 0.95, False),
                                                    list({"p1", "p2"} - {self.role})[0])

                self.payoff_mat[own_mv][opp_mv] = (round(own_po, 3), round(opp_po, 3))
        print()

    def remove_strictly_dominated_strategies(self, player: int):
        """
            From the payoff matrix previously built, search for strictly dominated strategies and remove them from
            the matrix (for the provided player)

            :param player: 0 or 1, indicating the target value in the tuples
            :return: indicates if a modification has been performed
        """

        dominated_rows = []
        dominated_columns = []

        own_moves = list(self.payoff_mat.keys())
        try:
            opp_moves = list(self.payoff_mat[own_moves[0]].keys())
        except Exception as e:
            print()

        if not player:  # line elimination
            for own_move in own_moves:
                if any(all(self.payoff_mat[own_move][opponent_move][player] < self.payoff_mat[m2][opponent_move][player]
                           for opponent_move in opp_moves) for m2 in own_moves if m2 != own_move):
                    dominated_rows.append(own_move)

        else:  # column elimination
            for opp_move in opp_moves:
                if any(all(self.payoff_mat[player_move][opp_move][player] < self.payoff_mat[player_move][m2][player]
                           for player_move in own_moves) for m2 in opp_moves if
                       m2 != opp_moves.index(opp_move)):
                    dominated_columns.append(opp_move)

        # Update the payoff matrix by removing dominated rows and columns
        tmp = {own_move: {opp_move: self.payoff_mat[own_move][opp_move]
                          for opp_move in opp_moves if opp_move not in dominated_columns}
               for own_move in own_moves if own_move not in dominated_rows}
        self.payoff_mat = tmp

        return dominated_rows or dominated_columns

    def mixed_nash_equilibrium(self):
        """
            If the strictly dominated strategies elimination left several choices for the player, a randomized choice
            must be performed on the remaining moves

            :return: Selected move (name)
        """

        move = random.choice([k for k in self.payoff_mat.keys()])
        return move

    def regular_move(self):
        """
            Choose a move for regular game conditions
        """

        # determine best option
        while self.remove_strictly_dominated_strategies(0) or self.remove_strictly_dominated_strategies(1):
            continue

        if len(self.payoff_mat) > 1 and False:
            move = self.mixed_nash_equilibrium()
        else:
            move = list(self.payoff_mat.keys())[0]

        return move

    def post_faint_move(self):
        """
            Choose a move (more specifically, a switch) after current on-field fainted. The games induced by the
            different possible switches are evaluated and the most promising one determines the switch.
        """

        return

    def make_move(self, game: PokeGame):

        if self.game is None:
            # initializations + compute payoff matrix
            self.game = copy.deepcopy(game)
            self.fill_game_with_estimation()
            self.build_payoff_matrix()

        # opponent down
        if (not self.game.player1_view.on_field2.cur_hp and self.role == "p1" or
                not self.game.player2_view.on_field1.cur_hp and self.role == "p2"):
            move = None

        # ourselves down
        elif (not self.game.player1_view.on_field1.cur_hp and self.role == "p1" or
                not self.game.player2_view.on_field2.cur_hp and self.role == "p2"):
            move = self.post_faint_move()

        else:
            move = self.regular_move()

        return move


if __name__ == '__main__':

    for p in ["p1", "p2"]:
        game = PokeGame(team_specs_for_game)
        a1 = PlayerGT(p)
        a1.make_move(game)
        game.play_round("switch p2", "light_steel", 0.85, True)
        a1.make_move(game)

        pm = a1.payoff_mat

        for k in pm.keys():
            print(k, pm[k])
