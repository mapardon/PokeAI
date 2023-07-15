import copy
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


def gen_dummy_team_1():
    return [Pokemon("p1", "FIRE", [100, 100, 100, 100], gen_move_list_1()),
            Pokemon("p2", "ELECTRIC", [100, 80, 100, 100], gen_move_list_2())]


def gen_dummy_team_2():
    return [Pokemon("d1", "WATER", [100, 100, 100, 100], gen_move_list_3()),
            Pokemon("d2", "DRAGON", [100, 80, 100, 100], gen_move_list_4())]


def gen_team_unknown():
    return [Pokemon(None, None, [None] * 4, gen_unknown_moves()),
            Pokemon(None, None, [None] * 4, gen_unknown_moves())]


"""
 *
 *    Tests
 *
"""


class TestCasePokeGame(unittest.TestCase):
    @parameterized.expand([
        ("team1", True),
        ("team2", True),
        ("", False)
    ])
    def test_game_finished(self, down_team, expected_output):
        game = PokeGame(team_specs_for_game)
        if down_team == "team1":
            for p in game.game_state.team1:
                p.cur_hp = 0
        elif down_team == "team2":
            for p in game.game_state.team2:
                p.cur_hp = 0
        else:  # not whole team down
            game.game_state.team1[0].cur_hp = 0
            game.game_state.team2[0].cur_hp = 0
        self.assertEqual(game.is_end_state(game.get_cur_state()), expected_output)

    @parameterized.expand([
        (True, True),
        (False, False)
    ])
    def test_first_player_won(self, team1_victory, expected_output):
        game = PokeGame(team_specs_for_game)
        if team1_victory:
            for p in game.game_state.team2:
                p.cur_hp = 0
        else:
            for p in game.game_state.team1:
                p.cur_hp = 0
        self.assertEqual(game.first_player_won(), expected_output)

    def test_get_player1_view(self):
        game = PokeGame(team_specs_for_game)
        exp = PokeGame.GameStruct(team_specs_for_game)
        exp.team2 = gen_team_unknown()
        exp.on_field2 = exp.team2[0]
        exp.on_field2.name, exp.on_field2.poke_type, exp.on_field2.cur_hp, exp.on_field2.hp = "d1", "WATER", 100, 100
        self.assertEqual(game.get_player1_view(), exp)

    def test_get_player2_view(self):
        game = PokeGame(team_specs_for_game)
        exp = PokeGame.GameStruct(team_specs_for_game)
        exp.team1 = gen_team_unknown()
        exp.on_field1 = exp.team1[0]
        exp.on_field1.name, exp.on_field1.poke_type, exp.on_field1.cur_hp, exp.on_field1.hp = "p1", "FIRE", 100, 100
        self.assertEqual(game.get_player2_view(), exp)

    def test_player_view_update(self):
        pass

    @parameterized.expand([
        (False, False, ["light_steel", "heavy_water", "switch d2"], "p2"),
        (True, False, ["switch d2"], "p2"),
        (False, False, ["light_psychic", "heavy_fire", "switch p2"], "p1"),
        (True, False, ["switch p2"], "p1"),
        (False, True, [None], "p1"),
        (True, True, ["switch p2"], "p1"),
        (False, True, [None], "p2"),
        (True, True, ["switch d2"], "p2")
    ])
    def test_get_moves_from_state(self, fainted, opp_fainted, expected_output, player):
        game = PokeGame(team_specs_for_game)
        if fainted:
            if player == "p1":
                game.game_state.on_field1.cur_hp *= 0
            else:
                game.game_state.on_field2.cur_hp *= 0

        if opp_fainted:
            if player == "p2":
                game.game_state.on_field1.cur_hp *= 0
            else:
                game.game_state.on_field2.cur_hp *= 0

        self.assertListEqual(game.get_moves_from_state(player, game.get_cur_state()), expected_output)

    @parameterized.expand([
        (Move("light_fire", "FIRE", 50), Pokemon("p1", "FIRE", [100] * 4, [None]),
         Pokemon("p2", "NORMAL", [100] * 4, [None]), 56),  # stab, normal efficiency
        (Move("light_fire", "FIRE", 50), Pokemon("p1", "FIRE", [100] * 4, [None]),
         Pokemon("p2", "WATER", [100] * 4, [None]), 28),  # stab, resistance
        (Move("light_fire", "FIRE", 50), Pokemon("p1", "FIRE", [100] * 4, [None]),
         Pokemon("p2", "GRASS", [100] * 4, [None]), 112),  # stab, weakness
        (Move("light_fire", "FIRE", 50), Pokemon("p1", "STEEL", [100] * 4, [None]),
         Pokemon("p2", "NORMAL", [100] * 4, [None]), 37),  # no stab, normal efficiency
        (Move("light_fire", "FIRE", 50), Pokemon("p1", "STEEL", [100] * 4, [None]),
         Pokemon("p2", "WATER", [100] * 4, [None]), 18),  # no stab, resistance
        (Move("light_fire", "FIRE", 50), Pokemon("p1", "STEEL", [100] * 4, [None]),
         Pokemon("p2", "GRASS", [100] * 4, [None]), 74)  # no stab, weakness
    ])
    def test_damage(self, move, attacker, target, expect_dmg):
        dmg = PokeGame.damage_formula(move, attacker, target, 0.85)
        self.assertEqual(dmg, expect_dmg)

    @parameterized.expand([
        ("light_psychic", "light_steel", "p1", "d1"),
        ("switch p2", "light_steel", "p2", "d1"),
        ("light_psychic", "switch d2", "p1", "d2"),
        ("switch p2", None, "p2", "d1"),
        (None, "switch d2", "p1", "d2"),
        ("light_psychic", "heavy_water", "p1", "d1")
    ])
    def test_apply_player_moves(self, player1_move, player2_move, exp_field1_name, exp_field2_name):
        game = PokeGame(team_specs_for_game)
        gs = game.game_state
        gs.on_field2.spe -= 1  # ensure attack order

        game.play_round(player1_move, player2_move)
        succeeded = True
        if player1_move is not None and "switch" not in player1_move:  # p1 attacked
            succeeded &= gs.on_field2.name == exp_field2_name and gs.on_field2.cur_hp < gs.on_field2.hp
            pass
        else:
            succeeded &= gs.on_field1.name == exp_field1_name

        if player2_move is not None and "switch" not in player2_move:  # p2 attacked
            succeeded &= gs.on_field1.name == exp_field1_name and gs.on_field1.cur_hp < gs.on_field1.hp
        else:
            succeeded &= gs.on_field2.name == exp_field2_name

        self.assertTrue(succeeded)

    @parameterized.expand([
        ("switch p2", "switch d2", {'p1_moved': True, 'p1_fainted': False, 'p2_moved': True, 'p2_fainted': False}),
        ("light_psychic", "light_steel", {'p1_moved': True, 'p1_fainted': False, 'p2_moved': True, 'p2_fainted': False}),
        ("light_psychic", "heavy_water", {'p1_moved': True, 'p1_fainted': True, 'p2_moved': True, 'p2_fainted': False}),
        ("light_psychic", "switch d2", {'p1_moved': True, 'p1_fainted': False, 'p2_moved': True, 'p2_fainted': False})
    ])
    def test_apply_player_moves_2(self, p1_move, p2_move, exp_out):
        game = PokeGame(team_specs_for_game2)
        res = game.play_round(p1_move, p2_move)
        self.assertEqual(res, exp_out)

    def test_get_numeric_repr(self):
        exp = [1, 100, 100, 100, 100, 10, 50, 1, 100,
               3, 100, 80, 100, 100, 4, 50, 3, 100,
               2, 100, 100, 100, 100, 16, 50, 2, 100,
               14, 100, 80, 100, 100, 11, 50, 14, 100]
        game = PokeGame(team_specs_for_game)
        self.assertListEqual(game.get_numeric_repr(game.game_state), exp)


if __name__ == '__main__':
    unittest.main()
