from copy import deepcopy

from src.game.PokeGame import PokeGame
from src.game.Pokemon import Move
from src.game.constants import MIN_HP, MAX_HP, MIN_STAT, MAX_STAT, MIN_POW


def fill_game_with_estimation(role: str, game: PokeGame):
    """
        Provided PokeGame has some unknown values replaced with estimations. This is done to have a slightly better
        approximation than simply discarding actions concerning unknown Pokémons and moves.

        :param role: "p1" or "p2", depending on the player asking estimation for opponent team
        :param game: PokeGame object where the modifications will apply. (!) parameter is written and should be a copy
    """

    own_view, opp_view = [game.player1_view, game.player2_view][::(-1) ** (role == "p2")]
    own_view_own_team, own_view_opp_team = [own_view.team1, own_view.team2][::(-1) ** (role == "p2")]
    opp_view_own_team, opp_view_opp_team = [opp_view.team1, opp_view.team2][::(-1) ** (role == "p2")]

    # Give names of one team to the other (this reveals no sensitive info and allows to be coherent in the switches)
    plv_unknown_names = {p.name for p in opp_view_opp_team} - {p.name for p in own_view_opp_team}
    opv_unknown_names = {p.name for p in own_view_own_team} - {p.name for p in opp_view_own_team}
    for p, q in zip(own_view_opp_team, opp_view_own_team):
        if p.name is None:
            p.name = plv_unknown_names.pop()
        if q.name is None:
            q.name = opv_unknown_names.pop()

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
    for p in opp_view_own_team:
        for q in own_view_own_team:
            if p.name == q.name:
                if p.poke_type is None:
                    p.poke_type = "NOTYPE"
                    p.cur_hp, p.hp, p.atk, p.des, p.spe = ((MIN_HP + MAX_HP) // 2, (MIN_HP + MAX_HP) // 2,
                                                           (MIN_STAT + MAX_STAT) // 2, (MIN_STAT + MAX_STAT) // 2,
                                                           (MIN_STAT + MAX_STAT) // 2)

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
    if role == "p1":
        opp_view.team2 = deepcopy(own_view.team2)
        opp_view.on_field2 = opp_view.team2[
            [i for i, p in enumerate(opp_view.team2) if p.name == opp_view.on_field2.name][0]]
    else:
        opp_view.team1 = deepcopy(own_view.team1)
        opp_view.on_field1 = opp_view.team1[
            [i for i, p in enumerate(opp_view.team1) if p.name == opp_view.on_field1.name][0]]
