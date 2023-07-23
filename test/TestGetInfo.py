import random
import unittest

from parameterized import parameterized

from src.game.PokeGame import PokeGame
from src.game.Pokemon import Pokemon, Move
from src.game.constants import MIN_STAT, MAX_STAT

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
                        (("d2", "DRAGON", 100, 80, 100, 80),
                         (("light_bug", "BUG", 50), ("heavy_dragon", "DRAGON", 100)))]]

team_specs2 = [[(("p1", "FIRE", 100, 100, 100, 100),
                 (("light_psychic", "PSYCHIC", 50), ("heavy_fire", "FIRE", 100))),
                (("p2", "ROCK", 100, 100, 100, 95),
                 (("light_fairy", "FAIRY", 50), ("heavy_rock", "ROCK", 100)))],
               [(("d1", "ELECTRIC", 100, 80, 100, 95),
                 (("light_steel", "STEEL", 50), ("heavy_electric", "ELECTRIC", 100))),
                (("d2", "BUG", 100, 80, 100, 100),
                 (("light_ghost", "GHOST", 50), ("heavy_bug", "BUG", 100)))]]

dummy_poke1 = Pokemon("p1", "GROUND", (100, 100, 100, 100),
                      (Move("heavy_ground", "GROUND", 100), Move("light_flying", "FLYING", 50)))
dummy_poke2 = Pokemon("p2", "DARK", (90, 110, 90, 110),
                      (Move("heavy_dark", "DARK", 100), Move("light_fairy", "FAIRY", 50)))

"""
 *
 *    Tests
 *
"""


class MyTestCase(unittest.TestCase):

    @parameterized.expand([
        ("p1", ["light_psychic"], ["light_steel"],
         [[(("p1", "FIRE", 100, 100, 100, 100),
            (("light_psychic", "PSYCHIC", 50), ("heavy_fire", "FIRE", 100))),
           (("p2", "ELECTRIC", 100, 80, 100, 100),
            (("light_grass", "GRASS", 50), ("heavy_electric", "ELECTRIC", 100)))],
          [(("d1", "WATER", 100, None, None, None), (("light_steel", "STEEL", 50), (None, None, None))),
           ((None, None, None, None, None, None), ((None, None, None), (None, None, None)))]]),
        ("p2", ["light_psychic"], ["light_steel"],
         [[(("p1", "FIRE", 100, None, None, None), (("light_psychic", "PSYCHIC", 50), (None, None, None))),
           ((None, None, None, None, None, None), ((None, None, None), (None, None, None)))],
          [(("d1", "WATER", 100, 100, 100, 100),
            (("light_steel", "STEEL", 50), ("heavy_water", "WATER", 100))),
           (("d2", "DRAGON", 100, 80, 100, 80),
            (("light_bug", "BUG", 50), ("heavy_dragon", "DRAGON", 100)))]]),
        ("p1", ["heavy_fire"], ["light_steel"],
         [[(("p1", "FIRE", 100, 100, 100, 100),
            (("light_psychic", "PSYCHIC", 50), ("heavy_fire", "FIRE", 100))),
           (("p2", "ELECTRIC", 100, 80, 100, 100),
            (("light_grass", "GRASS", 50), ("heavy_electric", "ELECTRIC", 100)))],
          [(("d1", "WATER", 100, None, None, None), (("light_steel", "STEEL", 50), (None, None, None))),
           ((None, None, None, None, None, None), ((None, None, None), (None, None, None)))]]),
        ("p2", ["heavy_fire"], ["light_steel"],
         [[(("p1", "FIRE", 100, None, None, None,), (("heavy_fire", "FIRE", 100), (None, None, None))),
           ((None, None, None, None, None, None), ((None, None, None), (None, None, None)))],
          [(("d1", "WATER", 100, 100, 100, 100),
            (("light_steel", "STEEL", 50), ("heavy_water", "WATER", 100))),
           (("d2", "DRAGON", 100, 80, 100, 80),
            (("light_bug", "BUG", 50), ("heavy_dragon", "DRAGON", 100)))]]),
        ("p1", ["light_psychic"], ["switch d2"],
         [[(("p1", "FIRE", 100, 100, 100, 100),
            (("light_psychic", "PSYCHIC", 50), ("heavy_fire", "FIRE", 100))),
           (("p2", "ELECTRIC", 100, 80, 100, 100),
            (("light_grass", "GRASS", 50), ("heavy_electric", "ELECTRIC", 100)))],
          [(("d1", "WATER", 100, None, None, None), ((None, None, None), (None, None, None))),
           (("d2", "DRAGON", 100, None, None, None), ((None, None, None), (None, None, None)))]]),
        ("p2", ["light_psychic"], ["switch d2"],
         [[(("p1", "FIRE", 100, None, None, None), (("light_psychic", "PSYCHIC", 50), (None, None, None))),
           ((None, None, None, None, None, None), ((None, None, None), (None, None, None)))],
          [(("d1", "WATER", 100, 100, 100, 100),
            (("light_steel", "STEEL", 50), ("heavy_water", "WATER", 100))),
           (("d2", "DRAGON", 100, 80, 100, 80),
            (("light_bug", "BUG", 50), ("heavy_dragon", "DRAGON", 100)))]]),
        ("p1", ["switch p2"], ["light_steel"],
         [[(("p1", "FIRE", 100, 100, 100, 100),
            (("light_psychic", "PSYCHIC", 50), ("heavy_fire", "FIRE", 100))),
           (("p2", "ELECTRIC", 100, 80, 100, 100),
            (("light_grass", "GRASS", 50), ("heavy_electric", "ELECTRIC", 100)))],
          [(("d1", "WATER", 100, None, None, None), (("light_steel", "STEEL", 50), (None, None, None))),
           ((None, None, None, None, None, None), ((None, None, None), (None, None, None)))]]),
        ("p2", ["switch p2"], ["light_steel"],
         [[(("p1", "FIRE", 100, None, None, None), ((None, None, None), (None, None, None))),
           (("p2", "ELECTRIC", 100, None, None, None), ((None, None, None), (None, None, None)))],
          [(("d1", "WATER", 100, 100, 100, 100),
            (("light_steel", "STEEL", 50), ("heavy_water", "WATER", 100))),
           (("d2", "DRAGON", 100, 80, 100, 80),
            (("light_bug", "BUG", 50), ("heavy_dragon", "DRAGON", 100)))]]),
        ("p1", ["switch p2"], ["switch d2"],
         [[(("p1", "FIRE", 100, 100, 100, 100),
            (("light_psychic", "PSYCHIC", 50), ("heavy_fire", "FIRE", 100))),
           (("p2", "ELECTRIC", 100, 80, 100, 100),
            (("light_grass", "GRASS", 50), ("heavy_electric", "ELECTRIC", 100)))],
          [(("d1", "WATER", 100, None, None, None), ((None, None, None), (None, None, None))),
           (("d2", "DRAGON", 100, None, None, None), ((None, None, None), (None, None, None)))]]),
        ("p2", ["switch p2"], ["switch d2"],
         [[(("p1", "FIRE", 100, None, None, None), ((None, None, None), (None, None, None))),
           (("p2", "ELECTRIC", 100, None, None, None), ((None, None, None), (None, None, None)))],
          [(("d1", "WATER", 100, 100, 100, 100),
            (("light_steel", "STEEL", 50), ("heavy_water", "WATER", 100))),
           (("d2", "DRAGON", 100, 80, 100, 80),
            (("light_bug", "BUG", 50), ("heavy_dragon", "DRAGON", 100)))]]),
        ("p1", ("light_psychic", "light_psychic"), ("light_steel", "light_steel"),
         [[(("p1", "FIRE", 100, 100, 100, 100),
            (("light_psychic", "PSYCHIC", 50), ("heavy_fire", "FIRE", 100))),
           (("p2", "ELECTRIC", 100, 80, 100, 100),
            (("light_grass", "GRASS", 50), ("heavy_electric", "ELECTRIC", 100)))],
          [(("d1", "WATER", 100, None, None, None), (("light_steel", "STEEL", 50), (None, None, None))),
           ((None, None, None, None, None, None), ((None, None, None), (None, None, None)))]]),
        ("p2", ("light_psychic", "light_psychic"), ("light_steel", "light_steel"),
         [[(("p1", "FIRE", 100, None, None, None), (("light_psychic", "PSYCHIC", 50), (None, None, None))),
           ((None, None, None, None, None, None), ((None, None, None), (None, None, None)))],
          [(("d1", "WATER", 100, 100, 100, 100),
            (("light_steel", "STEEL", 50), ("heavy_water", "WATER", 100))),
           (("d2", "DRAGON", 100, 80, 100, 80),
            (("light_bug", "BUG", 50), ("heavy_dragon", "DRAGON", 100)))]]),
        ("p1", ("light_psychic", "switch p2"), ("heavy_water", None),
         [[(("p1", "FIRE", 100, 100, 100, 100),
            (("light_psychic", "PSYCHIC", 50), ("heavy_fire", "FIRE", 100))),
           (("p2", "ELECTRIC", 100, 80, 100, 100),
            (("light_grass", "GRASS", 50), ("heavy_electric", "ELECTRIC", 100)))],
          [(("d1", "WATER", 100, None, None, None), (("heavy_water", "WATER", 100), (None, None, None))),
           ((None, None, None, None, None, None), ((None, None, None), (None, None, None)))]]),
        ("p2", ("light_psychic", "switch p2"), ("heavy_water", None),
         [[(("p1", "FIRE", 100, None, None, None), (("light_psychic", "PSYCHIC", 50), (None, None, None))),
           (("p2", "ELECTRIC", 100, None, None, None), ((None, None, None), (None, None, None)))],
          [(("d1", "WATER", 100, 100, 100, 100),
            (("light_steel", "STEEL", 50), ("heavy_water", "WATER", 100))),
           (("d2", "DRAGON", 100, 80, 100, 80),
            (("light_bug", "BUG", 50), ("heavy_dragon", "DRAGON", 100)))]]),
        ("p1", ("light_psychic", "heavy_fire"), ("light_steel", "light_steel"),
         [[(("p1", "FIRE", 100, 100, 100, 100),
            (("light_psychic", "PSYCHIC", 50), ("heavy_fire", "FIRE", 100))),
           (("p2", "ELECTRIC", 100, 80, 100, 100),
            (("light_grass", "GRASS", 50), ("heavy_electric", "ELECTRIC", 100)))],
          [(("d1", "WATER", 100, None, None, None), (("light_steel", "STEEL", 50), (None, None, None))),
           ((None, None, None, None, None, None), ((None, None, None), (None, None, None)))]]),
        ("p2", ("light_psychic", "heavy_fire"), ("light_steel", "light_steel"),
         [[(("p1", "FIRE", 100, None, None, None),
            (("light_psychic", "PSYCHIC", 50), ("heavy_fire", "FIRE", 100))),
           ((None, None, None, None, None, None), ((None, None, None), (None, None, None)))],
          [(("d1", "WATER", 100, 100, 100, 100),
            (("light_steel", "STEEL", 50), ("heavy_water", "WATER", 100))),
           (("d2", "DRAGON", 100, 80, 100, 80),
            (("light_bug", "BUG", 50), ("heavy_dragon", "DRAGON", 100)))]]),
        ("p1", ("light_psychic", "heavy_fire"), ("switch d2", "light_bug"),
         [[(("p1", "FIRE", 100, 100, 100, 100),
            (("light_psychic", "PSYCHIC", 50), ("heavy_fire", "FIRE", 100))),
           (("p2", "ELECTRIC", 100, 80, 100, 100),
            (("light_grass", "GRASS", 50), ("heavy_electric", "ELECTRIC", 100)))],
          [(("d1", "WATER", 100, None, None, None), ((None, None, None), (None, None, None))),
           (("d2", "DRAGON", 100, None, None, None), (("light_bug", "BUG", 50), (None, None, None)))]]),
        ("p2", ("light_psychic", "heavy_fire"), ("light_steel", "light_steel"),
         [[(("p1", "FIRE", 100, None, None, None),
            (("light_psychic", "PSYCHIC", 50), ("heavy_fire", "FIRE", 100))),
           ((None, None, None, None, None, None), ((None, None, None), (None, None, None)))],
          [(("d1", "WATER", 100, 100, 100, 100),
            (("light_steel", "STEEL", 50), ("heavy_water", "WATER", 100))),
           (("d2", "DRAGON", 100, 80, 100, 80),
            (("light_bug", "BUG", 50), ("heavy_dragon", "DRAGON", 100)))]])
    ])
    def test_directly_available_info(self, test_player, player1_moves, player2_moves, exp_specs):
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

        exp_view = PokeGame.GameStruct(exp_specs)

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
        (False, False,
         Pokemon("p1", "STEEL", (100, 100, 100, 100), (Move("metal-atk", "STEEL", 95), Move(None, None, None))),
         Pokemon("test-normal", "FLYING", (100, 100, 100, 100),
                 (Move("flying-atk", "FLYING", 95), Move(None, None, None)))),
        (False, False,
         Pokemon("p1", "STEEL", (100, 120, 80, 80), (Move("metal-atk", "STEEL", 55), Move(None, None, None))),
         Pokemon("test-effective", "ICE", (100, 120, 100, 80), (Move(None, None, None), Move(None, None, None)))),
        (False, False,
         Pokemon("pkmn1", "STEEL", (100, 120, 100, 80), (Move("metal-atk", "STEEL", 95), Move(None, None, None))),
         Pokemon("test-KO", "NORMAL", (10, 120, 100, 80), (Move(None, None, None), Move(None, None, None)))),
        (True, True,
         Pokemon("pkmn1", "GHOST", (100, 120, 100, 80), (Move("ghost-atk", "GHOST", 95), Move(None, None, None))),
         Pokemon("test-ineffective", "NORMAL", (100, 120, 100, 80), (Move(None, None, None), Move(None, None, None)))),
        (True, False,
         Pokemon("pkmn1", "STEEL", (100, MIN_STAT, 100, 80), (Move("steel-atk", "STEEL", 95), Move(None, None, None))),
         Pokemon("test-minatk", "FLYING", (100, 120, 100, 80), (Move(None, None, None), Move(None, None, None)))),
        (False, True,
         Pokemon("pkmn1", "STEEL", (100, MAX_STAT, 80, 80), (Move("steel-atk", "STEEL", 95), Move(None, None, None))),
         Pokemon("test-maxatk", "FLYING", (100, 120, 100, 80), (Move(None, None, None), Move(None, None, None))))
    ])
    def test_reverse_attack_calculator(self, lo_is_none: bool, hi_is_none: bool, p1: Pokemon, p2: Pokemon):
        hp_loss = PokeGame.damage_formula(p1.moves[0], p1, p2)
        lo, hi = PokeGame.reverse_attack_calculator(p1.moves[0], p1, p2, hp_loss)
        self.assertTrue((lo_is_none and lo is None or lo <= p1.atk) and (hi_is_none and hi is None or p1.atk <= hi),
                        msg="{} <= {} <= {}".format(lo, p1.atk, hi))

    @parameterized.expand([
        (False, False,
         Pokemon("p1", "STEEL", (100, 100, 100, 100), (Move("metal-atk", "STEEL", 95), Move(None, None, None))),
         Pokemon("test-normal", "FLYING", (100, 100, 100, 100),
                 (Move("flying-atk", "FLYING", 95), Move(None, None, None)))),
        (False, False,
         Pokemon("p1", "STEEL", (100, 120, 80, 80), (Move("metal-atk", "STEEL", 55), Move(None, None, None))),
         Pokemon("test-effective", "ICE", (100, 120, 100, 80), (Move(None, None, None), Move(None, None, None)))),
        (False, False,
         Pokemon("pkmn1", "STEEL", (100, 120, 100, 80), (Move("metal-atk", "STEEL", 95), Move(None, None, None))),
         Pokemon("test-KO", "NORMAL", (10, 120, 100, 80), (Move(None, None, None), Move(None, None, None)))),
        (True, True,
         Pokemon("pkmn1", "GHOST", (100, 120, 100, 80), (Move("ghost-atk", "GHOST", 95), Move(None, None, None))),
         Pokemon("test-ineffective", "NORMAL", (100, 120, 100, 80), (Move(None, None, None), Move(None, None, None)))),
        (True, False,
         Pokemon("pkmn1", "STEEL", (100, 100, 100, 80), (Move("steel-atk", "STEEL", 95), Move(None, None, None))),
         Pokemon("test-mindef", "FLYING", (100, 120, MIN_STAT, 80), (Move(None, None, None), Move(None, None, None)))),
        (False, True,
         Pokemon("pkmn1", "STEEL", (100, 100, 80, 80), (Move("steel-atk", "STEEL", 95), Move(None, None, None))),
         Pokemon("test-maxdef", "FLYING", (100, 100, MAX_STAT, 80), (Move(None, None, None), Move(None, None, None))))
    ])
    def test_reverse_defense_calculator(self, lo_is_none: bool, hi_is_none: bool, p1: Pokemon, p2: Pokemon):
        hp_loss = PokeGame.damage_formula(p1.moves[0], p1, p2)
        lo, hi = PokeGame.reverse_defense_calculator(p1.moves[0], p1, p2, hp_loss)
        self.assertTrue((lo_is_none and lo is None or lo <= p2.des) and (hi_is_none and hi is None or p2.des <= hi),
                        msg="{} <= {} <= {}".format(lo, p2.des, hi))

    @parameterized.expand([
        (["light_psychic"], ["light_steel"], 140, 99,
         [[(("p1", "FIRE", 100, 100, 100, 100),
            (("light_psychic", "PSYCHIC", 50), ("heavy_fire", "FIRE", 100)))],
          [(("d1", "ELECTRIC", 100, 80, 100, 95),
            (("light_steel", "STEEL", 50), ("heavy_electric", "ELECTRIC", 100)))]]),
        (["light_psychic", "light_psychic", "light_psychic"], ["light_steel", "switch d2", "light_grass"], 104, 140,
         [[(("p1", "FIRE", 100, 100, 100, 100),
            (("light_psychic", "PSYCHIC", 50), ("heavy_fire", "FIRE", 100)))],
          [(("d1", "ELECTRIC", 100, 80, 100, 95),
            (("light_steel", "STEEL", 50), ("heavy_electric", "ELECTRIC", 100))),
           (("d2", "STEEL", 100, 140, 100, 105),
            (("light_grass", "GRASS", 50), (None, None, None)))]]),
        (["light_psychic", "light_psychic", "light_psychic"], ["light_steel", "switch d2", "light_grass"], 104, 99,
         [[(("p1", "FIRE", 100, 100, 100, 100),
            (("light_psychic", "PSYCHIC", 50), ("heavy_fire", "FIRE", 100)))],
          [(("d1", "ELECTRIC", 100, 80, 100, 105),
            (("light_steel", "STEEL", 50), ("heavy_electric", "ELECTRIC", 100))),
           (("d2", "STEEL", 100, 140, 100, 95),
            (("light_grass", "GRASS", 50), (None, None, None)))]]),
        (["light_psychic"], ["switch d2"], None, None,
         [[(("p1", "FIRE", 100, 100, 100, 100),
            (("light_psychic", "PSYCHIC", 50), ("heavy_fire", "FIRE", 100)))],
          [(("d1", "ELECTRIC", 100, 80, 100, 95),
            (("light_steel", "STEEL", 50), ("heavy_electric", "ELECTRIC", 100))),
           (("d2", "STEEL", 100, 140, 100, 105),
            (("light_grass", "GRASS", 50), (None, None, None)))]])
    ])
    def test_speed_estimation(self, player1_moves, player2_moves, p1_spe_exp, p2_spe_exp, team_specs):

        game = PokeGame(team_specs)

        for player1_move, player2_move in zip(player1_moves, player2_moves):
            game.apply_player_moves(game.game_state, player1_move, player2_move, 0.85)
            game.directly_available_info("p1", player1_move)
            game.directly_available_info("p2", player2_move)

            p1_first = game.game_state.on_field1.spe > game.game_state.on_field2.spe
            p2_first = not p1_first

            p2_spe_est = PokeGame.estimate_speed(p1_first, player1_move, player2_move, game.player1_view.on_field1,
                                                 game.player1_view.on_field2)
            p1_spe_est = PokeGame.estimate_speed(p2_first, player2_move, player1_move, game.player2_view.on_field2,
                                                 game.player2_view.on_field1)
            game.player1_view.on_field2.spe = p2_spe_est
            game.player2_view.on_field1.spe = p1_spe_est

        self.assertTrue((game.player1_view.on_field2.spe is None and p2_spe_exp is None or
                        game.player1_view.on_field2.spe == p2_spe_exp) and
                        (game.player2_view.on_field1.spe is None and p1_spe_exp is None or
                         game.player2_view.on_field1.spe == p1_spe_exp))

    @parameterized.expand([
        (False, False, "p1", ["light_psychic"], ["light_steel"],
         [[(("p1", "FIRE", 100, 100, 100, 100),
            (("light_psychic", "PSYCHIC", 50), ("heavy_fire", "FIRE", 100)))],
          [(("p2", "ELECTRIC", 100, 80, 100, 100),
            (("light_steel", "STEEL", 50), ("heavy_electric", "ELECTRIC", 100)))]]),
        (False, False, "p2", ["light_psychic"], ["light_steel"],
         [[(("p1", "FIRE", 100, 100, 100, 100),
            (("light_psychic", "PSYCHIC", 50), ("heavy_fire", "FIRE", 100)))],
          [(("p2", "ELECTRIC", 100, 80, 100, 100),
            (("light_steel", "STEEL", 50), ("heavy_electric", "ELECTRIC", 100)))]]),
        (False, False, "p1", ["switch p2", "light_fairy"], ["switch d2", "light_ghost"], team_specs2),
        (False, False, "p2", ["switch p2", "light_fairy"], ["switch d2", "light_ghost"], team_specs2),
        (True, True, "p1", ["light_psychic", "switch p2"], ["light_steel", "switch d2"], team_specs2),
        (True, True, "p1", ["light_psychic", "switch p2"], ["light_steel", "switch d2"], team_specs2),
        (True, True, "p1", ["light_ground"], ["light_ghost"],
         [[(("p1", "NORMAL", 100, 100, 100, 100),
            (("light_ground", "GROUND", 50), ("heavy_fire", "FIRE", 100)))],
          [(("d1", "FLYING", 100, 80, 100, 100),
            (("light_ghost", "GHOST", 50), ("heavy_electric", "ELECTRIC", 100)))]]),
        (True, True, "p2", ["light_ghost"], ["light_ground"],
         [[(("p1", "FLYING", 100, 100, 100, 100),
            (("light_ghost", "GHOST", 50), ("heavy_fire", "FIRE", 100)))],
          [(("d1", "NORMAL", 100, 80, 100, 100),
            (("light_ground", "GROUND", 50), ("heavy_electric", "ELECTRIC", 100)))]])
    ])
    def test_statistic_estimation(self, atk_is_none, des_is_none, test_player, player1_moves, player2_moves,
                                  team_specs):

        game = PokeGame(team_specs)
        for player1_move, player2_move in zip(player1_moves, player2_moves):
            pre_team1 = [(p.name, p.poke_type, p.cur_hp, p.hp) for p in game.game_state.team1]
            pre_team2 = [(p.name, p.poke_type, p.cur_hp, p.hp) for p in game.game_state.team2]

            game.apply_player_moves(game.game_state, player1_move, player2_move, 0.85)
            game.directly_available_info("p1", player1_move)
            game.directly_available_info("p2", player2_move)

            ret = {'p1_moved': "switch" in player1_move or "switch" in player2_move or
                               [p[2] for p in pre_team2 if p[0] == game.game_state.on_field2.name][
                                   0] != game.game_state.on_field2.cur_hp,
                   'p1_fainted': not game.game_state.on_field1.is_alive(),
                   'p1_first': game.game_state.on_field1.spe > game.game_state.on_field2.spe,
                   'p2_moved': "switch" in player2_move or "switch" in player1_move or
                               [p[2] for p in pre_team1 if p[0] == game.game_state.on_field1.name][
                                   0] != game.game_state.on_field1.cur_hp,
                   'p2_fainted': not game.game_state.on_field2.is_alive(),
                   'p2_first': game.game_state.on_field1.spe < game.game_state.on_field2.spe}

            game.statistic_estimation(test_player, ret, player1_move if test_player == "p1" else player2_move,
                                      player2_move if test_player == "p1" else player1_move,
                                      pre_team1 if test_player == "p1" else pre_team2,
                                      pre_team2 if test_player == "p1" else pre_team1)

        test_of = game.get_player1_view().on_field2 if test_player == "p1" else game.get_player2_view().on_field1
        real_of = game.game_state.on_field2 if test_player == "p1" else game.game_state.on_field1

        self.assertTrue((atk_is_none and test_of.atk is None or real_of.atk <= test_of.atk) and
                        (des_is_none and test_of.des is None or real_of.des <= test_of.des) and
                        real_of.spe < test_of.spe)


if __name__ == '__main__':
    unittest.main()
