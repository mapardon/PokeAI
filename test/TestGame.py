import copy
import random, unittest

from parameterized import parameterized
from src.game.PokeGame import PokeGame

random.seed(19)

dummy_team_specs = [[(("p1", "FIRE", 100, 100, 100, 100, 100, 100),
                      (("light_psychic", "PSYCHIC", 50), ("heavy_fire", "FIRE", 100))),
                     (("p2", "ELECTRIC", 100, 80, 100, 80, 100, 100),
                      (("light_grass", "GRASS", 50), ("heavy_electric", "ELECTRIC", 100)))],
                    [(("d1", "WATER", 100, 100, 100, 100, 100, 100),
                      (("light_steel", "STEEL", 50), ("heavy_water", "WATER", 100))),
                     (("d2", "DRAGON", 100, 80, 100, 80, 100, 100),
                      (("light_bug", "BUG", 50), ("heavy_dragon", "DRAGON", 100)))]]

move_list_1 = [PokeGame.Move("light_psychic", "PSYCHIC", 50), PokeGame.Move("heavy_fire", "FIRE", 100)]
move_list_2 = [PokeGame.Move("light_grass", "GRASS", 50), PokeGame.Move("heavy_electric", "ELECTRIC", 100)]
move_list_3 = [PokeGame.Move("light_steel", "STEEL", 50), PokeGame.Move("heavy_water", "WATER", 100)]
move_list_4 = [PokeGame.Move("light_bug", "BUG", 50), PokeGame.Move("heavy_dragon", "DRAGON", 100)]
unknown_moves = [PokeGame.Move(None, None, None), PokeGame.Move(None, None, None)]

dummy_team_1 = [PokeGame.Pokemon("p1", "FIRE", [100, 100, 100, 100, 100, 100], move_list_1),
                PokeGame.Pokemon("p2", "ELECTRIC", [100, 80, 100, 80, 100, 100], move_list_2)]
dummy_team_2 = [PokeGame.Pokemon("d1", "WATER", [100, 100, 100, 100, 100, 100], move_list_3),
                PokeGame.Pokemon("d2", "DRAGON", [100, 80, 100, 80, 100, 100], move_list_4)]
team_unknown = [PokeGame.Pokemon(None, None, [None] * 6, copy.deepcopy(unknown_moves)),
                PokeGame.Pokemon(None, None, [None] * 6, copy.deepcopy(unknown_moves))]


class MyTestCase(unittest.TestCase):
    """ NB: parameterized tests only works when whole class is executed """

    def test_create_move(self):
        fail = False
        try:
            m = PokeGame.Move("light_fire", "FIRE", 50)
        except Exception:
            fail = True
        self.assertEqual(fail, False)

    def test_create_Pokemon(self):
        fail = False
        try:
            moves = [PokeGame.Move("heavy_fire", "FIRE", 100), PokeGame.Move("light_grass", "GRASS", 50)]
            p = PokeGame.Pokemon("p", "FIRE", (100, 100, 100, 100, 100, 100), moves)
        except Exception:
            fail = True
        self.assertEqual(fail, False)

    @parameterized.expand([
        (str(), (dummy_team_1, dummy_team_2)),
        ("player1", (dummy_team_1, team_unknown)),
        ("player2", (team_unknown, dummy_team_2))
    ])
    def test_init_game_struct(self, view, expected_output):
        gs = PokeGame.GameStruct(view, dummy_team_specs)
        self.assertTupleEqual((gs.team1, gs.team2), expected_output)

    @parameterized.expand([
        (PokeGame.Move("light_fire", "FIRE", 50), PokeGame.Pokemon("p1", "FIRE", [100] * 6, [None]), PokeGame.Pokemon("p2", "NORMAL", [100] * 6, [None]), 58),
        (PokeGame.Move("light_fire", "FIRE", 50), PokeGame.Pokemon("p1", "FIRE", [100] * 6, [None]), PokeGame.Pokemon("p2", "WATER", [100] * 6, [None]), 32),
        (PokeGame.Move("light_fire", "FIRE", 50), PokeGame.Pokemon("p1", "FIRE", [100] * 6, [None]), PokeGame.Pokemon("p2", "GRASS", [100] * 6, [None]), 124),
        (PokeGame.Move("light_fire", "FIRE", 50), PokeGame.Pokemon("p1", "STEEL", [100] * 6, [None]), PokeGame.Pokemon("p2", "NORMAL", [100] * 6, [None]), 40),
        (PokeGame.Move("light_fire", "FIRE", 50), PokeGame.Pokemon("p1", "STEEL", [100] * 6, [None]), PokeGame.Pokemon("p2", "WATER", [100] * 6, [None]), 21),
        (PokeGame.Move("light_fire", "FIRE", 50), PokeGame.Pokemon("p1", "STEEL", [100] * 6, [None]), PokeGame.Pokemon("p2", "GRASS", [100] * 6, [None]), 81)
    ])
    def test_damage(self, move, attacker, target, expect_dmg):
        dmg = PokeGame.damage_formula(move, attacker, target)
        self.assertEqual(dmg, expect_dmg)

    def test_game_finished(self):
        pass


if __name__ == '__main__':
    unittest.main()
