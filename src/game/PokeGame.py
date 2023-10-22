import copy
import random
from math import floor, ceil

from src.game.Pokemon import Pokemon, Move
from src.game.constants import TYPES_INDEX, TYPE_CHART, MOVES, MIN_STAT, MAX_STAT


class TeamSpecs:
    def __init__(self):
        self.on_field1_idx = int()
        self.team1 = list()
        self.on_field2_idx = int()
        self.team2 = list()


class PokeGame:
    class GameStruct:
        """  Contains all information needed to represent a game state """

        def __init__(self, teams_specs):
            self.team1 = list()
            self.team2 = list()

            for spec, team in zip(teams_specs, [self.team1, self.team2]):
                for p in spec:
                    moves = list()
                    for atk in p[1]:
                        moves.append(Move(atk[0], atk[1], atk[2]))
                    team.append(Pokemon(p[0][0], p[0][1], p[0][2:6], moves))

            self.on_field1 = self.team1[0]
            self.on_field2 = self.team2[0]

        def __eq__(self, other):
            """ Consider Pokémon and attacks must be in same order """

            test = True
            # teams
            for ts, to in zip((self.team1, self.team2), (other.team1, other.team2)):
                for ps, po in zip(ts, to):
                    test &= ps == po and ps.cur_hp == po.cur_hp  # as we are comparing states, cur_hp of Pokémon matters

            # on-field (names are unique per team)
            test &= self.on_field1.name == other.on_field1.name
            test &= self.on_field2.name == other.on_field2.name

            return test

        def __str__(self):
            out = "~team1~\nof1: {}\n\n".format(self.on_field1)
            for i, p in enumerate(self.team1):
                out += "{}. {}\n".format(i, p)

            out += "\n~team2~\nof2: {}\n\n".format(self.on_field2)
            for i, p in enumerate(self.team2):
                out += "{}. {}\n".format(i, p)

            return out

    def __init__(self, teams_specs):
        """
            'team_specs' has the following shape:

            [[( (t1_p1_name, t1_p1_type, p1_hp, p1_atk, ...), ((a1_name, a1_type, a1_pow), ...) ), (t1_p2_hp, ...), ...],
             [( (t2_p1_name, ...), ... ), ...]]
        """

        self.game_state: PokeGame.GameStruct = PokeGame.GameStruct(teams_specs)
        # For player pov, opponent team unknown (NB: suppose all Pokémon have same # of attacks)
        unknown_specs = [(tuple([None for _ in range(6)]), tuple([(None, None, None) for _ in range(len(teams_specs[0][0][1]))]))]
        self.player1_view: PokeGame.GameStruct = PokeGame.GameStruct([teams_specs[0]] + [unknown_specs * len(teams_specs[1])])
        self.player2_view: PokeGame.GameStruct = PokeGame.GameStruct([unknown_specs * len(teams_specs[0])] + [teams_specs[1]])

        # Players witness name, type and hp of first opponent Pokémon (+ know they have a light power STAB)
        p2_lead_view, p2_lead_src = self.player1_view.team2[0], self.game_state.on_field2
        p2_lead_view.name, p2_lead_view.poke_type, p2_lead_view.hp, p2_lead_view.cur_hp = (p2_lead_src.name,
                                                                                           p2_lead_src.poke_type,
                                                                                           p2_lead_src.cur_hp,
                                                                                           p2_lead_src.hp)

        p1_lead_view, p1_lead_src = self.player2_view.team1[0], self.game_state.on_field1
        p1_lead_view.name, p1_lead_view.poke_type, p1_lead_view.hp, p1_lead_view.cur_hp = (p1_lead_src.name,
                                                                                           p1_lead_src.poke_type,
                                                                                           p1_lead_src.cur_hp,
                                                                                           p1_lead_src.hp)

    def __eq__(self, other):
        return self.game_state == other.game_state and self.player1_view == other.player1_view and self.player2_view == other.player2_view

    def __str__(self):
        return " complete view:\n{}\n player1 view:\n{}\n player2 view\n{}".format(self.game_state, self.player1_view,
                                                                                   self.player2_view)

    def get_numeric_repr(self, state: GameStruct = None, player: str = None):
        """ Converts the provided state in binary vector

        :param state: GameStruct object to be converted. If None, use attributes
        :param player: "p1" or "p2", indicating which view must be converted
        :return: list of int representing schematically the state
        """

        if state is None:
            if player == "p1":
                state = self.player1_view
            elif player == "p2":
                state = self.player2_view
            else:
                return None

        num_state = list()
        for t, of in zip([state.team1, state.team2], [state.on_field1, state.on_field2]):
            for p in [of] + [p for p in t if p.name != of.name]:
                mvs = list()
                for m in p.moves:
                    if m.name is None:
                        mvs += [None, None]
                    else:
                        mvs += [TYPES_INDEX[m.move_type], m.base_pow]
                if p.name is None:
                    num_state += [None, None, None, None, None, None] + mvs
                else:
                    num_state += [TYPES_INDEX[p.poke_type], p.cur_hp, p.hp, p.atk, p.des, p.spe] + mvs

        return [i if i is not None else 0 for i in num_state]

    def get_cur_state(self):
        return copy.deepcopy(self.game_state)

    def get_player_view(self, player: str):
        """
        Returns a copy of the GameStruct object related to specified player view

        :param player: "p1" or "p2" to indicate which player's view must be returned
        """

        return copy.deepcopy(self.player1_view) if player == "p1" else copy.deepcopy(self.player2_view)

    def get_moves_from_state(self, player: str, state: GameStruct):
        """
        Return possible moves for the specified player from the specified state (allows to retrieve possible moves
        for a player from a state that is not self.game_state)

        :param player: "p1" or "p2" to indicate for which player moves must be listed
        :param state: GameStruct object where moves must be searched
        :return: List of string containing name of moves playable.
        """

        state = state if state is not None else self.player1_view if player == "p1" else self.player2_view
        team, on_field, opp_on_field = (state.team1, state.on_field1, state.on_field2) if player == "p1" else (
            state.team2, state.on_field2, state.on_field1)

        if not opp_on_field.is_alive() and on_field.is_alive():
            # opponent faint but player not: only opponent moves (choosing replacement)
            return [None]

        switches = ["switch " + p.name for p in team if p.cur_hp > 0 and p.name != on_field.name]
        if not on_field.is_alive():
            moves = switches
        else:
            moves = [m.name for m in on_field.moves] + switches
        return moves

    def is_end_state(self, state=None):
        """
        Test if the provided or current state is an end state, meaning one of the players have all Pokémon with 0 cur_hp

        :param state: GameStruct object to test
        :return: bool value
        """

        state = state if state is not None else self.game_state
        return sum([p.is_alive() for p in state.team1]) == 0 or sum([p.is_alive() for p in state.team2]) == 0

    def first_player_won(self, state=None):
        """
        Check if some Pokémon from team1 are not dead. NB: a False value returned does not imply player2 won (game may
        be unfinished).

        :param state: PokeGame object to test.
        :return: bool value
        """

        state = state if state is not None else self.game_state
        return sum([p.is_alive() for p in state.team1]) > 0

    def swap_states(self, game_state: GameStruct):
        self.game_state = game_state

    def play_round(self, p1_move: str, p2_move: str, force_dmg: float = 0.0, force_order: bool = None):
        """
        Call functions related to move application (apply_player_moves & get_info_from_state), change inner and return
        information about what happened (whether any side fainted & who moved).

        :param p1_move: name of move selected by player 1
        :param p2_move: name of move selected by player 2
        :param force_dmg: parameter for apply_player_moves
        :param force_order: parameter for apply_player_moves
        :return: Python dict indicating which side has played a move and which side has fainted
        """

        # save start-of-turn information
        p1v_pre_of1, p1v_pre_of2 = self.player1_view.on_field1, self.player1_view.on_field2
        p2v_pre_of1, p2v_pre_of2 = self.player2_view.on_field1, self.player2_view.on_field2
        pre_of1_name, pre_of1_cur_hp, pre_of1_spe = (self.game_state.on_field1.name, self.game_state.on_field1.cur_hp,
                                                     self.game_state.on_field1.spe)
        pre_of2_name, pre_of2_cur_hp, pre_of2_spe = (self.game_state.on_field2.name, self.game_state.on_field2.cur_hp,
                                                     self.game_state.on_field2.spe)

        # apply moves
        # (move order is determined here to keep track of who moved first)
        order = random.choice([True, False]) if force_order is None else force_order

        # post faint switch or same priority level moves
        if (None in (p1_move, p2_move) or "switch" not in p1_move and "switch" not in p2_move or "switch" in p1_move and
                "switch" in p2_move):
            self.apply_player_moves(self.game_state, p1_move, p2_move, force_dmg=force_dmg, force_order=force_order)

        # attack and switch ("pre" values of the side switching must be updated to those of the switched pokémon)
        elif "switch" in p1_move and "switch" not in p2_move or "switch" not in p1_move and "switch" in p2_move:
            if "switch" in p1_move:
                self.apply_player_moves(self.game_state, p1_move, None, force_dmg=force_dmg, force_order=None)
                p1v_pre_of1, p2v_pre_of1 = self.player1_view.on_field1, self.player2_view.on_field1
                pre_of1_name, pre_of1_cur_hp, pre_of1_spe = (self.game_state.on_field1.name,
                                                             self.game_state.on_field1.cur_hp,
                                                             self.game_state.on_field1.spe)
                self.apply_player_moves(self.game_state, None, p2_move, force_dmg=force_dmg, force_order=None)
            else:
                self.apply_player_moves(self.game_state, None, p2_move, force_dmg=force_dmg, force_order=None)
                p2v_pre_of1, p2v_pre_of2 = self.player2_view.on_field1, self.player2_view.on_field2
                pre_of2_name, pre_of2_cur_hp, pre_of2_spe = (self.game_state.on_field2.name,
                                                             self.game_state.on_field2.cur_hp,
                                                             self.game_state.on_field2.spe)
                self.apply_player_moves(self.game_state, p1_move, None, force_dmg=force_dmg, force_order=None)

        # test if any side has fainted & which side moved (opponent lost hp or player switched) & who moved first
        p1_moved = False
        if p1_move is not None:
            p1_moved |= p1_move is not None and "switch" not in p1_move and\
                        (self.game_state.on_field1.cur_hp > 0 or
                         self.game_state.on_field1.spe > self.game_state.on_field2.spe or
                         self.game_state.on_field1.spe == self.game_state.on_field2.spe and order)
            p1_moved |= p2_move is None or "switch" in p1_move or "switch" in p2_move

        p2_moved = False
        if p2_move is not None:
            p2_moved |= p2_move is not None and "switch" not in p2_move and\
                        (self.game_state.on_field2.cur_hp > 0 or
                         self.game_state.on_field2.spe > self.game_state.on_field1.spe or
                         self.game_state.on_field1.spe == self.game_state.on_field2.spe and not order)
            p2_moved |= p1_move is None or "switch" in p1_move or "switch" in p2_move

        p1_first, p2_first = False, False
        # As switch and attacks have different priorities, no first mover will be considered in case of mix choice
        if None not in (p1_move, p2_move) and (
                "switch" in p1_move and "switch" in p2_move or "switch" not in p1_move and "switch" not in p2_move):
            p1_first = pre_of1_spe > pre_of2_spe
            p1_first |= pre_of1_spe == pre_of2_spe and order
            p2_first = not p1_first

        ret = {'p1_moved': p1_moved, 'p1_fainted': not self.game_state.on_field1.is_alive(), 'p1_first': p1_first,
               'p2_moved': p2_moved, 'p2_fainted': not self.game_state.on_field2.is_alive(), 'p2_first': p2_first}

        # player get new information
        self.directly_available_info("p1", p2_move, ret)
        self.directly_available_info("p2", p1_move, ret)

        if None not in (p1_move, p2_move):
            # post faint switch, no useful info to gather
            self.statistic_estimation("p1", ret, p1_move, p2_move, (pre_of1_name, pre_of1_cur_hp, p1v_pre_of1.spe),
                                      (pre_of2_name, pre_of2_cur_hp, p1v_pre_of2.spe))
            self.statistic_estimation("p2", ret, p2_move, p1_move, (pre_of2_name, pre_of2_cur_hp, p2v_pre_of2.spe),
                                      (pre_of1_name, pre_of1_cur_hp, p2v_pre_of1.spe))

        return ret

    @staticmethod
    def damage_formula(move: Move, attacker: Pokemon, target: Pokemon, force_dmg: float = 0.0):
        """
        Compute the amount of damage caused by the move used in specified conditions.

        :param move: Move object corresponding to attack used
        :param attacker: Pokémon object corresponding to the Pokémon using the move
        :param target: Pokémon object corresponding to the Pokémon receiving the move
        :param force_dmg: if between 0.85 and 1: used as substitution of random parameter (force value of multiplier),
            otherwise: generate random number.
        :return: Number of damage caused, as an integer
        """

        if move is None:
            return 0

        # base damage
        dmg = (floor(floor((2 * 100 / 5 + 2) * move.base_pow * attacker.atk / target.des) / 50) + 2)

        # modifiers
        rd = force_dmg if 0.85 <= force_dmg <= 1 else random.randint(85, 100) / 100
        stab = 1.5 if move.move_type == attacker.poke_type else 1
        type_aff = TYPE_CHART[move.move_type][target.poke_type]
        dmg *= rd * stab * type_aff
        if 0 < dmg < 1:
            dmg = 1

        return floor(dmg)

    def apply_player_moves(self, game_state: GameStruct, p1_move: str | None, p2_move: str | None, force_dmg: float = 0.0,
                           force_order: bool = None):
        """
        Execute player choices with regard to game rules to the game_state passed as parameter. This function applies
        changes on a parameter game_state and not on the attribute because some strategies require to test potential
        result on several game states.

        :param game_state: GameState object on which to apply the moves (NB: in general, used with the "complete"
            game_state, not a player view)
        :param p1_move: name of attack or 'switch {name}'
        :param p2_move: same
        :param force_dmg: if float between 0.85 and 1, will be used to force damage random factor
        :param force_order: if both players attack and have same speed, force_order=True will make p1 move first, False
            will make p2 move first, None will leave the order be determined randomly
        :return: provided game_state with players action applied
        """

        # both switch
        if p1_move is not None and "switch" in p1_move and p2_move is not None and "switch" in p2_move:
            game_state.on_field1 = game_state.team1[[n.name for n in game_state.team1].index(p1_move.split(" ")[1])]
            game_state.on_field2 = game_state.team2[[n.name for n in game_state.team2].index(p2_move.split(" ")[1])]

        # p1 switch
        elif p1_move is not None and "switch" in p1_move:
            game_state.on_field1 = game_state.team1[[n.name for n in game_state.team1].index(p1_move.split(" ")[1])]
            if p2_move is not None:
                game_state.on_field1.cur_hp = max(0, game_state.on_field1.cur_hp - self.damage_formula(
                    game_state.on_field2.move_from_name(p2_move), game_state.on_field2, game_state.on_field1,
                    force_dmg))

        # p2 switch
        elif p2_move is not None and "switch" in p2_move:
            game_state.on_field2 = game_state.team2[[n.name for n in game_state.team2].index(p2_move.split(" ")[1])]
            if p1_move is not None:
                game_state.on_field2.cur_hp = max(0, game_state.on_field2.cur_hp - self.damage_formula(
                    game_state.on_field1.move_from_name(p1_move), game_state.on_field1, game_state.on_field2,
                    force_dmg))

        # both attack (nb: should never be both None at same time)
        elif None not in (p1_move, p2_move):
            # first, determine attack order
            attack_order = [(game_state.on_field1, p1_move, 'p1'), (game_state.on_field2, p2_move, 'p2')]
            if game_state.on_field1.spe > game_state.on_field2.spe:
                pass
            elif game_state.on_field1.spe < game_state.on_field2.spe:
                attack_order.reverse()
            else:
                if force_order is None:
                    random.shuffle(attack_order)
                elif not force_order:
                    attack_order.reverse()

            attack_order[1][0].cur_hp = max(0, attack_order[1][0].cur_hp - self.damage_formula(
                attack_order[0][0].move_from_name(attack_order[0][1]), attack_order[0][0], attack_order[1][0],
                force_dmg))
            # second attacker must be alive to attack
            if attack_order[1][0].is_alive():
                attack_order[0][0].cur_hp = max(0, attack_order[0][0].cur_hp - self.damage_formula(
                    attack_order[1][0].move_from_name(attack_order[1][1]), attack_order[1][0], attack_order[0][0],
                    force_dmg))

        # p1/p2 attacks after a switch of the other
        else:
            attacker, target = tuple([game_state.on_field1, game_state.on_field2][::(-1) ** (p1_move is None)])
            move = attacker.move_from_name(p1_move if p1_move is not None else p2_move)
            target.cur_hp = max(0, target.cur_hp - self.damage_formula(move, attacker, target, force_dmg))

        return game_state

    def directly_available_info(self, player: str, opponent_move: str, turn_res: dict):
        """
        Update player view with directly available information, information seen during the round (attack used by
        opponent, type and hp of Pokémon switched).

        :param player: "p1" or "p2", indicating whether information is searched for player1 or player2
        :param opponent_move: Name of move performed by opponent player
        :param turn_res: "ret" object from "play_move" function
        :return: None but update internal state
        """

        real_own, real_other = (self.game_state.on_field1, self.game_state.on_field2) if player == "p1" else (
            self.game_state.on_field2, self.game_state.on_field1)
        own_team, other_team = (self.player1_view.team1, self.player1_view.team2) if player == "p1" else (
            self.player2_view.team2, self.player2_view.team1)

        # Own on-field
        own_of = own_team[[i for i, p in enumerate(own_team) if p.name == real_own.name][0]]
        # update player view reference to on-field
        if player == "p1":
            self.player1_view.on_field1 = own_of
        elif player == "p2":
            self.player2_view.on_field2 = own_of
        own_of.cur_hp = real_own.cur_hp

        # Opponent on-field (test if opponent switched, potentially on previously unseen Pokémon)
        already_seen = real_other.name in [p.name for p in other_team]
        other_of = other_team[[p.name for p in other_team].index(real_other.name if already_seen else None)]

        # update player view of reference
        if player == "p1":
            self.player1_view.on_field2 = other_of
        elif player == "p2":
            self.player2_view.on_field1 = other_of

        # HP and type changes (visible information)
        other_of.name, other_of.poke_type, other_of.cur_hp, other_of.hp = (real_other.name, real_other.poke_type,
                                                                           real_other.cur_hp, real_other.hp)

        # Attack used
        if opponent_move is not None and opponent_move not in [m.name for m in other_of.moves] and\
                "switch" not in opponent_move and turn_res["p2_moved" if player == "p1" else "p1_moved"]:  # opponent used previously unseen attack
            unknown_move_index = [m.move_type for m in other_of.moves].index(None)
            move = Move(opponent_move, *MOVES[opponent_move])
            other_of.moves[unknown_move_index] = move

    @staticmethod
    def reverse_attack_calculator(move: Move, attacker: Pokemon, target: Pokemon, hp_loss: int):
        """
        From a move, target and hp loss, compute the minimum value that the attack stat must have had.
        NB: Some parts of the damage formula make the inverse calculation not perfectly computable:
         - floor divisions
         - random factor
        Therefore, a lower and upper bound are considered.

        :param move: Move object corresponding to attack used
        :param attacker: Pokémon object corresponding to the Pokémon using the move
        :param target: Pokémon object corresponding to the Pokémon receiving the move
        :param hp_loss: Amount of health point lost by target
        :return: Lowest and highest estimations of statistic
        """

        stab = 1.5 ** (move.move_type == attacker.poke_type)
        type_aff = TYPE_CHART[move.move_type][target.poke_type]
        if not type_aff:
            # no info from no hp_loss (plus, it would trigger a zero division)
            return None, None

        lo_num, lo_den = (50 * target.des * ceil(hp_loss / (1 * stab * type_aff) - 2)), (42 * move.base_pow)
        hi_num, hi_den = (50 * target.des * ceil((hp_loss + 1) / (0.85 * stab * type_aff) - 2)), (42 * move.base_pow)
        if 0 in (lo_den, hi_den):
            # if hp_loss is very small, den ends up in 2 - 2, but such case gives no useful info & it's just ignored
            return None, None

        lo, hi = ceil(lo_num / lo_den), floor(hi_num / hi_den)
        lo, hi = min(MAX_STAT, max(MIN_STAT, lo)), min(MAX_STAT, max(MIN_STAT, hi))
        return lo, hi

    @staticmethod
    def reverse_defense_calculator(move: Move, attacker: Pokemon, target: Pokemon, hp_loss: int):
        """
        From a move, attacker and hp loss, compute the minimum value that the defense stat must have had. If estimation
        cannot be made (too few remaining HP), None value is returned.

        :param move: Move object corresponding to attack used
        :param attacker: Pokémon object corresponding to the Pokémon using the move
        :param target: Pokémon object corresponding to the Pokémon receiving the move
        :param hp_loss: Amount of health point lost by target
        :return: Lowest and highest estimations of statistic
        """

        stab = 1.5 ** (move.move_type == attacker.poke_type)
        type_aff = TYPE_CHART[move.move_type][target.poke_type]
        if not type_aff:
            # no info from no hp_loss (plus, it would trigger a zero division)
            return None, None

        lo_num, lo_den = (42 * move.base_pow * attacker.atk), (50 * ceil((hp_loss + 1) / (0.85 * stab * type_aff) - 2))
        hi_num, hi_den = (42 * move.base_pow * attacker.atk), (50 * ceil(hp_loss / (1 * stab * type_aff) - 2))
        if 0 in (lo_den, hi_den):
            # if hp_loss is very small, den ends up in 2 - 2, but such case gives no useful info & it's just ignored
            return None, None

        lo, hi = ceil(lo_num / lo_den), floor(hi_num / hi_den)
        lo, hi = min(MAX_STAT, max(MIN_STAT, lo)), min(MAX_STAT, max(MIN_STAT, hi))
        return lo, hi

    @staticmethod
    def estimate_speed(player_first: bool, own_move: str, opp_move: str, own_spe: int, opp_spe: int):
        """
        From the observation of the order of action, make an estimation of the speed that the opponent should have.
        The estimation is an upper estimation.

        :param player_first: boolean value indicating whether player moved first.
        :param own_move: name of move chosen by player
        :param opp_move: name of move chosen by the opponent
        :param own_spe: speed player's Pokémon that was on field at the moment of the action
        :param opp_spe: same for opponent (player estimation)
        :return: estimation of the speed statistic of opp_of
        """

        est = opp_spe
        if None not in (own_move, opp_move) and (
                "switch" in own_move and "switch" in opp_move or "switch" not in own_move and "switch" not in opp_move):
            # switches and normal attacks have different level of priority and cannot be compared
            if player_first:
                est = own_spe - 1 if opp_spe is None else min(opp_spe, own_spe - 1)
            else:
                est = 140 if opp_spe is None else max(opp_spe, own_spe + 1)

        return est

    def statistic_estimation(self, player: str | None, turn_res: dict, own_move: str, opp_move: str,
                             pre_own_of: tuple[str, int, int],
                             pre_opp_of: tuple[str, int, int]):
        """
        Call reverse defense and attack calculator and set an estimation of the opponent statistic in player view,
        based on damage dealt/received. Actual stat can be underestimated in case of faint (real amount of damage
        not shown).

        :param player: "p1" or "p2" indicating which player view is being estimated
        :param turn_res: "ret" object from "play_move" function
        :param own_move: name of move performed by player
        :param opp_move: name of move performed by opponent
        :param pre_own_of: (p.name, p.cur_hp, p.spe) of the on field Pokémon of the player at the beginning of the round
        :param pre_opp_of: Same for opponent
        :return: None but update player view
        """

        # aliases
        view = self.player1_view if player == "p1" else self.player2_view
        own_of, opp_of = (view.on_field1, view.on_field2) if player == "p1" else (view.on_field2, view.on_field1)
        own_team, opp_team = (view.team1, view.team2) if player == "p1" else (view.team2, view.team1)

        own_moved, own_fainted, own_first = ("p1_moved", "p1_fainted", "p1_first") if player == "p1" else (
            "p2_moved", "p2_fainted", "p2_first")
        own_moved, own_fainted, own_first = turn_res[own_moved], turn_res[own_fainted], turn_res[own_first]
        opp_moved, opp_fainted, opp_first = ("p2_moved", "p2_fainted", "p2_first") if player == "p1" else (
            "p1_moved", "p1_fainted", "p2_first")
        opp_moved, opp_fainted, opp_first = turn_res[opp_moved], turn_res[opp_fainted], turn_res[opp_first]

        # opponent attack
        if opp_moved and "switch" not in opp_move:
            hp_loss = pre_own_of[1] - own_of.cur_hp
            move = Move(opp_move, *MOVES[opp_move])

            # evaluate min and max possible value of stat landing the attack
            min_est, max_est = self.reverse_attack_calculator(move, opp_of, own_of, hp_loss)
            if max_est is not None:
                if not (own_fainted and opp_of.atk is not None):  # estimation is biased, keep old value
                    opp_of.atk = max(max_est, opp_of.atk) if opp_of.atk is not None else max_est

        # opponent defense
        if own_moved and "switch" not in own_move:
            hp_loss = pre_opp_of[1] - opp_of.cur_hp
            move = Move(own_move, *MOVES[own_move])

            min_est, max_est = self.reverse_defense_calculator(move, own_of, opp_of, hp_loss)
            if max_est is not None:
                if not (opp_fainted and opp_of.des is not None):
                    opp_of.des = max(max_est, opp_of.des) if opp_of.des is not None else max_est

        # opponent speed
        if "switch" in own_move and "switch" in opp_move:
            # if both sides switched, estimation is made for Pokémon withdrawn from field
            opp_old_of = opp_team[[i for i, p in enumerate(opp_team) if p.name == pre_opp_of[0]][0]]
            max_est = self.estimate_speed(own_first, own_move, opp_move, pre_own_of[2], pre_opp_of[2])
            opp_old_of.spe = max_est
        elif "switch" not in own_move and "switch" not in opp_move:
            max_est = self.estimate_speed(own_first, own_move, opp_move, own_of.spe, opp_of.spe)
            opp_of.spe = max_est
