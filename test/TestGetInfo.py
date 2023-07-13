import random, unittest

from parameterized import parameterized
from src.game.PokeGame import PokeGame
from src.game.Pokemon import Pokemon, Move
from src.game.constants import MOVES

random.seed(19)

"""
 *
 *    Utility methods
 *
"""

team_specs_for_game = [[(("p1", "FIRE", 100, 100, 100, 100, 100, 100),
                         (("light_psychic", "PSYCHIC", 50), ("heavy_fire", "FIRE", 100))),
                        (("p2", "ELECTRIC", 100, 80, 100, 80, 100, 100),
                         (("light_grass", "GRASS", 50), ("heavy_electric", "ELECTRIC", 100)))],
                       [(("d1", "WATER", 100, 100, 100, 100, 100, 100),
                         (("light_steel", "STEEL", 50), ("heavy_water", "WATER", 100))),
                        (("d2", "DRAGON", 100, 80, 100, 80, 100, 100),
                         (("light_bug", "BUG", 50), ("heavy_dragon", "DRAGON", 100)))]]

"""
 *
 *    Tests
 *
"""


class MyTestCase(unittest.TestCase):

    @parameterized.expand([
        ("p1", "light_psychic", "light_steel",
         Pokemon("p1", "FIRE", tuple([100]) * 7, [Move("light_psychic", "PSYCHIC", 50), Move(None, None, None)]),
         Pokemon("d1", "WATER", tuple([100]) * 7, [Move("light_steel", "STEEL", 50), Move(None, None, None)])),
        ("p2", "light_psychic", "light_steel",
         Pokemon("p1", "FIRE", tuple([100]) * 7, [Move("light_psychic", "PSYCHIC", 50), Move(None, None, None)]),
         Pokemon("d1", "WATER", tuple([100]) * 7, [Move("light_steel", "STEEL", 50), Move(None, None, None)])),
        ("p1", "heavy_fire", "light_steel",
         Pokemon("p1", "FIRE", tuple([100]) * 7, [Move("heavy_fire", "FIRE", 100), Move(None, None, None)]),
         Pokemon("d1", "WATER", tuple([100]) * 7, [Move("light_steel", "STEEL", 50), Move(None, None, None)])),
        ("p2", "heavy_fire", "light_steel",
         Pokemon("p1", "FIRE", tuple([100]) * 7, [Move("heavy_fire", "FIRE", 100), Move(None, None, None)]),
         Pokemon("d1", "WATER", tuple([100]) * 7, [Move("light_steel", "STEEL", 50), Move(None, None, None)]))
    ])
    def test_directly_available_info_1(self, player: str, player1_move: Move, player2_move: Move, p1: Pokemon, p2: Pokemon):
        """ Both attacked """

        game = PokeGame(team_specs_for_game)
        game.apply_player_moves(game.game_state, player1_move, player2_move, 0.85)
        game.directly_available_info(player, player2_move if player == "p1" else player1_move)

        exp = PokeGame(team_specs_for_game)
        dmg_on_p2 = PokeGame.damage_formula(p1.moves[0], p1, p2, 0.85)
        dmg_on_p1 = PokeGame.damage_formula(p2.moves[0], p2, p1, 0.85)
        exp.player1_view.team2[0].cur_hp -= dmg_on_p2
        exp.player1_view.team1[0].cur_hp -= dmg_on_p1
        exp.player1_view.team2[0].moves[0] = Move(player2_move, MOVES[player2_move][0], MOVES[player2_move][1])
        exp.player2_view.team1[0].cur_hp -= dmg_on_p1
        exp.player2_view.team2[0].cur_hp -= dmg_on_p2
        exp.player2_view.team1[0].moves[0] = Move(player1_move, MOVES[player1_move][0], MOVES[player1_move][1])

        test1 = game.get_player1_view() if player == "p1" else game.get_player2_view()
        test2 = exp.get_player1_view() if player == "p1" else exp.get_player2_view()

        if test1 != test2:
            print()

        self.assertEqual(test1, test2)

    def test_directly_available_info_2(self):
        """ p1 attacked and p2 switched """
        game = PokeGame(team_specs_for_game)
        self.assertEqual(True, True)

    def test_reverse_attack_calculator(self):
        self.assertEqual(True, True)

    def test_reverse_defense_calculator(self):
        self.assertEqual(True, True)

    def test_statistic_estimation(self):
        self.assertEqual(True, True)

    def test_get_info_from_state(self):
        self.assertEqual(True, 1)


if __name__ == '__main__':
    unittest.main()
