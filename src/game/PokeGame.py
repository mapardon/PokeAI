import copy
import random
from math import floor

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
                    team.append(Pokemon(p[0][0], p[0][1], p[0][2:8], moves))

            self.on_field1 = self.team1[0]
            self.on_field2 = self.team2[0]

        def __eq__(self, other):
            """ Consider Pokémon and attacks must be in same order """

            test = True
            # teams
            for ts, to in zip((self.team1, self.team2), (other.team1, other.team2)):
                for ps, po in zip(ts, to):
                    test &= ps == po and ps.cur_hp == po.cur_hp  # as we are comparing states, cur_hp of Pokémon matter

            # on-field
            test &= self.on_field1.name == other.on_field1.name
            test &= self.on_field2.name == other.on_field2.name

            return test

    def __init__(self, teams_specs):
        """
            'team_specs' has the following shape:

            [[( (t1_p1_name, t1_p1_type, p1_hp, p1_atk, ...), ((a1_name, a1_type, a1_pow), ...) ), (t1_p2_hp, ...), ...],
             [( (t2_p1_name, ...), ... ), ...]]
        """

        self.game_state: PokeGame.GameStruct = PokeGame.GameStruct(teams_specs)
        # For player pov, opponent team unknown
        unknown_specs = [(tuple([None for _ in range(8)]), tuple([(None, None, None, None) for _ in range(2)])) for _ in range(2)]
        self.player1_view: PokeGame.GameStruct = PokeGame.GameStruct([teams_specs[0]] + [unknown_specs])
        self.player2_view: PokeGame.GameStruct = PokeGame.GameStruct([unknown_specs] + [teams_specs[1]])

        # Players witness name, type and hp of first opponent Pokemon
        p2_lead_view, p2_lead_src = self.player1_view.team2[0], self.game_state.on_field2
        p2_lead_view.name, p2_lead_view.poke_type, p2_lead_view.hp, p2_lead_view.cur_hp = p2_lead_src.name, p2_lead_src.poke_type, p2_lead_src.cur_hp, p2_lead_src.hp
        p1_lead_view, p1_lead_src = self.player2_view.team1[0], self.game_state.on_field1
        p1_lead_view.name, p1_lead_view.poke_type, p1_lead_view.hp, p1_lead_view.cur_hp = p1_lead_src.name, p1_lead_src.poke_type, p1_lead_src.cur_hp, p1_lead_src.hp

    def get_numeric_repr(self, state):
        """ Converts the provided state (GameStruct) in binary vector shape """

        # TODO consider each side separately
        num_state = list()
        for t, of in zip([state.team1, state.team2], [state.on_field1, state.on_field2]):
            for p in [of] + [p for p in t if p.name != of.name]:
                mvs = list()
                for m in p.moves:
                    mvs += [TYPES_INDEX[m.move_type], m.base_pow]
                num_state += [TYPES_INDEX[p.poke_type], p.cur_hp, p.atk, p.des, p.spe] + mvs
        return num_state

    def get_cur_state(self):
        return copy.deepcopy(self.game_state)

    def get_player1_view(self):
        """ Returns a copy of the GameStruct object related to first player point of view """

        return copy.deepcopy(self.player1_view)

    def get_player2_view(self):
        """ Returns a copy of the GameStruct object related to second player point of view """

        return copy.deepcopy(self.player2_view)

    def get_moves_from_state(self, player, state):
        """ Return possible moves for the specified player from the specified state (allows to retrieve possible moves
         for a player from a state that is not self.game_state) """

        state = state if state is not None else self.player1_view if player == "p1" else self.player2_view
        team, on_field, opp_on_field = (state.team1, state.on_field1, state.on_field2) if player == "p1" else (state.team2, state.on_field2, state.on_field1)

        if not opp_on_field.is_alive() and on_field.is_alive():
            # opponent faint but player not: only opponent moves (choosing replacement)
            return [None]

        switches = ["switch " + p.name for p in team if p.cur_hp > 0 and p.name != on_field.name]
        if not on_field.is_alive():
            moves = switches
        else:
            moves = [m.name for m in on_field.moves] + switches
        return moves

    def is_end_state(self, state):
        state = state if state is not None else self.game_state
        return sum([p.is_alive() for p in state.team1]) == 0 or sum([p.is_alive() for p in state.team2]) == 0

    def first_player_won(self, state=None):
        """ Check if some pokemon from team1 are not dead. Note: this function should be run after game_finished
        returned True. """

        state = state if state is not None else self.game_state
        return sum([p.is_alive() for p in state.team1]) > 0

    def swap_states(self, game_state):
        self.game_state = game_state

    def play_round(self, p1_move, p2_move):
        """
        Call functions related to move application (apply_player_moves & get_info_from_state), change inner state and
        return information about what happened (whether any side fainted & who moved).

        :param p1_move: name of move selected by player 1
        :param p2_move: name of move selected by player 2
        :return: Python dict indicating which side has played a move and which side has fainted
        """

        # save start-of-turn information
        hp_side1 = self.game_state.on_field1.cur_hp
        name_side1 = self.game_state.on_field1.name
        hp_side2 = self.game_state.on_field2.cur_hp
        name_side2 = self.game_state.on_field2.name
        pre_team1 = [(p.name, p.poke_type, p.cur_hp, p.hp) for p in self.game_state.team1]
        pre_team2 = [(p.name, p.poke_type, p.cur_hp, p.hp) for p in self.game_state.team2]

        # apply moves (move order is determined here to keep track of who moved first)
        order = random.choice([True, False])
        self.apply_player_moves(self.game_state, p1_move, p2_move, force_order=order)

        # test if any side has fainted / which side moved (opponent lost hp or player switched)
        p1_moved = False
        if p1_move is not None:
            p1_moved |= hp_side2 > self.game_state.on_field2.cur_hp and name_side2 == self.game_state.on_field2.name
            p1_moved |= name_side2 != self.game_state.on_field2.name  # opponent switched
            p1_moved |= name_side1 != self.game_state.on_field1.name  # player switched

        p2_moved = False
        if p2_move is not None:
            p2_moved |= hp_side1 > self.game_state.on_field1.cur_hp and name_side1 == self.game_state.on_field1.name
            p2_moved |= name_side1 != self.game_state.on_field1.name
            p2_moved |= name_side2 != self.game_state.on_field2.name

        p1_first, p2_first = False, False
        if "switch" in p1_move and "switch" in p2_move or "switch" not in p1_move and "switch" not in p2_move:
            p1_first = self.game_state.on_field1.spe > self.game_state.on_field2.spe
            p1_first |= self.game_state.on_field1.spe == self.game_state.on_field1.spe and order
            p2_first = not p1_first
        ret = {'p1_moved': p1_moved, 'p1_fainted': not self.game_state.on_field1.is_alive(), 'p1_first': p1_first,
               'p2_moved': p2_moved, 'p2_fainted': not self.game_state.on_field2.is_alive(), 'p2_first': p2_first}

        # player get new information
        self.directly_available_info("p1", p1_move)
        self.directly_available_info("p2", p2_move)

        self.statistic_estimation("p1", ret, p1_move, p2_move, pre_team1, pre_team2)
        self.statistic_estimation("p2", ret, p1_move, p2_move, pre_team1, pre_team2)

        return ret

    @staticmethod
    def damage_formula(move, attacker, target, force_dmg=0.0):
        """
        Compute the amount of damage caused by the move used in specified conditions.

        :param move: Move object corresponding to attack used
        :param attacker: Pokemon object corresponding to the Pokémon using the move
        :param target: Pokemon object corresponding to the Pokémon receiving the move
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
        type_aff = 1 if target.poke_type not in TYPE_CHART[move.move_type] else TYPE_CHART[move.move_type][target.poke_type]
        dmg *= rd * stab * type_aff

        return floor(dmg)

    def apply_player_moves(self, game_state, p1_move, p2_move, force_dmg=0.0, force_order=None):
        """
        Execute player choices with regard to game rules to the game_state passed as parameter. This function applies
        changes on a parameter game_state and not on the attribute because some strategies require to test potential
        result on several game states.

        :param game_state: PokeGame object on which to apply the moves
        :param p1_move: name of attack or 'switch {name}'
        :param p2_move: same
        :param force_dmg: if float between 0.85 and 1, will be used to force damage random factor
        :param force_order: if both players attack and have same speed, force_order=True will make p1 move first, False
            will make p2 move first, None will leave the order be determined randomly
        :return: state with applied players actions
        """

        # both switch
        if p1_move is not None and "switch" in p1_move and p2_move is not None and "switch" in p2_move:
            game_state.on_field1 = game_state.team1[[n.name for n in game_state.team1].index(p1_move.split(" ")[1])]
            game_state.on_field2 = game_state.team2[[n.name for n in game_state.team2].index(p2_move.split(" ")[1])]

        # p1 switch
        elif p1_move is not None and "switch" in p1_move:
            game_state.on_field1 = game_state.team1[[n.name for n in game_state.team1].index(p1_move.split(" ")[1])]
            if p2_move is not None:
                game_state.on_field1.cur_hp = max(0, game_state.on_field1.cur_hp - self.damage_formula(game_state.on_field2.move_from_name(p2_move), game_state.on_field2, game_state.on_field1, force_dmg))

        # p2 switch
        elif p2_move is not None and "switch" in p2_move:
            game_state.on_field2 = game_state.team2[[n.name for n in game_state.team2].index(p2_move.split(" ")[1])]
            if p1_move is not None:
                game_state.on_field2.cur_hp = max(0, game_state.on_field2.cur_hp - self.damage_formula(game_state.on_field1.move_from_name(p1_move), game_state.on_field1, game_state.on_field2, force_dmg))

        # both attack (nb: cannot be both None at same time)
        else:
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

            attack_order[1][0].cur_hp = max(0, attack_order[1][0].cur_hp - self.damage_formula(attack_order[0][0].move_from_name(attack_order[0][1]), attack_order[0][0], attack_order[1][0], force_dmg))
            # second attacker must be alive to attack
            if attack_order[1][0].is_alive():
                attack_order[0][0].cur_hp = max(0, attack_order[0][0].cur_hp - self.damage_formula(attack_order[1][0].move_from_name(attack_order[1][1]), attack_order[1][0], attack_order[0][0], force_dmg))

        return game_state

    def directly_available_info(self, player, opponent_move):
        """
        Update player view with directly available information, information seen during the round (attack used by
        opponent, type and hp of Pokémon switched).

        :param player: "p1" or "p2", indicating whether information is searched for player1 or player2
        :param opponent_move: Name of move performed by opponent player
        :return: None but update internal state
        """

        real_own, real_other = (self.game_state.on_field1, self.game_state.on_field2) if player == "p1" else (self.game_state.on_field2, self.game_state.on_field1)
        own_of, other_of = (self.player1_view.on_field1, self.player1_view.on_field2) if player == "p1" else (self.player2_view.on_field2, self.player2_view.on_field1)
        own_team, other_team = (self.player1_view.team1, self.player1_view.team2) if player == "p1" else (self.player2_view.team2, self.player2_view.team1)

        # Own on-field
        own_of = own_team[[i for i, p in enumerate(own_team) if p.name == real_own.name][0]]
        # update player view of reference
        if player == "p1":
            self.player1_view.on_field1 = own_of
        elif player == "p2":
            self.player2_view.on_field2 = own_of
        own_of.cur_hp = real_own.cur_hp

        # Opponent on-field
        if real_other.name not in [p.name for p in other_team]:  # unknown name, opponent switched on new Pokémon
            unknown_poke_index = [p.name for p in other_team].index(None)
            other_of = other_team[unknown_poke_index]

            # update player view of reference
            if player == "p1":
                self.player1_view.on_field2 = other_of
            elif player == "p2":
                self.player2_view.on_field1 = other_of

        # HP and type changes (visible information)
        other_of.name, other_of.poke_type, other_of.cur_hp, other_of.hp = real_other.name, real_other.poke_type,\
            real_other.cur_hp, real_other.hp

        # Attack used
        if opponent_move not in [m.name for m in other_of.moves] and "switch" not in opponent_move:  # opponent used previously unseen attack
            unknown_move_index = 0 if other_of.moves[0].name is None else 1  # only have 2 attacks
            real_move = Move(opponent_move, *MOVES[opponent_move])
            other_of.moves[unknown_move_index] = Move(real_move.name, real_move.move_type, real_move.base_pow)

    @staticmethod
    def reverse_attack_calculator(move, attacker, target, hp_loss):
        """
        From a move, target and hp loss, compute the minimum value that the attack stat must have had.
        NB: Some parts of the damage formula make the inverse calculation not perfectly computable:
         - floor divisions
         - random factor
        Therefore, a lower and upper bound are considered.

        :param move: Move object corresponding to attack used
        :param attacker: Pokemon object corresponding to the Pokémon using the move
        :param target: Pokemon object corresponding to the Pokémon receiving the move
        :param hp_loss: Amount of health point lost by target
        :return: Lowest and highest estimations of statistic
        """

        attacker = copy.copy(attacker)
        max_atk = -1  # hitting min power
        min_atk = -1  # hitting max power

        # test edge cases
        attacker.atk = MIN_STAT
        min_60, max_60 = PokeGame.damage_formula(move, attacker, target, 0.85), PokeGame.damage_formula(move, attacker, target, 1.0)
        attacker.atk = MAX_STAT
        min_140, max_140 = PokeGame.damage_formula(move, attacker, target, 0.85), PokeGame.damage_formula(move, attacker, target, 1.0)
        if hp_loss < min_60 or hp_loss == 0:  # too few remaining HP or ineffective move
            min_atk, max_atk = None, None
        elif min_60 <= hp_loss < max_60:
            min_atk = None
        elif min_140 < hp_loss <= max_140:
            max_atk = None

        atk = MIN_STAT
        while atk <= MAX_STAT and (max_atk == -1 or min_atk == -1):
            attacker.atk = atk
            min_dmg = PokeGame.damage_formula(move, attacker, target, 0.85)
            max_dmg = PokeGame.damage_formula(move, attacker, target, 1)

            if hp_loss < max_dmg and min_atk == -1:
                min_atk = atk - 1

            if hp_loss < min_dmg and max_atk == -1:
                max_atk = atk - 1

            atk += 1

        return min_atk, max_atk

    @staticmethod
    def reverse_defense_calculator(move, attacker, target, hp_loss):
        """
        From a move, attacker and hp loss, compute the minimum value that the defense stat must have had. If estimation
        cannot be made (too few remaining HP), None value is returned.

        :param move: Move object corresponding to attack used
        :param attacker: Pokemon object corresponding to the Pokémon using the move
        :param target: Pokemon object corresponding to the Pokémon receiving the move
        :param hp_loss: Amount of health point lost by target
        :return: Lowest and highest estimations of statistic
        """

        target = copy.copy(target)
        max_des = -1  # taking max power
        min_des = -1  # taking min power

        # test edge cases
        target.des = MIN_STAT
        min_60, max_60 = PokeGame.damage_formula(move, attacker, target, 0.85), PokeGame.damage_formula(move, attacker, target, 1)
        target.des = MAX_STAT
        min_140, max_140 = PokeGame.damage_formula(move, attacker, target, 0.85), PokeGame.damage_formula(move, attacker, target, 1)
        if hp_loss < min_140 or hp_loss == 0:  # too few remaining HP or ineffective move
            max_des, min_des = None, None
        elif min_140 <= hp_loss < max_140:
            max_des = None
        elif min_60 < hp_loss <= max_60:
            min_des = None
        elif min_60 == hp_loss:
            min_des = MIN_STAT

        des = MAX_STAT
        while des >= MIN_STAT and (max_des == -1 or min_des == -1):
            target.des = des
            min_dmg = PokeGame.damage_formula(move, attacker, target, 0.85)
            max_dmg = PokeGame.damage_formula(move, attacker, target, 1)

            if hp_loss < max_dmg and max_des == -1:
                max_des = des - 1

            if hp_loss < min_dmg and min_des == -1:
                min_des = des - 1

            des -= 1

        return min_des, max_des

    @staticmethod
    def estimate_speed(player_first, own_move, opp_move, own_of, opp_of):
        """
        From the observation of the order of action, make an estimation of the speed that the opponent should have.
        The estimation is an upper estimation ("worst-case", highest possible).

        :param player_first: boolean value indicating whether player moved first.
        :param own_move: name of move chosen by player
        :param opp_move: name of move chosen by the opponent
        :param own_of: reference to player on_field Pokémon
        :param opp_of: same for opponent
        :return: estimation of the speed statistic of opp_of
        """

        est = opp_of.spe
        if "switch" in own_move and "switch" in opp_move or "switch" not in own_move and "switch" not in opp_move:
            # switches and normal attacks have different level of priority and cannot be compared
            if player_first:
                est = own_of.spe - 1 if opp_of.spe is None else min(opp_of.spe, own_of.spe - 1)
            else:
                est = 140 if opp_of.spe is None else max(opp_of.spe, own_of.spe + 1)

        return est

    def statistic_estimation(self, player, turn_res, own_move, opp_move, pre_own_team, pre_opp_team):
        """
        Call reverse defense and attack calculator and set an estimation of the opponent statistic in player view,
        based on damage dealt/received. Actual stat can be underestimated in case of faint (real amount of damage
        not shown).

        :param player: "p1" or "p2" indicating which player view is being estimated
        :param turn_res: "ret" object from "play_move" function
        :param own_move: name of move performed by player
        :param opp_move: name of move performed by opponent
        :param pre_own_team: copy of the state of the player at the beginning of the round (tuples containing
            (p.name, p.poke_type, p.cur_hp, p.hp)).
        :param pre_opp_team: Same for opponent
        :return: None but update player view
        """

        view = self.player1_view if player == "p1" else self.player2_view
        own_of, opp_of = (view.on_field1, view.on_field2) if player == "p1" else (view.on_field2, view.on_field1)
        own_moved, own_fainted, own_first = ("p1_moved", "p1_fainted", "p1_first") if player == "p1" else ("p2_moved", "p2_fainted", "p2_first")
        own_moved, own_fainted, own_first = turn_res[own_moved], turn_res[own_fainted], turn_res[own_first]
        opp_moved, opp_fainted, opp_first = ("p2_moved", "p2_fainted", "p2_first") if player == "p1" else ("p1_moved", "p1_fainted", "p2_first")
        opp_moved, opp_fainted, opp_first = turn_res[opp_moved], turn_res[opp_fainted], turn_res[opp_first]

        # opponent attack
        if opp_moved and "switch" not in opp_move:
            hp_loss = [p[2] for p in pre_own_team if p[0] == own_of.name][0] - own_of.cur_hp
            move = Move(opp_move, *MOVES[opp_move])

            # evaluate min and max possible value of stat landing the attack
            min_est, max_est = self.reverse_attack_calculator(move, opp_of, own_of, hp_loss)
            est = max_est if max_est is not None else min_est

            if est is not None:  # hp_loss does not represent full opponent power
                opp_of.atk = max(est, opp_of.atk) if opp_of.atk is not None else est

        # opponent defense
        if own_moved and "switch" not in own_move:
            hp_loss = [p[2] for p in pre_opp_team if p[0] == opp_of.name][0] - opp_of.cur_hp
            move = Move(own_move, *MOVES[own_move])

            min_est, max_est = self.reverse_defense_calculator(move, own_of, opp_of, hp_loss)
            est = max_est if max_est is not None else min_est

            if est is not None:
                opp_of.des = max(est, opp_of.des) if opp_of.des is not None else est

        # opponent speed
        max_est = self.estimate_speed(own_first, own_move, opp_move, own_of, opp_of)
        opp_of.spe = max_est
