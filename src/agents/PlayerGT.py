import copy

from src.agents.AbstractPlayer import AbstractPlayer
from src.game.PokeGame import PokeGame
from src.game.Pokemon import Move, Pokemon
from src.game.constants import MIN_POW, MIN_STAT, MAX_STAT, MIN_HP, MAX_HP

#MIN_HP, MAX_HP = 100, 100


class PlayerGT(AbstractPlayer):
    """
        Construct payoff matrix based on the knowledge of the given state and apply game theory algorithms (strictly
        dominated strategies elimination, Nash equilibrium search) to select most promising move
    """

    def __init__(self, role: str):
        super().__init__(role)
        self.game = None

    def fill_game_with_estimation(self):
        """
            Local copy of the game is filled with estimations (this is done to have a slightly better approximation than
            simply discard actions concerning unknown Pokémon)
        """

        own_view, opp_view = [self.game.player1_view, self.game.player2_view][::(-1) ** (self.role == "p2")]
        own_view_own_team, own_view_opp_team = [own_view.team1, own_view.team2][::(-1) ** (self.role == "p2")]
        opp_view_own_team, opp_view_opp_team = [opp_view.team1, opp_view.team2][::(-1) ** (self.role == "p2")]

        # Give names of one team to the other (this reveals no supposedly unknown information and allows to make switches match)
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

        # Own Pokémon unknown to opponent are set to default, real stats are provided for Pokémon already seen
        for p, q in zip(opp_view_own_team, own_view_own_team):
            if p.poke_type is None:
                p.poke_type = "NOTYPE"

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

        # Team of the opponent is considered our view of it (no access to supposedly unknown elements)
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
            Shape: [player1 action][player2 action]: (p1 payoff, p2 payoff)
        """

        own_view, opp_view = [self.game.player1_view, self.game.player2_view][::(-1) ** (self.role == "p2")]
        payoff_mat = dict()

        own_ops = [v for v in self.game.get_moves_from_state(self.role, own_view) if v is not None]
        opp_ops = [v for v in self.game.get_moves_from_state("p1" if self.role == "p2" else "p2", opp_view) if
                   v is not None]

        for own_mv in own_ops:
            if own_mv not in payoff_mat.keys():
                payoff_mat[own_mv] = dict()
            for opp_mv in (opp_ops if self.role == "p2" else own_ops):
                p1_v, p2_v = self.game.get_player_view("p1"), self.game.get_player_view("p2")

                eff_opp_mv = None
                p1_po = self.compute_player_payoff(self.game.apply_player_moves(p1_v, own_mv,
                        opp_mv if "switch" in opp_mv or opp_mv in (m.name for m in p1_v.on_field2.moves) else "light_notype", 0.95, False), "p1")
                p2_po = self.compute_player_payoff(self.game.apply_player_moves(p2_v,
                        own_mv if "switch" in own_mv or own_mv in (m.name for m in p2_v.on_field1.moves) else "light_notype", opp_mv, 0.95, False), "p2")

                payoff_mat[own_mv][opp_mv] = (round(p1_po, 3), round(p2_po, 3))

        return payoff_mat

    def make_move(self, game: PokeGame):
        self.game = copy.deepcopy(game)
        self.fill_game_with_estimation()
        payoff_matrix = self.build_payoff_matrix()

        return payoff_matrix


if __name__ == '__main__':

    team_specs_for_game = [[(("p1", "FIRE", 100, 100, 100, 100),
                             (("light_psychic", "PSYCHIC", 50), ("light_fire", "FIRE", 50))),
                            (("p2", "ELECTRIC", 100, 100, 100, 100),
                             (("light_grass", "GRASS", 50), ("light_electric", "ELECTRIC", 50)))],
                           [(("d1", "WATER", 100, 100, 100, 100),
                             (("light_steel", "STEEL", 50), ("light_water", "WATER", 50))),
                            (("d2", "DRAGON", 100, 80, 100, 100),
                             (("light_bug", "BUG", 50), ("light_dragon", "DRAGON", 50)))]]
    team_specs_for_gaze = [[(("p1", "FIRE", 100, 100, 100, 100),
                             (("light_psychic", "PSYCHIC", 50), ("light_fire", "FIRE", 50), ("light_bug", "BUG", 50))),
                            (("p2", "ELECTRIC", 100, 100, 100, 100),
                             (("light_grass", "GRASS", 50), ("light_electric", "ELECTRIC", 50), ("light_ghost", "GHOST", 50))),
                            (("p3", "GRASS", 100, 100, 100, 100),
                             (("light_grass", "GRASS", 50), ("light_ice", "ICE", 50), ("light_fighting", "FIGHTING", 50)))],
                           [(("d1", "WATER", 100, 100, 100, 100),
                             (("light_steel", "STEEL", 50), ("light_water", "WATER", 50), ("light_fairy", "FAIRY", 50))),
                            (("d2", "DRAGON", 100, 100, 100, 100),
                             (("light_bug", "BUG", 50), ("light_dragon", "DRAGON", 50), ("light_ground", "GROUND", 50))),
                            (("d3", "BUG", 100, 100, 100, 100),
                             (("light_bug", "BUG", 50), ("light_normal", "NORMAL", 50), ("light_dark", "DARK", 50)))]]

    gamez = PokeGame(team_specs_for_game)
    a1 = PlayerGT("p2")

    #gamez.play_round("light_psychic", "light_steel", 0.85, True)
    pm = a1.make_move(gamez)

    print("player1 view")
    print(a1.game.player1_view)
    print("player2 view")
    print(a1.game.player2_view)

    for k in pm.keys():
        print(k, pm[k])
