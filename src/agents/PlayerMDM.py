import random

from src.agents.AbstractPlayer import AbstractPlayer
from src.game.PokeGame import PokeGame
from src.game.constants import TYPE_CHART


class PlayerMDM(AbstractPlayer):
    """
        Most damaging move: select action that will deal the greatest amount of damage considering the current state
    """

    def __init__(self, role: str):
        super().__init__(role)

    def make_move(self, game: PokeGame):
        view = game.get_player_view(self.role)
        own_of, other_of = [view.on_field1, view.on_field2][::(-1) ** (self.role == "p2")]

        if own_of.cur_hp == 0:  # must switch
            ret = random.choice(game.get_moves_from_state(self.role, game.game_state))

        else:
            # Damage potential of a move is defined by its final power (considering enemy weakness and STAB)
            moves_final_pow = list()
            for m in own_of.moves:
                moves_final_pow += [m.base_pow * TYPE_CHART[
                    m.move_type][other_of.poke_type] * (1 + 0.5 * (m.move_type == own_of.poke_type))]
            ret = own_of.moves[max(enumerate(moves_final_pow), key=lambda x: x[1])[0]].name

        return ret
