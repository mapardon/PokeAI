import random
import unittest

from parameterized import parameterized

from src.game.Pokemon import Pokemon, Move
from src.game.PokeGame import PokeGame

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

unknown_specs = [((None, None, None, None, None, None), ((None, None, None), (None, None, None)))] * 2


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


def gen_dummy_team_1():
    return [Pokemon("p1", "FIRE", [100, 100, 100, 100], gen_move_list_1()),
            Pokemon("p2", "ELECTRIC", [100, 80, 100, 100], gen_move_list_2())]


def gen_dummy_team_2():
    return [Pokemon("d1", "WATER", [100, 100, 100, 100], gen_move_list_3()),
            Pokemon("d2", "DRAGON", [100, 80, 100, 100], gen_move_list_4())]


def gen_team_unknown():
    return [Pokemon(None, None, [None] * 4, gen_unknown_moves()),
            Pokemon(None, None, [None] * 4, gen_unknown_moves())]


def gen_dummy_struct():
    return PokeGame.GameStruct(team_specs_for_game)


"""
 *
 *    Tests
 *
"""


class TestCaseGameStruct(unittest.TestCase):

    @parameterized.expand([
        (team_specs_for_game[0], unknown_specs, gen_dummy_team_1(), gen_team_unknown()),
        (team_specs_for_game[1], team_specs_for_game[0], gen_dummy_team_2(), gen_dummy_team_1())
    ])
    def test_create_game_struct(self, specs_team1, specs_team2, exp_team1, exp_team2):
        ts = [specs_team1, specs_team2]
        gs = PokeGame.GameStruct(ts)

        self.assertTupleEqual((gs.team1, gs.team2), (exp_team1, exp_team2))

    @parameterized.expand([
        (team_specs_for_game, gen_dummy_struct(), True),
        (team_specs_for_game, gen_dummy_struct(), False)
    ])
    def test_cmp_game_struct(self, team_specs, exp_struct, exp_res):

        if exp_res:
            gs = PokeGame.GameStruct(team_specs)
            self.assertEqual(gs, exp_struct)
        else:
            gs = PokeGame.GameStruct([team_specs[1], team_specs[0]])
            self.assertNotEqual(gs, exp_struct)


if __name__ == '__main__':
    unittest.main()
