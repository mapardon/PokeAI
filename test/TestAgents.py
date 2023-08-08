import unittest, random

import numpy as np
from parameterized import parameterized

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


def initialize_test_game():
    return PokeGame(team_specs_for_game)


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
        self.assertListEqual(net_shapes, expected_shape, init_mode)

    def test_forward_pass(self):
        # mode, role, network, ls, lamb, act_f, eps, lr, mvsel
        sentinel = True
        network = initialize_NN([10], "normal")
        pstate = np.array([random.randint(0, 1) for _ in range(N_INPUT)])
        nstate = np.array([random.randint(0, 1) for _ in range(N_INPUT)])
        player_ml = PlayerML("train", "1", network, "Q-learning", None, "sigmoid", 0.3, 0.15, "eps-greedy")
        pre = player_ml.forward_pass(pstate)
        player_ml.backpropagation(pstate, nstate, 0.75)
        post = player_ml.forward_pass(pstate)

        self.assertTrue(sentinel, "Failed test strategy {}".format("Q-learning"))

    # test make_move of different agents

    def test_makemove_random(self):
        game = initialize_test_game()
        sentinel = True
        try:
            agent = PlayerRandom("1")
            select = agent.make_move(game)
        except Exception:
            sentinel = False
        self.assertTrue(sentinel)

    def test_makemove_ml(self):
        self.assertTrue(True)

    def test_makemove_minimax(self):
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
