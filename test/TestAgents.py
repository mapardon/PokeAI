import copy
import unittest, random

import numpy as np
from parameterized import parameterized

from src.agents.PlayerBM import PlayerBM
from src.agents.PlayerMDM import PlayerMDM
from src.agents.PlayerRandom import PlayerRandom
from src.agents.init_NN import initialize_NN, N_INPUT
from src.agents.PlayerML import PlayerML
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


class MyTestCase(unittest.TestCase):

    @parameterized.expand([
        ("normal", [10], [(10, N_INPUT), (10,)]),
        ("xavier", [12], [(12, N_INPUT), (12,)]),
        ("normalized-xavier", [20], [(20, N_INPUT), (20,)]),
        ("He", [15, 20, 12], [(15, N_INPUT), (20, 15), (12, 20), (12,)])
    ])
    def test_init_NN(self, init_mode, shape_in, expected_shape):
        net = initialize_NN(shape_in, init_mode)
        net_shapes = [l.shape for l in net]
        self.assertListEqual(expected_shape, net_shapes, init_mode)

    def test_forward_pass(self):
        # mode, role, network, ls, lamb, act_f, eps, lr, mvsel
        sentinel = True
        network = initialize_NN([10], "normal")
        pstate = [random.randint(0, 1) for _ in range(N_INPUT)]
        nstate = [random.randint(0, 1) for _ in range(N_INPUT)]

        try:
            player_ml = PlayerML("train", "p1", network, "Q-learning", None, "sigmoid", 0.3, 0.15, "eps-greedy")
            pre = player_ml.forward_pass(pstate)
            player_ml.backpropagation(PokeGame(team_specs_for_game), pstate, nstate, 0.75)
            post = player_ml.forward_pass(pstate)
        except Exception as e:
            sentinel = False

        self.assertTrue(sentinel, "Failed test strategy {}".format("Q-learning"))

    # test make_move of different agents

    def test_makemove_random(self):
        game = PokeGame(team_specs_for_game)
        sentinel = True

        try:
            agent = PlayerRandom("p1")
            select = agent.make_move(game)
        except Exception:
            sentinel = False

        self.assertTrue(sentinel)

    @parameterized.expand([
        ("p1", "heavy_fire", False),
        ("p2", "heavy_water", False),
        ("p2", "switch d2", True)
    ])
    def test_makemove_mdm(self, test_player, exp_move, is_ko):
        game = PokeGame(team_specs_for_game)
        agent = PlayerMDM(test_player)

        if is_ko:
            if test_player == "p2":
                game.game_state.on_field2.cur_hp = 0
                game.player1_view.on_field2.cur_hp = 0
                game.player2_view.on_field2.cur_hp = 0
        test = agent.make_move(game)

        self.assertEqual(exp_move, test)

    @parameterized.expand([
        ("p1", False, "heavy_fire"),
        ("p2", False, "heavy_water"),
        ("p1", True, "switch p2"),
        ("p2", True, "heavy_water")
    ])
    def test_makemove_bm(self, test_player, full_view, exp_move):
        game = PokeGame(team_specs_for_game)
        agent = PlayerBM(test_player)

        if full_view:
            game.player1_view = copy.deepcopy(game.game_state)
            game.player2_view = copy.deepcopy(game.game_state)

        test = agent.make_move(game)

        self.assertEqual(exp_move, test)


if __name__ == '__main__':
    unittest.main()
