import copy

from src.agents.AbstractPlayer import AbstractPlayer
from src.game.PokeGame import PokeGame
from src.game.Pokemon import Move, Pokemon
from src.game.constants import MIN_POW, MIN_STAT, MAX_STAT


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
            simply discard actions concerning unknown Pokémon and moves)
        """

        own_view, opp_view = [self.game.player1_view, self.game.player2_view][::(-1) ** (self.role == "p2")]
        own_team, opp_team = [own_view.team1, own_view.team2][::(-1) ** (self.role == "p2")]
        opp_view_own_team = opp_view.team1 if self.role == "p1" else opp_view.team2

        # Unknown opponent Pokémon are default "NOTYPE" + average stat
        for i, p in enumerate(opp_team):
            if p.name is None:
                opp_team[i] = Pokemon("uk" + str(i), "NOTYPE", [(MIN_STAT + MAX_STAT) // 2] * 4,
                                      [Move("light_notype", "NOTYPE", MIN_POW)] + [Move(None, None, None)] * 2)

        # Own Pokémon unknown to opponent are set to default, real stats are provided for Pokémon already seen
        for i, p in enumerate(opp_view_own_team):
            if p.name is None:
                opp_view_own_team[i] = Pokemon("uk" + str(i), "NOTYPE", [(MIN_STAT + MAX_STAT) // 2] * 4,
                                               [Move("light_notype", "NOTYPE", MIN_POW)] + [Move(None, None, None)] * 2)
            else:
                if p.atk is None:
                    p.atk = own_team[[i for i, q in enumerate(own_team) if q.name == p.name][0]].atk
                if p.des is None:
                    p.des = own_team[[i for i, q in enumerate(own_team) if q.name == p.name][0]].des
                if p.spe is None:
                    p.spe = own_team[[i for i, q in enumerate(own_team) if q.name == p.name][0]].spe

        # All Pokémon have at least 1 STAB of MIN_POW
        for p in opp_team:
            if p.poke_type not in (m.move_type for m in p.moves):
                unknown_idx = [m.move_type for m in p.moves].index(None)
                p.moves[unknown_idx] = Move("light_" + p.poke_type, p.poke_type, MIN_POW)

        for p in opp_view_own_team:
            if p.poke_type not in (m.move_type for m in p.moves):
                unknown_idx = [m.move_type for m in p.moves].index(None)
                p.moves[unknown_idx] = Move("light_" + p.poke_type, p.poke_type, MIN_POW)

        # Team of the opponent is considered our view of it (no access to supposedly unknown elements)
        if self.role == "p1":
            opp_view.team2 = copy.deepcopy(own_view.team2)
            opp_view.on_field2 = opp_view.team2[[i for i, p in enumerate(opp_view.team2) if p.name == opp_view.on_field2.name][0]]
        else:
            opp_view.team1 = copy.deepcopy(own_view.team1)
            opp_view.on_field1 = opp_view.team1[[i for i, p in enumerate(opp_view.team1) if p.name == opp_view.on_field1.name][0]]

    def build_payoff_matrix(self):

        own_view, opp_view = [self.game.player1_view, self.game.player2_view][::(-1) ** (self.role == "p2")]
        own_of, opp_of = [own_view.on_field1, own_view.on_field2][::(-1) ** (self.role == "p2")]
        payoff_mat = dict()

        own_ops = [v for v in self.game.get_moves_from_state(self.role, own_view) if v is not None]
        opp_ops = [v for v in self.game.get_moves_from_state("p1" if self.role == "p2" else "p2", opp_view) if v is not None]

        for m1 in own_ops:
            if m1 not in payoff_mat.keys():
                payoff_mat[m1] = dict()
            for m2 in opp_ops:
                payoff_mat[m1][m2] = dict()

        return payoff_mat

    def make_move(self, game: PokeGame):
        self.game = copy.deepcopy(game)
        self.fill_game_with_estimation()
        payoff_matrix = self.build_payoff_matrix()

        return payoff_matrix
