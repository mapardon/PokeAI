import random, unittest

from parameterized import parameterized
from src.game.PokeGame import PokeGame
from src.game.Pokemon import Pokemon, Move

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

dummy_poke1 = Pokemon("p1", "GROUND", (100, 100, 100, 100, 100, 100), (Move("heavy_ground", "GROUND", 100), Move("light_flying", "FLYING", 50)))
dummy_poke2 = Pokemon("p2", "DARK", (90, 110, 90, 110, 90, 110), (Move("heavy_dark", "DARK", 100), Move("light_fairy", "FAIRY", 50)))

"""
 *
 *    Tests
 *
"""


class MyTestCase(unittest.TestCase):

    @parameterized.expand([
        ("p1", ["light_psychic"], ["light_steel"],
         [[(("p1", "FIRE", 100, 100, 100, 100, 100, 100), (("light_psychic", "PSYCHIC", 50), ("heavy_fire", "FIRE", 100))),
           (("p2", "ELECTRIC", 100, 80, 100, 80, 100, 100), (("light_grass", "GRASS", 50), ("heavy_electric", "ELECTRIC", 100)))],
          [(("d1", "WATER", 100, None, None, None, None, None), (("light_steel", "STEEL", 50), (None, None, None))),
           ((None, None, None, None, None, None, None, None), ((None, None, None), (None, None, None)))]]),
        ("p2", ["light_psychic"], ["light_steel"],
         [[(("p1", "FIRE", 100, None, None, None, None, None), (("light_psychic", "PSYCHIC", 50), (None, None, None))),
           ((None, None, None, None, None, None, None, None), ((None, None, None), (None, None, None)))],
          [(("d1", "WATER", 100, 100, 100, 100, 100, 100), (("light_steel", "STEEL", 50), ("heavy_water", "WATER", 100))),
           (("d2", "DRAGON", 100, 80, 100, 80, 100, 100), (("light_bug", "BUG", 50), ("heavy_dragon", "DRAGON", 100)))]]),
        ("p1", ["heavy_fire"], ["light_steel"],
         [[(("p1", "FIRE", 100, 100, 100, 100, 100, 100), (("light_psychic", "PSYCHIC", 50), ("heavy_fire", "FIRE", 100))),
           (("p2", "ELECTRIC", 100, 80, 100, 80, 100, 100), (("light_grass", "GRASS", 50), ("heavy_electric", "ELECTRIC", 100)))],
          [(("d1", "WATER", 100, None, None, None, None, None), (("light_steel", "STEEL", 50), (None, None, None))),
           ((None, None, None, None, None, None, None, None), ((None, None, None), (None, None, None)))]]),
        ("p2", ["heavy_fire"], ["light_steel"],
         [[(("p1", "FIRE", 100, None, None, None, None, None), (("heavy_fire", "FIRE", 100), (None, None, None))),
           ((None, None, None, None, None, None, None, None), ((None, None, None), (None, None, None)))],
          [(("d1", "WATER", 100, 100, 100, 100, 100, 100), (("light_steel", "STEEL", 50), ("heavy_water", "WATER", 100))),
           (("d2", "DRAGON", 100, 80, 100, 80, 100, 100), (("light_bug", "BUG", 50), ("heavy_dragon", "DRAGON", 100)))]]),
        ("p1", ["light_psychic"], ["switch d2"],
         [[(("p1", "FIRE", 100, 100, 100, 100, 100, 100), (("light_psychic", "PSYCHIC", 50), ("heavy_fire", "FIRE", 100))),
           (("p2", "ELECTRIC", 100, 80, 100, 80, 100, 100), (("light_grass", "GRASS", 50), ("heavy_electric", "ELECTRIC", 100)))],
          [(("d1", "WATER", 100, None, None, None, None, None), ((None, None, None), (None, None, None))),
           (("d2", "DRAGON", 100, None, None, None, None, None), ((None, None, None), (None, None, None)))]]),
        ("p2", ["light_psychic"], ["switch d2"],
         [[(("p1", "FIRE", 100, None, None, None, None, None), (("light_psychic", "PSYCHIC", 50), (None, None, None))),
           ((None, None, None, None, None, None, None, None), ((None, None, None), (None, None, None)))],
          [(("d1", "WATER", 100, 100, 100, 100, 100, 100), (("light_steel", "STEEL", 50), ("heavy_water", "WATER", 100))),
           (("d2", "DRAGON", 100, 80, 100, 80, 100, 100), (("light_bug", "BUG", 50), ("heavy_dragon", "DRAGON", 100)))]]),
        ("p1", ["switch p2"], ["light_steel"],
         [[(("p1", "FIRE", 100, 100, 100, 100, 100, 100), (("light_psychic", "PSYCHIC", 50), ("heavy_fire", "FIRE", 100))),
           (("p2", "ELECTRIC", 100, 80, 100, 80, 100, 100), (("light_grass", "GRASS", 50), ("heavy_electric", "ELECTRIC", 100)))],
          [(("d1", "WATER", 100, None, None, None, None, None), (("light_steel", "STEEL", 50), (None, None, None))),
           ((None, None, None, None, None, None, None, None), ((None, None, None), (None, None, None)))]]),
        ("p2", ["switch p2"], ["light_steel"],
         [[(("p1", "FIRE", 100, None, None, None, None, None), ((None, None, None), (None, None, None))),
           (("p2", "ELECTRIC", 100, None, None, None, None, None), ((None, None, None), (None, None, None)))],
          [(("d1", "WATER", 100, 100, 100, 100, 100, 100), (("light_steel", "STEEL", 50), ("heavy_water", "WATER", 100))),
           (("d2", "DRAGON", 100, 80, 100, 80, 100, 100), (("light_bug", "BUG", 50), ("heavy_dragon", "DRAGON", 100)))]]),
        ("p1", ["switch p2"], ["switch d2"],
         [[(("p1", "FIRE", 100, 100, 100, 100, 100, 100), (("light_psychic", "PSYCHIC", 50), ("heavy_fire", "FIRE", 100))),
           (("p2", "ELECTRIC", 100, 80, 100, 80, 100, 100), (("light_grass", "GRASS", 50), ("heavy_electric", "ELECTRIC", 100)))],
          [(("d1", "WATER", 100, None, None, None, None, None), ((None, None, None), (None, None, None))),
           (("d2", "DRAGON", 100, None, None, None, None, None), ((None, None, None), (None, None, None)))]]),
        ("p2", ["switch p2"], ["switch d2"],
         [[(("p1", "FIRE", 100, None, None, None, None, None), ((None, None, None), (None, None, None))),
           (("p2", "ELECTRIC", 100, None, None, None, None, None), ((None, None, None), (None, None, None)))],
          [(("d1", "WATER", 100, 100, 100, 100, 100, 100), (("light_steel", "STEEL", 50), ("heavy_water", "WATER", 100))),
           (("d2", "DRAGON", 100, 80, 100, 80, 100, 100), (("light_bug", "BUG", 50), ("heavy_dragon", "DRAGON", 100)))]]),
        ("p1", ("light_psychic", "light_psychic"), ("light_steel", "light_steel"),
         [[(("p1", "FIRE", 100, 100, 100, 100, 100, 100), (("light_psychic", "PSYCHIC", 50), ("heavy_fire", "FIRE", 100))),
           (("p2", "ELECTRIC", 100, 80, 100, 80, 100, 100), (("light_grass", "GRASS", 50), ("heavy_electric", "ELECTRIC", 100)))],
          [(("d1", "WATER", 100, None, None, None, None, None), (("light_steel", "STEEL", 50), (None, None, None))),
           ((None, None, None, None, None, None, None, None), ((None, None, None), (None, None, None)))]]),
        ("p2", ("light_psychic", "light_psychic"), ("light_steel", "light_steel"),
         [[(("p1", "FIRE", 100, None, None, None, None, None), (("light_psychic", "PSYCHIC", 50), (None, None, None))),
           ((None, None, None, None, None, None, None, None), ((None, None, None), (None, None, None)))],
          [(("d1", "WATER", 100, 100, 100, 100, 100, 100), (("light_steel", "STEEL", 50), ("heavy_water", "WATER", 100))),
           (("d2", "DRAGON", 100, 80, 100, 80, 100, 100), (("light_bug", "BUG", 50), ("heavy_dragon", "DRAGON", 100)))]]),
        ("p1", ("light_psychic", "switch p2"), ("heavy_water", None),
         [[(("p1", "FIRE", 100, 100, 100, 100, 100, 100), (("light_psychic", "PSYCHIC", 50), ("heavy_fire", "FIRE", 100))),
           (("p2", "ELECTRIC", 100, 80, 100, 80, 100, 100), (("light_grass", "GRASS", 50), ("heavy_electric", "ELECTRIC", 100)))],
          [(("d1", "WATER", 100, None, None, None, None, None), (("heavy_water", "WATER", 100), (None, None, None))),
           ((None, None, None, None, None, None, None, None), ((None, None, None), (None, None, None)))]]),
        ("p2", ("light_psychic", "switch p2"), ("heavy_water", None),
         [[(("p1", "FIRE", 100, None, None, None, None, None), (("light_psychic", "PSYCHIC", 50), (None, None, None))),
           (("p2", "ELECTRIC", 100, None, None, None, None, None), ((None, None, None), (None, None, None)))],
          [(("d1", "WATER", 100, 100, 100, 100, 100, 100), (("light_steel", "STEEL", 50), ("heavy_water", "WATER", 100))),
           (("d2", "DRAGON", 100, 80, 100, 80, 100, 100), (("light_bug", "BUG", 50), ("heavy_dragon", "DRAGON", 100)))]]),
        ("p1", ("light_psychic", "heavy_fire"), ("light_steel", "light_steel"),
         [[(("p1", "FIRE", 100, 100, 100, 100, 100, 100), (("light_psychic", "PSYCHIC", 50), ("heavy_fire", "FIRE", 100))),
           (("p2", "ELECTRIC", 100, 80, 100, 80, 100, 100), (("light_grass", "GRASS", 50), ("heavy_electric", "ELECTRIC", 100)))],
          [(("d1", "WATER", 100, None, None, None, None, None), (("light_steel", "STEEL", 50), (None, None, None))),
           ((None, None, None, None, None, None, None, None), ((None, None, None), (None, None, None)))]]),
        ("p2", ("light_psychic", "heavy_fire"), ("light_steel", "light_steel"),
         [[(("p1", "FIRE", 100, None, None, None, None, None), (("light_psychic", "PSYCHIC", 50), ("heavy_fire", "FIRE", 100))),
           ((None, None, None, None, None, None, None, None), ((None, None, None), (None, None, None)))],
          [(("d1", "WATER", 100, 100, 100, 100, 100, 100), (("light_steel", "STEEL", 50), ("heavy_water", "WATER", 100))),
           (("d2", "DRAGON", 100, 80, 100, 80, 100, 100), (("light_bug", "BUG", 50), ("heavy_dragon", "DRAGON", 100)))]]),
        ("p1", ("light_psychic", "heavy_fire"), ("switch d2", "light_bug"),
         [[(("p1", "FIRE", 100, 100, 100, 100, 100, 100), (("light_psychic", "PSYCHIC", 50), ("heavy_fire", "FIRE", 100))),
           (("p2", "ELECTRIC", 100, 80, 100, 80, 100, 100), (("light_grass", "GRASS", 50), ("heavy_electric", "ELECTRIC", 100)))],
          [(("d1", "WATER", 100, None, None, None, None, None), ((None, None, None), (None, None, None))),
           (("d2", "DRAGON", 100, None, None, None, None, None), (("light_bug", "BUG", 50), (None, None, None)))]]),
        ("p2", ("light_psychic", "heavy_fire"), ("light_steel", "light_steel"),
         [[(("p1", "FIRE", 100, None, None, None, None, None), (("light_psychic", "PSYCHIC", 50), ("heavy_fire", "FIRE", 100))),
           ((None, None, None, None, None, None, None, None), ((None, None, None), (None, None, None)))],
          [(("d1", "WATER", 100, 100, 100, 100, 100, 100), (("light_steel", "STEEL", 50), ("heavy_water", "WATER", 100))),
           (("d2", "DRAGON", 100, 80, 100, 80, 100, 100), (("light_bug", "BUG", 50), ("heavy_dragon", "DRAGON", 100)))]])
    ])
    def test_directly_available_info_multiple(self, test_player, player1_moves, player2_moves, exp_specs):
        """ Try to cover as much as possible different case that could occur during a game

        :param test_player: 'p1' or 'p2', indicating tested player
        :param player1_moves: list of names of moves performed by first player
        :param player2_moves: same for second player
        :param exp_specs: specifications to create GameStruct object corresponding to state that should have been
            reached by tested function
        """

        game = PokeGame(team_specs_for_game)
        for player1_move, player2_move in zip(player1_moves, player2_moves):
            game.apply_player_moves(game.game_state, player1_move, player2_move, 0.85)
            game.directly_available_info(test_player, player2_move if test_player == "p1" else player1_move)

        exp = PokeGame(exp_specs)
        if test_player == "p1":
            exp.player1_view = PokeGame.GameStruct(exp_specs)
        else:
            exp.player2_view = PokeGame.GameStruct(exp_specs)
        exp_view = exp.player1_view if test_player == "p1" else exp.player2_view

        p1_last_switch = None
        for p1_mv in player1_moves:
            if p1_mv is not None and "switch" in p1_mv:
                p1_last_switch = p1_mv
        p2_last_switch = None
        for p2_mv in player2_moves:
            if p2_mv is not None and "switch" in p2_mv:
                p2_last_switch = p2_mv
        if p1_last_switch is not None:
            exp_view.on_field1 = exp_view.team1[0] if exp_view.team1[0].name in p1_last_switch else exp_view.team1[1]
        if p2_last_switch is not None:
            exp_view.on_field2 = exp_view.team2[0] if exp_view.team2[0].name in p2_last_switch else exp_view.team2[1]

        # lower hp after attacks (copy from tested game object, damage formula is not the tested item here)
        for t1, t2 in zip([exp_view.team1, exp_view.team2], [game.game_state.team1, game.game_state.team2]):
            for p1, p2 in zip(t1, t2):
                if p1.cur_hp is not None:
                    p1.cur_hp = p2.cur_hp

        test_view = game.get_player1_view() if test_player == "p1" else game.get_player2_view()

        self.assertEqual(test_view, exp_view)

    @parameterized.expand([
        ()
    ])
    def test_reverse_attack_calculator(self, p1: Pokemon, p2: Pokemon):
        hp_loss = PokeGame.damage_formula(p1.moves[0], p1, p2, 0.85)
        PokeGame.reverse_attack_calculator(p1.moves[0], p1, p2, hp_loss, 0.85, True)
        self.assertEqual(True, True)

    def test_reverse_defense_calculator(self):
        self.assertEqual(True, True)

    def test_statistic_estimation(self):
        self.assertEqual(True, True)

    def test_get_info_from_state(self):
        self.assertEqual(True, 1)


if __name__ == '__main__':
    unittest.main()
