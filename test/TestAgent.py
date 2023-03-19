import unittest, random

from parameterized import parameterized
from src.agents.init_NN import initialize_NN, N_INPUT, N_OUT

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

    def test_default(self):
        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()
