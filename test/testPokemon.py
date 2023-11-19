import copy
import random
import unittest

from parameterized import parameterized

from src.game.Pokemon import Pokemon, Move

random.seed(19)

"""
 *
 *    Utility methods
 *
"""

team_specs_for_game = [[(("p1", "FIRE", 100, 100, 100, 100),
                         (("light_psychic", "PSYCHIC", 50), ("heavy_fire", "FIRE", 100))),
                        (("p2", "ELECTRIC", 100, 80, 100, 100),
                         (("light_grass", "GRASS", 50), ("heavy_electric", "ELECTRIC", 100)))],
                       [(("d1", "WATER", 100, 100, 100, 100),
                         (("light_steel", "STEEL", 50), ("heavy_water", "WATER", 100))),
                        (("d2", "DRAGON", 100, 80, 100, 100),
                         (("light_bug", "BUG", 50), ("heavy_dragon", "DRAGON", 100)))]]

team_specs_for_game2 = [[(("p1", "FIRE", 100, 100, 100, 100),
                          (("light_psychic", "PSYCHIC", 50), ("heavy_fire", "FIRE", 100))),
                         (("p2", "ELECTRIC", 100, 80, 100, 100),
                          (("light_grass", "GRASS", 50), ("heavy_electric", "ELECTRIC", 100)))],
                        [(("d1", "WATER", 100, 100, 100, 99),
                          (("light_steel", "STEEL", 50), ("heavy_water", "WATER", 100))),
                         (("d2", "DRAGON", 100, 80, 100, 100),
                          (("light_bug", "BUG", 50), ("heavy_dragon", "DRAGON", 100)))]]


def gen_move_list_1():
    return [Move("light_psychic", "PSYCHIC", 50), Move("heavy_fire", "FIRE", 100)]


def gen_move_list_2():
    return [Move("light_grass", "GRASS", 50), Move("heavy_electric", "ELECTRIC", 100)]


def gen_move_list_3():
    return [Move("light_steel", "STEEL", 50), Move("heavy_water", "WATER", 100)]


def gen_move_list_4():
    return [Move("light_bug", "BUG", 50), Move("heavy_dragon", "DRAGON", 100)]


def gen_unknown_moves():
    return [Move(None, None, None), Move(None, None, None)]


def gen_team_unknown():
    return [Pokemon(None, None, [None] * 4, gen_unknown_moves()),
            Pokemon(None, None, [None] * 4, gen_unknown_moves())]


"""
 *
 *    Tests
 *
"""


class TestCasePokemon(unittest.TestCase):
    """ NB: on PyCharm, parameterized tests only work when whole class is executed (error when launched individually) """

    def test_create_move(self):
        m = Move("light_fire", "FIRE", 50)

        test = [m.name, m.move_type, m.base_pow]
        exp = ["light_fire", "FIRE", 50]

        self.assertEqual(test, exp)

    def test_create_Pokemon(self):
        moves = [Move("heavy_fire", "FIRE", 100), Move("light_grass", "GRASS", 50)]
        p = Pokemon("p", "FIRE", (100, 100, 100, 100), moves)

        test = [p.name, p.poke_type, p.cur_hp, p.hp, p.atk, p.des, p.spe,
                p.moves[0].name, p.moves[0].move_type, p.moves[0].base_pow,
                p.moves[1].name, p.moves[1].move_type, p.moves[1].base_pow]
        exp = ["p", "FIRE", 100, 100, 100, 100, 100, "heavy_fire", "FIRE", 100, "light_grass", "GRASS", 50]

        self.assertEqual(test, exp)

    def test_copy_Pokemon_1(self):
        """
            Test if copy operator transmits values correctly and if copied object is independent of the original
        """

        moves = [Move("heavy_fire", "FIRE", 100), Move("light_grass", "GRASS", 50)]
        p = Pokemon("p", "FIRE", (100, 100, 100, 100), moves)

        p_cp = copy.copy(p)

        # change values of original Pokémon
        p.name, p.atk, p.des, p.spe, p.poke_type = "m", 120, 80, 110, "DRAGON"
        p.moves[0].name, p.moves[0].poke_type, p.moves[0].base_pow = "heavy_dragon", "DRAGON", 120
        p.moves[1].name, p.moves[1].poke_type, p.moves[1].base_pow = "light_dragon", "DRAGON", 50

        # values that should be retrieved in copied object
        test = [p_cp.name, p_cp.poke_type, p_cp.cur_hp, p_cp.hp, p_cp.atk, p_cp.des, p_cp.spe,
                p_cp.moves[0].name, p_cp.moves[0].move_type, p_cp.moves[0].base_pow,
                p_cp.moves[1].name, p_cp.moves[1].move_type, p_cp.moves[1].base_pow]
        exp = ["p", "FIRE", 100, 100, 100, 100, 100, "heavy_fire", "FIRE", 100, "light_grass", "GRASS", 50]

        self.assertEqual(test, exp)

    @parameterized.expand([
        (["p", "FIRE", 100, 100, 100, 100, 100, "heavy_fire", "FIRE", 100, "light_grass", "GRASS", 50],
         ["p", "FIRE", 100, 100, 100, 100, 100, "heavy_fire", "FIRE", 100, "light_grass", "GRASS", 50], True),
        (["p", "GROUND", 100, 100, 100, 100, 100, "heavy_ground", "GROUND", 100, "light_grass", "GRASS", 50],
         ["p", "FIRE", 100, 100, 100, 100, 100, "heavy_fire", "FIRE", 100, "light_grass", "GRASS", 50], False),
        (["p", "GROUND", 100, 100, 100, 100, 100, "heavy_ground", "GROUND", 100, "light_dark", "DARK", 50],
         ["p", "GROUND", 100, 100, 100, 120, 100, "heavy_ground", "GROUND", 100, "light_dark", "DARK", 50], False),
        (["p", "FIRE", 14, 100, 100, 100, 100, "heavy_fire", "FIRE", 100, "light_grass", "GRASS", 50],
         ["p", "FIRE", 100, 100, 100, 100, 100, "heavy_fire", "FIRE", 100, "light_grass", "GRASS", 50], True)
    ])
    def test_cmp_Pokemon(self, p1_specs, p2_specs, exp):
        p1 = Pokemon(p1_specs[0], p1_specs[1], p1_specs[3:7], [Move(p1_specs[7], p1_specs[8], p1_specs[9]),
                                                               Move(p1_specs[10], p1_specs[11], p1_specs[12])])
        p2 = Pokemon(p2_specs[0], p2_specs[1], p2_specs[3:7], [Move(p2_specs[7], p2_specs[8], p2_specs[9]),
                                                               Move(p2_specs[10], p2_specs[11], p2_specs[12])])
        p1.cur_hp = p1_specs[2]
        p2.cur_hp = p2_specs[2]

        if exp:
            self.assertEqual(p1, p2)
        else:
            self.assertNotEqual(p1, p2)

    @parameterized.expand([
        (Pokemon("p1", "normal", [100] * 4, []), 0, True),
        (Pokemon("p1", "normal", [100] * 4, []), 75, True),
        (Pokemon("p1", "normal", [100] * 4, []), 100, False)
    ])
    def test_is_alive(self, pokemon, reduced, expected_outcome):
        pokemon.cur_hp -= reduced
        self.assertEqual(pokemon.is_alive(), expected_outcome)


if __name__ == '__main__':
    unittest.main()
