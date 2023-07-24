import random
import unittest

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
                         (("d2", "DRAGON", 100, 80, 100, 101),
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
        game.apply_player_moves(gs, player1_move, player2_move, force_dmg=0.0, force_order=True)

        test_p1 = True
        if player1_move is not None and "switch" not in player1_move:  # p1 attacked
            test_p1 &= gs.on_field2.name == exp_field2_name and gs.on_field2.cur_hp < gs.on_field2.hp
        else:  # p1 switched
            test_p1 &= gs.on_field1.name == exp_field1_name

        test_p2 = True
        if player2_move is not None and "switch" not in player2_move:  # p2 attacked
            test_p2 &= gs.on_field1.name == exp_field1_name and gs.on_field1.cur_hp < gs.on_field1.hp
        else:  # p2 switched
            test_p2 &= gs.on_field2.name == exp_field2_name

        self.assertTrue(test_p1 and test_p2)

    @parameterized.expand([
        (["switch p2"], ["switch d2"], {'p1_moved': True, 'p1_fainted': False, 'p1_first': True,
                                        'p2_moved': True, "p2_fainted": False, "p2_first": False}),
        (["light_psychic"], ["light_steel"], {'p1_moved': True, 'p1_fainted': False, "p1_first": True,
                                              'p2_moved': True, 'p2_fainted': False, "p2_first": False}),
        (["light_psychic"], ["heavy_water"], {'p1_moved': True, 'p1_fainted': True, "p1_first": True,
                                              'p2_moved': True, 'p2_fainted': False, "p2_first": False}),
        (["light_psychic"], ["switch d2"], {'p1_moved': True, 'p1_fainted': False, "p1_first": False,
                                            'p2_moved': True, 'p2_fainted': False, "p2_first": False}),
        (["light_psychic", "switch p2", "light_grass"], ["switch d2", "light_bug", "light_bug"],
         {'p1_moved': True, 'p1_fainted': False, "p1_first": False,
          'p2_moved': True, 'p2_fainted': False, "p2_first": True}),
        ([None], ["switch d2"],
         {'p1_moved': False, 'p1_fainted': False, "p1_first": False,
          'p2_moved': True, 'p2_fainted': False, "p2_first": False})
    ])
    def test_play_round_return(self, p1_moves, p2_moves, exp_out):
        game = PokeGame(team_specs_for_game2)
        res = None
        for p1_move, p2_move in zip(p1_moves, p2_moves):
            res = game.play_round(p1_move, p2_move)

        self.assertEqual(res, exp_out)

    @parameterized.expand([
        (["light_psychic"], ["light_steel"]),
        (["light_psychic", "switch p2"], ["switch d2", "light_bug"]),
        (["switch p2"], ["switch d2"]),
        (["light_psychic"], ["heavy_water"]),
        (["light_psychic"], ["switch d2"]),
        (["light_psychic", "switch p2", "light_grass"], ["switch d2", "light_bug", "light_bug"]),
        ([None], ["switch d2"])
    ])
    def test_play_round_effects(self, p1_moves, p2_moves):
        game = PokeGame(team_specs_for_game2)
        rets = list()

        for p1_move, p2_move in zip(p1_moves, p2_moves):
            rets.append(game.play_round(p1_move, p2_move, 0.85, True))
            # NB: feedback of round was tested in other test and can thus be used safely in this test

        exp = PokeGame(team_specs_for_game2)
        for p1_move, p2_move, ret in zip(p1_moves, p2_moves, rets):
            pre_team1 = [(p.name, p.poke_type, p.cur_hp, p.hp) for p in exp.game_state.team1]
            pre_team2 = [(p.name, p.poke_type, p.cur_hp, p.hp) for p in exp.game_state.team2]

            exp.apply_player_moves(exp.game_state, p1_move, p2_move, 0.85, True)

            exp.directly_available_info("p1", p2_move)
            exp.directly_available_info("p2", p1_move)

            exp.statistic_estimation("p1", ret, p1_move, p2_move, pre_team1, pre_team2)
            exp.statistic_estimation("p2", ret, p2_move, p1_move, pre_team2, pre_team1)

        self.assertEqual(game, exp)

    def test_play_round_full_game(self):
        game = PokeGame(team_specs_for_game2)
        p1_moves = ["light_psychic", "heavy_fire", "switch p2", "heavy_electric", None, "heavy_electric",
                    "heavy_electric", "heavy_electric"]
        p2_moves = ["light_steel", "heavy_water", None, "light_steel", "switch d2", "light_bug", "light_bug",
                    "heavy_dragon"]

        for p1_move, p2_move in zip(p1_moves, p2_moves):
            game.play_round(p1_move, p2_move, 0.85, True)

        # expected values

        exp = PokeGame([[(("p1", "FIRE", 100, 100, 100, 100),
                          (("light_psychic", "PSYCHIC", 50), ("heavy_fire", "FIRE", 100))),
                         (("p2", "ELECTRIC", 100, 80, 100, 100),
                          (("light_grass", "GRASS", 50), ("heavy_electric", "ELECTRIC", 100)))],
                        [(("d1", "WATER", 100, 100, 100, 99),
                          (("light_steel", "STEEL", 50), ("heavy_water", "WATER", 100))),
                         (("d2", "DRAGON", 100, 80, 100, 101),
                          (("light_bug", "BUG", 50), ("heavy_dragon", "DRAGON", 100)))]])

        exp.player1_view = PokeGame.GameStruct([[(("p1", "FIRE", 100, 100, 100, 100),
                                                  (("light_psychic", "PSYCHIC", 50), ("heavy_fire", "FIRE", 100))),
                                                 (("p2", "ELECTRIC", 100, 80, 100, 100),
                                                  (("light_grass", "GRASS", 50), ("heavy_electric", "ELECTRIC", 100)))],
                                                [(("d1", "WATER", 100, 102, 115, 99),
                                                  (("light_steel", "STEEL", 50), ("heavy_water", "WATER", 100))),
                                                 (("d2", "DRAGON", 100, 80, 116, 140),
                                                  (("light_bug", "BUG", 50), ("heavy_dragon", "DRAGON", 100)))]])
        exp.player2_view = PokeGame.GameStruct([[(("p1", "FIRE", 100, 102, 115, 140),
                                                 (("light_psychic", "PSYCHIC", 50), ("heavy_fire", "FIRE", 100))),
                                                (("p2", "ELECTRIC", 100, 80, 119, 100),
                                                 (("heavy_electric", "ELECTRIC", 100), (None, None, None)))],
                                               [(("d1", "WATER", 100, 100, 100, 99),
                                                 (("light_steel", "STEEL", 50), ("heavy_water", "WATER", 100))),
                                                (("d2", "DRAGON", 100, 80, 100, 101),
                                                 (("light_bug", "BUG", 50), ("heavy_dragon", "DRAGON", 100)))]])

        exp.game_state.on_field1, exp.game_state.on_field2 = exp.game_state.team1[1], exp.game_state.team2[1]
        exp.player1_view.on_field1, exp.player1_view.on_field2 = exp.player1_view.team1[1], exp.player1_view.team2[1]
        exp.player2_view.on_field1, exp.player2_view.on_field2 = exp.player2_view.team1[1], exp.player2_view.team2[1]
        exp.game_state.team1[0].cur_hp, exp.game_state.team1[1].cur_hp, exp.game_state.team2[0].cur_hp, exp.game_state.team2[1].cur_hp = 0, 0, 0, 14
        exp.player1_view.team1[0].cur_hp, exp.player1_view.team1[1].cur_hp, exp.player1_view.team2[0].cur_hp, exp.player1_view.team2[1].cur_hp = 0, 0, 0, 14
        exp.player2_view.team1[0].cur_hp, exp.player2_view.team1[1].cur_hp, exp.player2_view.team2[0].cur_hp, exp.player2_view.team2[1].cur_hp = 0, 0, 0, 14

        self.assertEqual(game, exp, msg="{}\n{}".format(game, exp))

    def test_get_numeric_repr(self):
        exp = [1, 100, 100, 100, 100, 10, 50, 1, 100,
               3, 100, 80, 100, 100, 4, 50, 3, 100,
               2, 100, 100, 100, 100, 16, 50, 2, 100,
               14, 100, 80, 100, 100, 11, 50, 14, 100]
        game = PokeGame(team_specs_for_game)
        self.assertListEqual(game.get_numeric_repr(game.game_state), exp)


if __name__ == '__main__':
    unittest.main()
