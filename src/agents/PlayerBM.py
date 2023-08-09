import random

from src.agents.AbstractPlayer import AbstractPlayer
from src.game.PokeGame import PokeGame
from src.game.constants import TYPE_CHART


class PlayerBM(AbstractPlayer):
    """
        Balanced move: Attack if player has stronger offensive option than opponent, switch to the safest alternative
        otherwise
    """

    def __init__(self, role: str):
        super().__init__(role)

    def make_move(self, game: PokeGame):
        view = game.get_player_view(self.role)
        own_of, other_of = [view.on_field1, view.on_field2][::(-1) ** (self.role == "p2")]
        own_team = view.team1 if self.role == "p1" else view.team2

        if own_of.cur_hp == 0:
            ret = random.choice(game.get_moves_from_state(self.role, game.game_state))

        else:
            # Player offensive possibilities
            own_moves_final_pow = list()
            for m in own_of.moves:
                own_moves_final_pow += [m.base_pow * TYPE_CHART[
                    m.move_type][other_of.poke_type] * (1 + 0.5 * (m.move_type == own_of.poke_type))]

            # Opponent offensive possibilities
            opp_moves_final_pow = list()
            for m in other_of.moves:
                if m.name is not None:
                    opp_moves_final_pow += [m.base_pow * TYPE_CHART[
                        m.move_type][own_of.poke_type] * (1 + 0.5 * (m.move_type == other_of.poke_type))]

            # Player defensive possibilities
            if len(opp_moves_final_pow):
                own_def_ops = list()
                for p in own_team:
                    own_def_ops.append(list())
                    for m in other_of.moves:
                        if m.name is not None:
                            own_def_ops[-1].append(m.base_pow * TYPE_CHART[
                                m.move_type][p.poke_type] * (1 + 0.5 * (m.move_type == other_of.poke_type)))
                own_def_ops = [max(ops) for ops in own_def_ops]
                safest_switch_idx = min(enumerate(own_def_ops), key=lambda x: x[1])[0]

            # No info about opponent moves, player has strongest option or safest switch is current Pokémon: use strongest move
            if not len(opp_moves_final_pow) or max(opp_moves_final_pow) <= max(own_moves_final_pow) or safest_switch_idx == 0:
                ret = own_of.moves[max(enumerate(own_moves_final_pow), key=lambda x: x[1])[0]].name

            # Defense is more rewarding than attack
            else:
                ret = "switch " + own_team[safest_switch_idx].name

        return ret
