class Pokemon:
    def __init__(self, name, poke_type, stats, moves):
        self.name = name  # names must be unique inside a team

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

        return None if move_name is None else self.moves[[m.name for m in self.moves].index(move_name)]

    def __eq__(self, other):
        """ NB: must not have same current hp """

        test = self.name == other.name and self.poke_type == other.poke_type
        test &= (self.hp, self.atk, self.des, self.spa, self.spd, self.spe) == (
            other.hp, other.atk, other.des, other.spa, other.spd, other.spe)
        for ms, mo in zip(self.moves, other.moves):
            test &= ms == mo
        return test

    def __copy__(self):
        cp_stats = [self.hp, self.atk, self.des, self.spa, self.spd, self.spe]
        cp_moves = [Move(m.name, m.move_type, m.base_pow) for m in self.moves]
        return Pokemon(self.name, self.poke_type, cp_stats, cp_moves)

    def __repr__(self):
        return "{} ({}/{}, {}, {}, {}, {}, {}) [({}) - ({})]".format(self.name, self.cur_hp, self.hp, self.atk,
                                                                     self.des, self.spa, self.spd, self.spe,
                                                                     str(self.moves[0]), str(self.moves[1]))


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
