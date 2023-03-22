import unittest, random

import numpy as np
from parameterized import parameterized
from src.agents.init_NN import initialize_NN, N_INPUT
from src.agents.PlayerML import PlayerML

random.seed(19)


class MyTestCase(unittest.TestCase):

    @parameterized.expand([
        ("normal", [10], [(10, 5), (10,)]),
        ("xavier", [12], [(12, 5), (12,)]),
        ("normalized-xavier", [20], [(20, 5), (20,)]),
        ("He", [15, 20, 12], [(15, 5), (20, 15), (12, 20), (12,)])
    ])
    def test_init_NN(self, init_mode, shape_in, expected_shape):
        net = initialize_NN(shape_in, init_mode)
        net_shapes = [l.shape for l in net]
        self.assertListEqual(net_shapes, expected_shape, init_mode)

    def test_forward_pass(self):
        # mode, role, network, ls, lamb, act_f, eps, lr, mvsel
        sentinel = True
        try:
            network = initialize_NN([10], "normal")
            pstate = np.array([random.randint(0, 1) for _ in range(N_INPUT)])
            nstate = np.array([random.randint(0, 1) for _ in range(N_INPUT)])
            player_ml = PlayerML("train", "1", network, "Q_learning", None, "sigmoid", 0.3, 0.15, "eps-greedy")
            pre = player_ml.forward_pass(pstate)
            player_ml.backpropagation(pstate, nstate, 0.75)
            post = player_ml.forward_pass(pstate)

        except Exception as e:
            sentinel = False

        self.assertTrue(sentinel, "Failed test strategy {}".format(ls))


if __name__ == '__main__':
    unittest.main()
