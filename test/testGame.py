import copy
import random
import unittest

from parameterized import parameterized
from src.game.PokeGame import PokeGame
from src.game.Pokemon import Pokemon, Move

random.seed(19)

"""
 *
 *    Utils
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

team_specs_for_game3 = [[(("p1", "FAIRY", 100, 100, 100, 100),
                          (("light_psychic", "PSYCHIC", 50), ("heavy_fairy", "FAIRY", 100))),
                         (("p2", "FIRE", 100, 80, 100, 100),
                          (("light_grass", "GRASS", 50), ("heavy_fire", "FIRE", 100)))],
                        [(("d1", "WATER", 100, 100, 100, 99),
                          (("light_steel", "STEEL", 50), ("heavy_water", "WATER", 100)))]]

team_specs_for_game4 = [[(("p1", "FAIRY", 100, 100, 100, 100),
                          (("light_ground", "GROUND", 50), ("heavy_fairy", "FAIRY", 100))),
                         (("p2", "FIRE", 100, 80, 100, 100),
                          (("light_grass", "GRASS", 50), ("heavy_fire", "FIRE", 100)))],
                        [(("d1", "WATER", 100, 100, 100, 99),
                          (("light_steel", "STEEL", 50), ("heavy_water", "WATER", 100))),
                         (("d2", "DARK", 160, 100, 100, 85),
                          (("light_poison", "POISON", 50), ("heavy_dark", "DARK", 100)))]]


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
                p.cur_hp *= 0
        elif down_team == "team2":
            for p in game.game_state.team2:
                p.cur_hp *= 0
        else:  # not whole team down
            game.game_state.team1[0].cur_hp *= 0
            game.game_state.team2[0].cur_hp *= 0

        test = None
        test = game.get_cur_state()
        test = test

        self.assertEqual(expected_output, game.is_end_state(test))

    @parameterized.expand([
        (True, False, (True, False)),
        (False, True, (False, True)),
        (False, False, (False, False))
    ])
    def test_first_player_won(self, p1_victory, p2_victory, expected_output):
        game = PokeGame(team_specs_for_game)
        if p1_victory:
            for p in game.game_state.team2:
                p.cur_hp = 0
        elif p2_victory:
            for p in game.game_state.team1:
                p.cur_hp = 0
        self.assertEqual(game.match_result(), expected_output)

    def test_get_player1_view(self):
        game = PokeGame(team_specs_for_game)
        exp = PokeGame.GameStruct(team_specs_for_game)
        exp.team2 = gen_team_unknown()
        exp.on_field2 = exp.team2[0]
        exp.on_field2.name, exp.on_field2.poke_type, exp.on_field2.cur_hp, exp.on_field2.hp = "d1", "WATER", 100, 100
        self.assertEqual(game.get_player_view("p1"), exp)

    def test_get_player2_view(self):
        game = PokeGame(team_specs_for_game)
        exp = PokeGame.GameStruct(team_specs_for_game)
        exp.team1 = gen_team_unknown()
        exp.on_field1 = exp.team1[0]
        exp.on_field1.name, exp.on_field1.poke_type, exp.on_field1.cur_hp, exp.on_field1.hp = "p1", "FIRE", 100, 100
        self.assertEqual(game.get_player_view("p2"), exp)

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
        ("light_psychic", "heavy_water", "p1", "d1"),
        (None, "light_steel", "p1", "d1")
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

        self.assertEqual(exp_out, res)

    @parameterized.expand([
        (["light_psychic"], ["light_steel"], team_specs_for_game,
         [[(("p1", "FIRE", 100, 100, 100, 100),
            (("light_psychic", "PSYCHIC", 50), ("heavy_fire", "FIRE", 100))),
           (("p2", "ELECTRIC", 100, 80, 100, 100),
            (("light_grass", "GRASS", 50), ("heavy_electric", "ELECTRIC", 100)))],
          [(("d1", "WATER", 100, 102, 120, 99),
            (("light_steel", "STEEL", 50), (None, None, None))),
           ((None, None, None, None, None, None),
            ((None, None, None), (None, None, None)))]],
         [[(("p1", "FIRE", 100, 102, 123, 140),
            (("light_psychic", "PSYCHIC", 50), (None, None, None))),
           ((None, None, None, None, None, None),
            ((None, None, None), (None, None, None)))],
          [(("d1", "WATER", 100, 100, 100, 100),
            (("light_steel", "STEEL", 50), ("heavy_water", "WATER", 100))),
           (("d2", "DRAGON", 100, 80, 100, 100),
            (("light_bug", "BUG", 50), ("heavy_dragon", "DRAGON", 100)))]],
         [82, 100], [63, 100], 0, 0, 0, 0),
        (["light_ground"], ["switch d2"], team_specs_for_game4,
         [[(("p1", "FAIRY", 100, 100, 100, 100),
            (("light_ground", "GROUND", 50), ("heavy_fairy", "FAIRY", 100))),
           (("p2", "FIRE", 100, 80, 100, 100),
            (("light_grass", "GRASS", 50), ("heavy_fire", "FIRE", 100)))],
          [(("d1", "WATER", 100, None, None, None),
            ((None, None, None), (None, None, None))),
           (("d2", "DARK", 160, None, 120, None),
            ((None, None, None), (None, None, None)))]],
         [[(("p1", "FAIRY", 100, 102, None, None),
            (("light_ground", "GROUND", 50), (None, None, None))),
           ((None, None, None, None, None, None),
            ((None, None, None), (None, None, None)))],
          [(("d1", "WATER", 100, 100, 100, 99),
            (("light_steel", "STEEL", 50), ("heavy_water", "WATER", 100))),
           (("d2", "DARK", 160, 100, 100, 85),
            (("light_poison", "POISON", 50), ("heavy_dark", "DARK", 100)))]],
         [100, 100], [100, 123], 0, 1, 0, 1),
        (["heavy_fire", "switch p2"], ["heavy_water", None], team_specs_for_game2,
         [[(("p1", "FIRE", 100, 100, 100, 100),
            (("light_psychic", "PSYCHIC", 50), ("heavy_fire", "FIRE", 100))),
           (("p2", "ELECTRIC", 100, 80, 100, 100),
            (("light_grass", "GRASS", 50), ("heavy_electric", "ELECTRIC", 100)))],
          [(("d1", "WATER", 100, 60, 120, 99),
            (("heavy_water", "WATER", 100), (None, None, None))),
           ((None, None, None, None, None, None),
            ((None, None, None), (None, None, None)))]],
         [[(("p1", "FIRE", 100, 101, 140, 140),
            (("heavy_fire", "FIRE", 100), (None, None, None))),
           (("p2", "ELECTRIC", 100, None, None, None),
            ((None, None, None), (None, None, None)))],
          [(("d1", "WATER", 100, 100, 100, 99),
            (("light_steel", "STEEL", 50), ("heavy_water", "WATER", 100))),
           (("d2", "DRAGON", 100, 80, 100, 101),
            (("light_bug", "BUG", 50), ("heavy_dragon", "DRAGON", 100)))]],
         [0, 100], [46, 100], 1, 0, 1, 0)
    ])
    def test_play_round_effects(self, p1_moves, p2_moves, team_specs, p1v_res_specs, p2v_res_specs,
                                t1_hp, t2_hp, p1_v_of1_idx, p1_v_of2_idx, p2_v_of1_idx, p2_v_of2_idx):

        # actual values
        g = PokeGame(team_specs)
        for m1, m2 in zip(p1_moves, p2_moves):
            g.play_round(m1, m2, 0.85, True)

        # expected values

        # game state
        t = PokeGame(team_specs)
        for p1, p2, p1_hp, p2_hp in zip(t.game_state.team1, t.game_state.team2, t1_hp, t2_hp):
            p1.cur_hp, p2.cur_hp = p1_hp, p2_hp
        t.game_state.on_field1 = t.game_state.team1[p1_v_of1_idx]
        t.game_state.on_field2 = t.game_state.team2[p2_v_of2_idx]

        # player1 view
        t.player1_view = PokeGame.GameStruct(p1v_res_specs)
        for p1, p2, p1_hp, p2_hp in zip(t.player1_view.team1, t.player1_view.team2, t1_hp, t2_hp):
            p1.cur_hp = p1_hp
            if p2.hp is not None:
                p2.cur_hp = p2_hp
        t.player1_view.on_field1 = t.player1_view.team1[p1_v_of1_idx]
        t.player1_view.on_field2 = t.player1_view.team2[p1_v_of2_idx]

        # player2 view
        t.player2_view = PokeGame.GameStruct(p2v_res_specs)
        for p1, p2, p1_hp, p2_hp in zip(t.player2_view.team1, t.player2_view.team2, t1_hp, t2_hp):
            p2.cur_hp = p2_hp
            if p1.hp is not None:
                p1.cur_hp = p1_hp
        t.player2_view.on_field1 = t.player2_view.team1[p2_v_of1_idx]
        t.player2_view.on_field2 = t.player2_view.team2[p2_v_of2_idx]

        self.assertEqual(t, g, msg="moves: ({}, {})\nexp: {}\nact: {}".format(p1_moves, p2_moves, t, g))

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
                                                [(("d1", "WATER", 100, 102, 120, 99),
                                                  (("light_steel", "STEEL", 50), ("heavy_water", "WATER", 100))),
                                                 (("d2", "DRAGON", 100, 80, 120, 140),
                                                  (("light_bug", "BUG", 50), ("heavy_dragon", "DRAGON", 100)))]])

        exp.player2_view = PokeGame.GameStruct([[(("p1", "FIRE", 100, 102, 123, 140),
                                                  (("light_psychic", "PSYCHIC", 50), ("heavy_fire", "FIRE", 100))),
                                                 (("p2", "ELECTRIC", 100, 80, 124, 100),
                                                  (("heavy_electric", "ELECTRIC", 100), (None, None, None)))],
                                                [(("d1", "WATER", 100, 100, 100, 99),
                                                  (("light_steel", "STEEL", 50), ("heavy_water", "WATER", 100))),
                                                 (("d2", "DRAGON", 100, 80, 100, 101),
                                                  (("light_bug", "BUG", 50), ("heavy_dragon", "DRAGON", 100)))]])

        exp.game_state.on_field1, exp.game_state.on_field2 = exp.game_state.team1[1], exp.game_state.team2[1]
        exp.player1_view.on_field1, exp.player1_view.on_field2 = exp.player1_view.team1[1], exp.player1_view.team2[1]
        exp.player2_view.on_field1, exp.player2_view.on_field2 = exp.player2_view.team1[1], exp.player2_view.team2[1]
        exp.game_state.team1[0].cur_hp, exp.game_state.team1[1].cur_hp, exp.game_state.team2[0].cur_hp, \
            exp.game_state.team2[1].cur_hp = 0, 0, 0, 14
        exp.player1_view.team1[0].cur_hp, exp.player1_view.team1[1].cur_hp, exp.player1_view.team2[0].cur_hp, \
            exp.player1_view.team2[1].cur_hp = 0, 0, 0, 14
        exp.player2_view.team1[0].cur_hp, exp.player2_view.team1[1].cur_hp, exp.player2_view.team2[0].cur_hp, \
            exp.player2_view.team2[1].cur_hp = 0, 0, 0, 14

        self.assertEqual(exp, game, msg="exp: {}\nact: {}".format(exp, game))

    @parameterized.expand([
        (None, [1, 100, 100, 100, 100, 10, 50, 1, 100,
                3, 100, 80, 100, 100, 4, 50, 3, 100,
                2, 100, 100, 100, 100, 16, 50, 2, 100,
                14, 100, 80, 100, 100, 11, 50, 14, 100]),
        ("p1", [1, 100, 100, 100, 100, 10, 50, 1, 100,
                3, 100, 80, 100, 100, 4, 50, 3, 100,
                2, 100, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0]),
        ("p2", [1, 100, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0,
                2, 100, 100, 100, 100, 16, 50, 2, 100,
                14, 100, 80, 100, 100, 11, 50, 14, 100])
    ])
    def test_get_numeric_repr(self, player, exp):
        game = PokeGame(team_specs_for_game)

        if player is None:
            out = game.get_numeric_repr(game.game_state)
        elif player == "p1":
            out = game.get_numeric_repr(game.player1_view)
        else:
            out = game.get_numeric_repr(game.player2_view)

        self.assertListEqual(out, exp)

    def test_deepcopy_game(self):
        exp, game = PokeGame(team_specs_for_game), PokeGame(team_specs_for_game)
        game_cp = copy.deepcopy(game)

        # change values of original game
        for gs in [game.game_state, game.player1_view, game.player2_view]:
            for t in [gs.team1, gs.team2]:
                for p in t:
                    p.poke_type = "DARK"
                    p.cur_hp = 99
                    p.hp = 99
                    p.atk = 99
                    p.des = 99
                    p.spe = 97

                    for m in p.moves:
                        m.name = "light_dark"
                        m.move_type = "DARK"
                        m.base_pow = 55

        self.assertEqual(exp, game_cp)


if __name__ == '__main__':
    unittest.main()
