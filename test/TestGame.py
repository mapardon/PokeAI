import random, unittest

from parameterized import parameterized
from src.game.PokeGame import PokeGame

random.seed(19)

team_specs_for_game = [[(("p1", "FIRE", 100, 100, 100, 100, 100, 100),
                         (("light_psychic", "PSYCHIC", 50), ("heavy_fire", "FIRE", 100))),
                        (("p2", "ELECTRIC", 100, 80, 100, 80, 100, 100),
                         (("light_grass", "GRASS", 50), ("heavy_electric", "ELECTRIC", 100)))],
                       [(("d1", "WATER", 100, 100, 100, 100, 100, 100),
                         (("light_steel", "STEEL", 50), ("heavy_water", "WATER", 100))),
                        (("d2", "DRAGON", 100, 80, 100, 80, 100, 100),
                         (("light_bug", "BUG", 50), ("heavy_dragon", "DRAGON", 100)))]]

team_specs_for_game2 = [[(("p1", "FIRE", 100, 100, 100, 100, 100, 100),
                          (("light_psychic", "PSYCHIC", 50), ("heavy_fire", "FIRE", 100))),
                         (("p2", "ELECTRIC", 100, 80, 100, 80, 100, 100),
                          (("light_grass", "GRASS", 50), ("heavy_electric", "ELECTRIC", 100)))],
                        [(("d1", "WATER", 100, 100, 100, 100, 100, 99),
                          (("light_steel", "STEEL", 50), ("heavy_water", "WATER", 100))),
                         (("d2", "DRAGON", 100, 80, 100, 80, 100, 100),
                          (("light_bug", "BUG", 50), ("heavy_dragon", "DRAGON", 100)))]]


def gen_move_list_1():
    return [PokeGame.Move("light_psychic", "PSYCHIC", 50), PokeGame.Move("heavy_fire", "FIRE", 100)]


def gen_move_list_2():
    return [PokeGame.Move("light_grass", "GRASS", 50), PokeGame.Move("heavy_electric", "ELECTRIC", 100)]


def gen_move_list_3():
    return [PokeGame.Move("light_steel", "STEEL", 50), PokeGame.Move("heavy_water", "WATER", 100)]


def gen_move_list_4():
    return [PokeGame.Move("light_bug", "BUG", 50), PokeGame.Move("heavy_dragon", "DRAGON", 100)]


def gen_unknown_moves():
    return [PokeGame.Move(None, None, None), PokeGame.Move(None, None, None)]


def gen_dummy_team_1():
    return [PokeGame.Pokemon("p1", "FIRE", [100, 100, 100, 100, 100, 100], gen_move_list_1()),
            PokeGame.Pokemon("p2", "ELECTRIC", [100, 80, 100, 80, 100, 100], gen_move_list_2())]


def gen_dummy_team_2():
    return [PokeGame.Pokemon("d1", "WATER", [100, 100, 100, 100, 100, 100], gen_move_list_3()),
            PokeGame.Pokemon("d2", "DRAGON", [100, 80, 100, 80, 100, 100], gen_move_list_4())]


def gen_team_unknown():
    return [PokeGame.Pokemon(None, None, [None] * 6, gen_unknown_moves()),
            PokeGame.Pokemon(None, None, [None] * 6, gen_unknown_moves())]


class TestCaseGameStruct(unittest.TestCase):
    """ NB: parameterized tests only work when whole class is executed """

    def test_create_move(self):
        fail = False
        try:
            m = PokeGame.Move("light_fire", "FIRE", 50)
        except Exception:
            fail = True
        self.assertFalse(fail)

    def test_create_Pokemon(self):
        fail = False
        try:
            moves = [PokeGame.Move("heavy_fire", "FIRE", 100), PokeGame.Move("light_grass", "GRASS", 50)]
            p = PokeGame.Pokemon("p", "FIRE", (100, 100, 100, 100, 100, 100), moves)
        except Exception:
            fail = True
        self.assertFalse(fail)

    @parameterized.expand([
        (PokeGame.Pokemon("p1", "normal", [100] * 10, []), 0, True),
        (PokeGame.Pokemon("p1", "normal", [100] * 10, []), 75, True),
        (PokeGame.Pokemon("p1", "normal", [100] * 10, []), 100, False)
    ])
    def test_is_alive(self, pokemon, reduced, expected_outcome):
        pokemon.cur_hp -= reduced
        self.assertEqual(pokemon.is_alive(), expected_outcome)

    @parameterized.expand([
        (str(), (gen_dummy_team_1(), gen_dummy_team_2())),
        ("player1", (gen_dummy_team_1(), gen_team_unknown())),
        ("player2", (gen_team_unknown(), gen_dummy_team_2()))
    ])
    def test_init_game_struct(self, view, expected_output):
        gs = PokeGame.GameStruct(view, team_specs_for_game)
        self.assertTupleEqual((gs.team1, gs.team2), expected_output)


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
        self.assertEqual(game.game_finished(), expected_output)

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
        pass

    def test_get_player2_view(self):
        pass

    @parameterized.expand([
        (False, ["light_psychic", "heavy_fire", "switch p2"]),
        (True, ["switch p2"])
    ])
    def test_get_player1_moves(self, fainted, expected_output):
        game = PokeGame(team_specs_for_game)
        if fainted:
            game.game_state.on_field1.cur_hp *= 0
        self.assertEqual(game.get_player1_moves(), expected_output)

    @parameterized.expand([
        (False, ["light_steel", "heavy_water", "switch d2"]),
        (True, ["switch d2"])
    ])
    def test_get_player2_moves(self, fainted, expected_output):
        game = PokeGame(team_specs_for_game)
        if fainted:
            game.game_state.on_field2.cur_hp *= 0
        self.assertEqual(game.get_player2_moves(), expected_output)

    @parameterized.expand([
        (PokeGame.Move("light_fire", "FIRE", 50), PokeGame.Pokemon("p1", "FIRE", [100] * 6, [None]),
         PokeGame.Pokemon("p2", "NORMAL", [100] * 6, [None]), 56),  # stab, normal efficiency
        (PokeGame.Move("light_fire", "FIRE", 50), PokeGame.Pokemon("p1", "FIRE", [100] * 6, [None]),
         PokeGame.Pokemon("p2", "WATER", [100] * 6, [None]), 28),  # stab, resistance
        (PokeGame.Move("light_fire", "FIRE", 50), PokeGame.Pokemon("p1", "FIRE", [100] * 6, [None]),
         PokeGame.Pokemon("p2", "GRASS", [100] * 6, [None]), 112),  # stab, weakness
        (PokeGame.Move("light_fire", "FIRE", 50), PokeGame.Pokemon("p1", "STEEL", [100] * 6, [None]),
         PokeGame.Pokemon("p2", "NORMAL", [100] * 6, [None]), 37),  # no stab, normal efficiency
        (PokeGame.Move("light_fire", "FIRE", 50), PokeGame.Pokemon("p1", "STEEL", [100] * 6, [None]),
         PokeGame.Pokemon("p2", "WATER", [100] * 6, [None]), 18),  # no stab, resistance
        (PokeGame.Move("light_fire", "FIRE", 50), PokeGame.Pokemon("p1", "STEEL", [100] * 6, [None]),
         PokeGame.Pokemon("p2", "GRASS", [100] * 6, [None]), 74)  # no stab, weakness
    ])
    def test_damage(self, move, attacker, target, expect_dmg):
        dmg = PokeGame.damage_formula(move, attacker, target, True)
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

        game.apply_player_moves(player1_move, player2_move)
        succeeded = True
        if player1_move is not None and not "switch" in player1_move:  # p1 attacked
            succeeded &= gs.on_field2.name == exp_field2_name and gs.on_field2.cur_hp < gs.on_field2.hp
        else:
            succeeded &= gs.on_field1.name == exp_field1_name

        if player2_move is not None and not "switch" in player2_move:  # p2 attacked
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
        res = game.apply_player_moves(p1_move, p2_move)
        self.assertEqual(res, exp_out)


if __name__ == '__main__':
    unittest.main()
