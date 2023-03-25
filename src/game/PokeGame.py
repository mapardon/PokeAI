import copy
import random
from math import floor

TYPES = ['BUG', 'DARK', 'DRAGON', 'ELECTRIC', 'FAIRY', 'FIGHTING', 'FIRE', 'FLYING', 'GHOST', 'GRASS', 'GROUND', 'ICE',
         'STEEL', 'NORMAL', 'POISON', 'PSYCHIC', 'ROCK', 'WATER']

#  {offensive: {defensive: multiplier}}
TYPE_CHART = {'NORMAL': {'ROCK': 0.5, 'GHOST': 0, 'STEEL': 0.5, 'NORMAL': 1, 'FIRE': 1, 'WATER': 1, 'ELECTRIC': 1, 'GRASS': 1, 'ICE': 1, 'FIGHTING': 1, 'POISON': 1, 'GROUND': 1, 'FLYING': 1, 'PSYCHIC': 1, 'BUG': 1, 'DRAGON': 1, 'DARK': 1, 'FAIRY': 1},
              'FIRE': {'FIRE': 0.5, 'WATER': 0.5, 'GRASS': 2, 'ICE': 2, 'BUG': 2, 'ROCK': 0.5, 'DRAGON': 0.5, 'STEEL': 0.5, 'NORMAL': 1, 'ELECTRIC': 1, 'FIGHTING': 1, 'POISON': 1, 'GROUND': 1, 'FLYING': 1, 'PSYCHIC': 1, 'GHOST': 1, 'DARK': 1, 'FAIRY': 1},
              'WATER': {'FIRE': 2, 'WATER': 0.5, 'GRASS': 0.5, 'GROUND': 2, 'ROCK': 2, 'DRAGON': 0.5, 'NORMAL': 1, 'ELECTRIC': 1, 'ICE': 1, 'FIGHTING': 1, 'POISON': 1, 'FLYING': 1, 'PSYCHIC': 1, 'BUG': 1, 'GHOST': 1, 'DARK': 1, 'STEEL': 1, 'FAIRY': 1},
              'ELECTRIC': {'WATER': 2, 'ELECTRIC': 0.5, 'GRASS': 0.5, 'GROUND': 0, 'FLYING': 2, 'DRAGON': 0.5, 'NORMAL': 1, 'FIRE': 1, 'ICE': 1, 'FIGHTING': 1, 'POISON': 1, 'PSYCHIC': 1, 'BUG': 1, 'ROCK': 1, 'GHOST': 1, 'DARK': 1, 'STEEL': 1, 'FAIRY': 1},
              'GRASS': {'FIRE': 0.5, 'WATER': 2, 'GRASS': 0.5, 'POISON': 0.5, 'GROUND': 2, 'FLYING': 0.5, 'BUG': 0.5, 'ROCK': 2, 'DRAGON': 0.5, 'STEEL': 0.5, 'NORMAL': 1, 'ELECTRIC': 1, 'ICE': 1, 'FIGHTING': 1, 'PSYCHIC': 1, 'GHOST': 1, 'DARK': 1, 'FAIRY': 1},
              'ICE': {'FIRE': 0.5, 'WATER': 0.5, 'GRASS': 2, 'ICE': 0.5, 'GROUND': 2, 'FLYING': 2, 'DRAGON': 2, 'STEEL': 0.5, 'NORMAL': 1, 'ELECTRIC': 1, 'FIGHTING': 1, 'POISON': 1, 'PSYCHIC': 1, 'BUG': 1, 'ROCK': 1, 'GHOST': 1, 'DARK': 1, 'FAIRY': 1},
              'FIGHTING': {'NORMAL': 2, 'ICE': 2, 'POISON': 0.5, 'FLYING': 0.5, 'PSYCHIC': 0.5, 'BUG': 0.5, 'ROCK': 2, 'GHOST': 0, 'DARK': 2, 'STEEL': 2, 'FAIRY': 0.5, 'FIRE': 1, 'WATER': 1, 'ELECTRIC': 1, 'GRASS': 1, 'FIGHTING': 1, 'GROUND': 1, 'DRAGON': 1},
              'POISON': {'GRASS': 2, 'POISON': 0.5, 'GROUND': 0.5, 'ROCK': 0.5, 'GHOST': 0.5, 'STEEL': 0, 'FAIRY': 2, 'NORMAL': 1, 'FIRE': 1, 'WATER': 1, 'ELECTRIC': 1, 'ICE': 1, 'FIGHTING': 1, 'FLYING': 1, 'PSYCHIC': 1, 'BUG': 1, 'DRAGON': 1, 'DARK': 1},
              'GROUND': {'FIRE': 2, 'ELECTRIC': 2, 'GRASS': 0.5, 'POISON': 2, 'FLYING': 0, 'BUG': 0.5, 'ROCK': 2, 'STEEL': 2, 'NORMAL': 1, 'WATER': 1, 'ICE': 1, 'FIGHTING': 1, 'GROUND': 1, 'PSYCHIC': 1, 'GHOST': 1, 'DRAGON': 1, 'DARK': 1, 'FAIRY': 1},
              'FLYING': {'ELECTRIC': 0.5, 'GRASS': 2, 'FIGHTING': 2, 'BUG': 2, 'ROCK': 0.5, 'STEEL': 0.5, 'NORMAL': 1, 'FIRE': 1, 'WATER': 1, 'ICE': 1, 'POISON': 1, 'GROUND': 1, 'FLYING': 1, 'PSYCHIC': 1, 'GHOST': 1, 'DRAGON': 1, 'DARK': 1, 'FAIRY': 1},
              'PSYCHIC': {'FIGHTING': 2, 'POISON': 2, 'PSYCHIC': 0.5, 'DARK': 0, 'STEEL': 0.5, 'NORMAL': 1, 'FIRE': 1, 'WATER': 1, 'ELECTRIC': 1, 'GRASS': 1, 'ICE': 1, 'GROUND': 1, 'FLYING': 1, 'BUG': 1, 'ROCK': 1, 'GHOST': 1, 'DRAGON': 1, 'FAIRY': 1},
              'BUG': {'FIRE': 0.5, 'GRASS': 2, 'FIGHTING': 0.5, 'POISON': 0.5, 'FLYING': 0.5, 'PSYCHIC': 2, 'GHOST': 0.5, 'DARK': 2, 'STEEL': 0.5, 'FAIRY': 0.5, 'NORMAL': 1, 'WATER': 1, 'ELECTRIC': 1, 'ICE': 1, 'GROUND': 1, 'BUG': 1, 'ROCK': 1, 'DRAGON': 1},
              'ROCK': {'FIRE': 2, 'ICE': 2, 'FIGHTING': 0.5, 'GROUND': 0.5, 'FLYING': 2, 'BUG': 2, 'STEEL': 0.5, 'NORMAL': 1, 'WATER': 1, 'ELECTRIC': 1, 'GRASS': 1, 'POISON': 1, 'PSYCHIC': 1, 'ROCK': 1, 'GHOST': 1, 'DRAGON': 1, 'DARK': 1, 'FAIRY': 1},
              'GHOST': {'NORMAL': 0, 'PSYCHIC': 2, 'GHOST': 2, 'DARK': 0.5, 'FIRE': 1, 'WATER': 1, 'ELECTRIC': 1, 'GRASS': 1, 'ICE': 1, 'FIGHTING': 1, 'POISON': 1, 'GROUND': 1, 'FLYING': 1, 'BUG': 1, 'ROCK': 1, 'DRAGON': 1, 'STEEL': 1, 'FAIRY': 1},
              'DRAGON': {'DRAGON': 2, 'STEEL': 0.5, 'FAIRY': 0, 'NORMAL': 1, 'FIRE': 1, 'WATER': 1, 'ELECTRIC': 1, 'GRASS': 1, 'ICE': 1, 'FIGHTING': 1, 'POISON': 1, 'GROUND': 1, 'FLYING': 1, 'PSYCHIC': 1, 'BUG': 1, 'ROCK': 1, 'GHOST': 1, 'DARK': 1},
              'DARK': {'FIGHTING': 0.5, 'PSYCHIC': 2, 'GHOST': 2, 'DARK': 0.5, 'FAIRY': 0.5, 'NORMAL': 1, 'FIRE': 1, 'WATER': 1, 'ELECTRIC': 1, 'GRASS': 1, 'ICE': 1, 'POISON': 1, 'GROUND': 1, 'FLYING': 1, 'BUG': 1, 'ROCK': 1, 'DRAGON': 1, 'STEEL': 1},
              'STEEL': {'FIRE': 1, 'WATER': 1, 'ELECTRIC': 1, 'ICE': 2, 'ROCK': 2, 'STEEL': 0.5, 'FAIRY': 2, 'NORMAL': 1, 'GRASS': 1, 'FIGHTING': 1, 'POISON': 1, 'GROUND': 1, 'FLYING': 1, 'PSYCHIC': 1, 'BUG': 1, 'GHOST': 1, 'DRAGON': 1, 'DARK': 1},
              'FAIRY': {'FIRE': 0.5, 'FIGHTING': 2, 'POISON': 0.5, 'DRAGON': 2, 'DARK': 2, 'STEEL': 1, 'NORMAL': 1, 'WATER': 1, 'ELECTRIC': 1, 'GRASS': 1, 'ICE': 1, 'GROUND': 1, 'FLYING': 1, 'PSYCHIC': 1, 'BUG': 1, 'ROCK': 1, 'GHOST': 1, 'FAIRY': 1}}


class PokeGame:
    class Pokemon:
        def __init__(self, name, poke_type, stats, moves):
            self.name = name

            # off-game parameters
            self.poke_type = poke_type
            self.hp = stats[0]
            self.atk = stats[1]
            self.des = stats[2]
            self.spa = stats[3]
            self.spd = stats[4]
            self.spe = stats[5]

            # moves
            self.moves = moves

            # in-game parameters (current hp, stats modifiers, conditions...)
            self.cur_hp = stats[0]

        def is_alive(self):
            return self.cur_hp > 0

        def move_from_name(self, move_name):
            """ Returns a reference to the move object whose name is passed as parameter """
            return self.moves[[m.name for m in self.moves].index(move_name)]

        def __eq__(self, other):
            test = self.name == other.name and self.poke_type == other.poke_type
            test &= (self.hp, self.atk, self.des, self.spa, self.spd, self.spe) == (other.hp, other.atk, other.des, other.spa, other.spd, other.spe)
            for ms, mo in zip(self.moves, other.moves):
                test &= ms == mo
            return test

        def __repr__(self):
            return "{} ({}/{}, {}, {}, {}, {}, {}) [({}) - ({})]".format(self.name, self.cur_hp, self.hp, self.atk, self.des, self.spa, self.spd, self.spe, str(self.moves[0]), str(self.moves[1]))

    class Move:
        def __init__(self, name, move_type, base_pow):
            self.name = name
            self.move_type = move_type
            self.base_pow = base_pow

        def __eq__(self, other):
            return self.name == other.name and self.move_type == other.move_type and self.base_pow == other.base_pow

        def __str__(self):
            return "|{}, {}, {}|".format(self.name, self.move_type, self.base_pow)

        def __repr__(self):
            return "|{}, {}, {}|".format(self.name, self.move_type, self.base_pow)

    class GameStruct:
        """  Contains all information needed to represent a game state """

        def __init__(self, player_view, teams_specs):
            self.team1 = list()
            self.team2 = list()

            init_specs = copy.deepcopy(teams_specs)
            # hide opponent's team info
            if player_view == "player1":
                init_specs[1] = self.gen_unknown_specs()
            elif player_view == "player2":
                init_specs[0] = self.gen_unknown_specs()

            for spec, team in zip(init_specs, [self.team1, self.team2]):
                for p in spec:
                    moves = list()
                    for atk in p[1]:
                        moves.append(PokeGame.Move(atk[0], atk[1], atk[2]))
                    team.append(PokeGame.Pokemon(p[0][0], p[0][1], p[0][2:8], moves))

            self.on_field1 = self.team1[0]
            self.on_field2 = self.team2[0]

        def team_from_specs(self, team_specs):
            pass

        def gen_unknown_specs(self):
            return [(tuple([None for _ in range(8)]), tuple([(None, None, None, None) for _ in range(2)])) for _ in
                    range(2)]

        def __eq__(self, other):
            """ For now, we'll consider pokemons and attacks must be in same order """
            test = True
            for ts, to in zip((self.team1, self.team2), (other.team1, other.team2)):
                for ps, po in zip(ts, to):
                    test &= ps == po
            return test

    def __init__(self, teams_specs):
        """
            'team_specs' has the following shape:

            [[( (t1_p1_name, t1_p1_type, p1_hp, p1_atk, ...), ((a1_name, a1_type, a1_pow), ...) ), (t1_p2_hp, ...), ...],
             [( (t2_p1_name, ...), ... ), ...]]
        """

        self.game_state = PokeGame.GameStruct(str(), teams_specs)
        #self.player1_view = PokeGame.GameStruct("player1", teams_specs)
        #self.player2_view = PokeGame.GameStruct("player2", teams_specs)
        self.player1_view = self.game_state
        self.player2_view = self.game_state

    @staticmethod
    def get_binary_repr(state):
        """ Converts the provided state (GameStruct) in binary representation """
        return

    def get_cur_state(self):
        return copy.deepcopy(self.game_state)

    def get_player1_view(self):
        """ Returns a representation of the game state from the point of view of the first player """
        return copy.deepcopy(self.player1_view)

    def get_player2_view(self):
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

    def apply_and_swap_states(self, player_1_move, player_2_move):
        res = self.apply_player_moves(self.game_state, player_1_move, player_2_move)
        return res[1]

    @staticmethod
    def damage_formula(move, attacker, target, force_dmg=False):
        """ force_dmg can be set to a decimal number to force a given damage multiplier """
        # base damages
        dmg = (floor(floor((2 * 100 / 5 + 2) * move.base_pow * attacker.atk / target.des) / 50) + 2)
        # modifiers
        weather = 1
        critical = 1.5 if random.random() < 0 else 1  # TODO deal with that later
        rd = random.randint(85, 100) / 100 if not force_dmg else force_dmg
        stab = 1.5 if move.move_type == attacker.poke_type else 1  # TODO terastall
        type_aff = 1 if target.poke_type not in TYPE_CHART[move.move_type] else TYPE_CHART[move.move_type][target.poke_type]
        dmg *= weather * critical * rd * stab * type_aff
        return floor(dmg)

    def apply_player_moves(self, game_state, player1_move, player2_move, force_dmg=False):
        """
        Execute player choices with regard to game rules to the game_state passed as parameter. This function applies
        changes on a parameter game_state and not on the attribute because some strategies require to test potential
        result on several game states (e.g.: minimax).

        :param game_state: state on which to apply the moves
        :param player1_move: name of attack or 'switch {name}'
        :param player2_move: same
        :returns: state with applied player actions and dict of the following shape:
            {p1_moved: bool, p1_fainted: bool, p2_moved: bool, p2_fainted: bool} (because it is difficult, from outer
            scope, to determine who has moved, who has fainted and who has done both)
        """

        ret = {'p1_moved': player1_move is not None, 'p1_fainted': False, 'p2_moved': player2_move is not None, 'p2_fainted': False}

        # both switch
        if player1_move is not None and "switch" in player1_move and player2_move is not None and "switch" in player2_move:
            # TODO: consider speed
            game_state.on_field1 = game_state.team1[[n.name for n in game_state.team1].index(player1_move.split(" ")[1])]
            game_state.on_field2 = game_state.team2[[n.name for n in game_state.team2].index(player2_move.split(" ")[1])]

        elif player1_move is not None and "switch" in player1_move:
            game_state.on_field1 = game_state.team1[[n.name for n in game_state.team1].index(player1_move.split(" ")[1])]
            if player2_move is not None:
                game_state.on_field1.cur_hp = max(0, game_state.on_field1.cur_hp - self.damage_formula(game_state.on_field2.move_from_name(player2_move), game_state.on_field2, game_state.on_field1, force_dmg))

        elif player2_move is not None and "switch" in player2_move:
            game_state.on_field2 = game_state.team2[[n.name for n in game_state.team2].index(player2_move.split(" ")[1])]
            if player1_move is not None:
                game_state.on_field2.cur_hp = max(0, game_state.on_field2.cur_hp - self.damage_formula(game_state.on_field1.move_from_name(player1_move), game_state.on_field1, game_state.on_field2, force_dmg))

        # both attack (nb: cannot be both None at same time)
        else:
            # first, determine attack order
            attack_order = [(game_state.on_field1, player1_move, 'p1'), (game_state.on_field2, player2_move, 'p2')]
            if game_state.on_field1.spe > game_state.on_field2.spe:
                pass
            elif game_state.on_field1.spe < game_state.on_field2.spe:
                attack_order.reverse()
            else:
                random.shuffle(attack_order)

            attack_order[1][0].cur_hp = max(0, attack_order[1][0].cur_hp - self.damage_formula(attack_order[0][0].move_from_name(attack_order[0][1]), attack_order[0][0], attack_order[1][0], force_dmg))
            # second attacker must be alive to attack
            if attack_order[1][0].is_alive():
                attack_order[0][0].cur_hp = max(0,  attack_order[0][0].cur_hp - self.damage_formula(attack_order[1][0].move_from_name(attack_order[1][1]), attack_order[1][0], attack_order[0][0], force_dmg))
            else:
                if attack_order[1][2] == "p1":
                    ret["p1_moved"] = False
                else:
                    ret["p2_moved"] = False

        # test if any side has fainted
        if not game_state.on_field1.is_alive():
            ret["p1_fainted"] = True

        if not game_state.on_field2.is_alive():
            ret["p2_fainted"] = True

        return game_state, ret
