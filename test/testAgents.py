import copy
import unittest, random

import numpy as np
from parameterized import parameterized

from src.agents.PlayerBM import PlayerBM
from src.agents.PlayerGT import PlayerGT
from src.agents.PlayerMDM import PlayerMDM
from src.agents.PlayerRandom import PlayerRandom
from src.agents.nn_utils import initialize_nn, N_INPUT
from src.agents.PlayerRL import PlayerRL
from src.game.PokeGame import PokeGame
from src.game.constants import MIN_POW

random.seed(19)

# assert parameters order: (expected, actual)
team_specs_for_game = [[(("p1", "FIRE", 100, 100, 100, 100),
                         (("light_psychic", "PSYCHIC", 50), ("light_fire", "FIRE", 50))),
                        (("p2", "ELECTRIC", 100, 80, 100, 100),
                         (("light_grass", "GRASS", 50), ("light_electric", "ELECTRIC", 50)))],
                       [(("d1", "WATER", 100, 100, 100, 100),
                         (("light_steel", "STEEL", 50), ("light_water", "WATER", 50))),
                        (("d2", "DRAGON", 100, 80, 100, 100),
                         (("light_bug", "BUG", 50), ("light_dragon", "DRAGON", 50)))]]

team_specs_for_game2 = [[(("p1", "FIRE", 100, 100, 100, 100),
                          (("light_psychic", "PSYCHIC", 50), ("light_fire", "FIRE", 50), ("light_bug", "BUG", 50))),
                         (("p2", "ELECTRIC", 100, 100, 100, 100),
                          (("light_grass", "GRASS", 50), ("light_electric", "ELECTRIC", 50),
                           ("light_ghost", "GHOST", 50))),
                         (("p3", "GRASS", 100, 100, 100, 100),
                          (("light_grass", "GRASS", 50), ("light_ice", "ICE", 50), ("light_fighting", "FIGHTING", 50)))],
                        [(("d1", "WATER", 100, 100, 100, 100),
                          (("light_steel", "STEEL", 50), ("light_water", "WATER", 50), ("light_fairy", "FAIRY", 50))),
                         (("d2", "DRAGON", 100, 100, 100, 100),
                          (("light_bug", "BUG", 50), ("light_dragon", "DRAGON", 50), ("light_ground", "GROUND", 50))),
                         (("d3", "BUG", 100, 100, 100, 100),
                          (("light_bug", "BUG", 50), ("light_normal", "NORMAL", 50), ("light_dark", "DARK", 50)))]]


class MyTestCase(unittest.TestCase):

    @parameterized.expand([
        ("normal", [10], [(10, N_INPUT), (10,)]),
        ("xavier", [12], [(12, N_INPUT), (12,)]),
        ("normalized-xavier", [20], [(20, N_INPUT), (20,)]),
        ("He", [15, 20, 12], [(15, N_INPUT), (20, 15), (12, 20), (12,)])
    ])
    def test_init_NN(self, init_mode, shape_in, expected_shape):
        net = initialize_nn(shape_in, init_mode)
        net_shapes = [l.shape for l in net]
        self.assertListEqual(expected_shape, net_shapes, init_mode)

    def test_forward_pass(self):
        # mode, role, network, ls, lamb, act_f, eps, lr, mvsel
        sentinel = True
        network = initialize_nn([10], "normal")
        pstate = [random.randint(0, 1) for _ in range(N_INPUT)]
        nstate = [random.randint(0, 1) for _ in range(N_INPUT)]

        try:
            player_ml = PlayerRL("p1", "train", network, "Q-learning", None, "sigmoid", 0.3, 0.15, "eps-greedy")
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
        ("p1", "light_psychic", False),
        ("p2", "light_water", False),
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
        ("p1", False, "light_psychic"),
        ("p2", False, "light_water"),
        ("p1", True, "switch p2"),
        ("p2", True, "light_water")
    ])
    def test_makemove_bm(self, test_player, full_view, exp_move):
        game = PokeGame(team_specs_for_game)
        agent = PlayerBM(test_player)

        if full_view:
            game.player1_view = copy.deepcopy(game.game_state)
            game.player2_view = copy.deepcopy(game.game_state)

        test = agent.make_move(game)

        self.assertEqual(exp_move, test)

    @parameterized.expand([
        ([], [],
         [[(("p1", "FIRE", 100, 100, 100, 100),
            (("light_psychic", "PSYCHIC", 50), ("light_fire", "FIRE", 50))),
           (("p2", "ELECTRIC", 100, 80, 100, 100),
            (("light_grass", "GRASS", 50), ("light_electric", "ELECTRIC", 50)))],
          [(("d1", "WATER", 100, 100, 100, 100),
            (("light_water", "WATER", MIN_POW), ("light_notype", "NOTYPE", MIN_POW))),
           (("d2", "NOTYPE", 175, 100, 100, 100),
            (("light_notype", "NOTYPE", MIN_POW), (None, None, None)))]],
         [[(("p1", "FIRE", 100, 100, 100, 100),
            (("light_fire", "FIRE", MIN_POW), ("light_notype", "NOTYPE", MIN_POW))),
           (("p2", "NOTYPE", 175, 100, 100, 100),
            (("light_notype", "NOTYPE", MIN_POW), (None, None, None)))],
          [(("d1", "WATER", 100, 100, 100, 100),
            (("light_water", "WATER", MIN_POW), ("light_notype", "NOTYPE", MIN_POW))),
           (("d2", "NOTYPE", 175, 100, 100, 100),
            (("light_notype", "NOTYPE", MIN_POW), (None, None, None)))]]),
        (["light_psychic"], ["light_steel"],
         [[(("p1", "FIRE", 100, 100, 100, 100),
            (("light_psychic", "PSYCHIC", 50), ("light_fire", "FIRE", 50))),
           (("p2", "ELECTRIC", 100, 80, 100, 100),
            (("light_grass", "GRASS", 50), ("light_electric", "ELECTRIC", 50)))],
          [(("d1", "WATER", 100, 102, 120, 99),
            (("light_steel", "STEEL", 50), ("light_water", "WATER", 50))),
           (("d2", "NOTYPE", 175, 100, 100, 100),
            (("light_notype", "NOTYPE", 50), (None, None, None)))]],
         [[(("p1", "FIRE", 100, 100, 100, 100),
            (("light_psychic", "PSYCHIC", 50), ("light_fire", "FIRE", 50))),
           (("p2", "NOTYPE", 175, 100, 100, 100),
            (("light_notype", "NOTYPE", 50), (None, None, None)))],
          [(("d1", "WATER", 100, 102, 120, 99),
            (("light_steel", "STEEL", 50), ("light_water", "WATER", 50))),
           (("d2", "NOTYPE", 175, 100, 100, 100),
            (("light_notype", "NOTYPE", 50), (None, None, None)))]]
         )
    ])
    def test_gt_fill_game(self, p1_moves, p2_moves, exp_specs_p1view, exp_specs_p2view):
        game = PokeGame(team_specs_for_game)

        for m1, m2 in zip(p1_moves, p2_moves):
            game.play_round(m1, m2, 0.85, True)

        a1 = PlayerGT("p1")
        a1.make_move(game)

        exp_p1 = PokeGame.GameStruct(exp_specs_p1view)
        exp_p2 = PokeGame.GameStruct(exp_specs_p2view)
        for p, q in zip(exp_p1.team1 + exp_p1.team2, a1.game.player1_view.team1 + a1.game.player1_view.team2):
            p.cur_hp = q.cur_hp
        for p, q in zip(exp_p2.team1 + exp_p2.team2, a1.game.player2_view.team1 + a1.game.player2_view.team2):
            p.cur_hp = q.cur_hp

        if (exp_p1, exp_p2) != (a1.game.player1_view, a1.game.player2_view):
            print(exp_p1, exp_p2, a1.game.player1_view, a1.game.player2_view, sep='\n')

        self.assertEqual((exp_p1, exp_p2), (a1.game.player1_view, a1.game.player2_view),
                         msg="exp: {},\nact: {}".format(exp_p1, a1.game.player1_view))

    @parameterized.expand([
        ("p1",
         {'light_psychic': {'light_water': (-3.333, 2.322), 'light_notype': (-0.228, 0.0), 'switch d2': (0.456, -0.456), 'switch d3': (0.456, -0.456)},
          'light_fire': {'light_water': (-3.333, 2.433), 'light_notype': (-0.339, 0.111), 'switch d2': (0.689, -0.689), 'switch d3': (0.689, -0.689)},
          'light_bug': {'light_water': (-3.333, 2.322), 'light_notype': (-0.228, 0.0), 'switch d2': (0.456, -0.456), 'switch d3': (0.456, -0.456)},
          'switch p2': {'light_water': (-1.033, 0.689), 'light_notype': (-0.683, 0.456), 'switch d2': (0.0, 0.0), 'switch d3': (0.0, 0.0)},
          'switch p3': {'light_water': (-0.517, 0.689), 'light_notype': (-0.683, 0.456), 'switch d2': (0.0, 0.0), 'switch d3': (0.0, 0.0)}}),
        ("p2",
         {'light_fire': {'light_steel': (-0.111, -0.294), 'light_water': (-2.433, 2.778), 'light_fairy': (-0.111, -0.294), 'switch d2': (0.689, -0.517), 'switch d3': (0.689, -3.333)},
          'light_notype': {'light_steel': (0.0, -0.461), 'light_water': (-2.322, 2.778), 'light_fairy': (0.0, -0.461), 'switch d2': (0.456, -0.683), 'switch d3': (0.456, -0.683)},
          'switch p2': {'light_steel': (-0.456, 0.456), 'light_water': (-0.689, 0.689), 'light_fairy': (-0.456, 0.456), 'switch d2': (0.0, 0.0), 'switch d3': (0.0, 0.0)},
          'switch p3': {'light_steel': (-0.456, 0.456), 'light_water': (-0.689, 0.689), 'light_fairy': (-0.456, 0.456), 'switch d2': (0.0, 0.0), 'switch d3': (0.0, 0.0)}})
    ])
    def test_gt_build_payoff_matrix(self, test_player, exp_mat):
        game = PokeGame(team_specs_for_game2)
        gt = PlayerGT(test_player)

        gt.game = copy.deepcopy(game)
        gt.fill_game_with_estimation()
        gt.build_payoff_matrix()
        test_mat = gt.payoff_mat

        if test_mat != exp_mat:
            for m, n in zip((test_mat, exp_mat), ("test", "exp")):
                print(n)
                for k in m.keys():
                    print(k, m[k])

        for k1, k2 in zip(test_mat.keys(), exp_mat.keys()):
            for k11, k22 in zip(test_mat[k1].keys(), exp_mat[k2].keys()):
                if test_mat[k1][k11][1] != exp_mat[k2][k22][1]:
                    print("->>>", k1, k11, test_mat[k1][k11][1], k2, k22, exp_mat[k2][k22][1])
        for k1, k2 in zip(test_mat.keys(), exp_mat.keys()):
            for k11, k22 in zip(test_mat[k1].keys(), exp_mat[k2].keys()):
                if test_mat[k1][k11][0] != exp_mat[k2][k22][0]:
                    print("-<<<", k1, k11, test_mat[k1][k11][0], k2, k22, exp_mat[k2][k22][0])

        self.assertDictEqual(exp_mat, test_mat)

    @parameterized.expand([
        ({"a1": {"b1": (1, 1), "b2": (0, 0)}, "a2": {"b1": (0, 0), "b2": (1, 1)}},
         {"a1": {"b1": (1, 1), "b2": (0, 0)}, "a2": {"b1": (0, 0), "b2": (1, 1)}}),
        ({"a1": {"b1": (0, 0), "b2": (1, 1)}, "a2": {"b1": (1, 1), "b2": (2, 2)}},
         {"a2": {"b2": (2, 2)}}),
        (None, {'switch p3': {'light_water': (-0.517, 0.689)}})
    ])
    def test_remove_strictly_dominated_strategies(self, init, exp):
        game = PokeGame(team_specs_for_game2)
        agent = PlayerGT("p1")
        agent.game = game
        agent.fill_game_with_estimation()
        agent.build_payoff_matrix()

        if init is not None:
            agent.payoff_mat = init
        agent.remove_strictly_dominated_strategies()

        self.assertDictEqual(exp, agent.payoff_mat)

    @parameterized.expand([
        ("p1", {'a': {'c': (2, 1), 'd': (0, 0)}, 'b': {'c': (0, 0), 'd': (1, 2)}},
         ((np.array([1., 0.]), np.array([1., 0.])), np.array([2., 1.]))),
         #((np.array([0., 1.]), np.array([0., 1.])), np.array([1., 2.]))),
        ("p2", {'a': {'c': (5, 5), 'd': (0, 0)}, 'b': {'c': (0, 0), 'd': (5, 5)}},
         ((np.array([1., 0.]), np.array([1., 0.])), np.array([5., 5.]))),
         #((np.array([0., 1.]), np.array([0., 1.])), np.array([5., 5.]))),
        ("p1", {'a': {'d': (3, -1), 'e': (-1, 1)}, 'b': {'d': (0, 0), 'e': (0, 0)}, 'c': {'d': (-1, 2), 'e': (2, -1)}},
         ((np.array([0.6, 0., 0.4]), np.array([0.42857143, 0.57142857])), np.array([0.71428571, 0.2])))
    ])
    def test_ne_for_move(self, player, payoff_mat, exp):
        agent = PlayerGT(player)
        agent.game = PokeGame(team_specs_for_game2)
        agent.fill_game_with_estimation()
        agent.build_payoff_matrix()
        agent.remove_strictly_dominated_strategies()
        agent.payoff_mat = payoff_mat
        act = agent.nash_equilibrium_for_move()

        # comparison of numpy arrays is special
        test_payoffs = True
        for exp_expo, act_expo in zip(exp[1], act[1]):
            test_payoffs &= round(exp_expo, 8) == round(act_expo, 8)  # numpy is annoying with floats in arrays

        test_prob = True
        for exp_probs, act_probs in zip(exp[0], act[0]):
            for e1, e2 in zip(exp_probs, act_probs):
                test_prob &= round(e1, 8) == round(e2, 8)
                print(round(e1, 8) - round(e2, 8))

        self.assertTrue(test_payoffs and test_prob, msg="exp: {}\nact: {}".format(exp, act))

    @parameterized.expand([
        ("p1", "switch p3"),
        ("p2", "light_water")
    ])
    def test_regular_move(self, role, exp):
        agent = PlayerGT(role)
        agent.game = PokeGame(team_specs_for_game2)
        act = agent.regular_move()
        self.assertEqual(exp, act)

    @parameterized.expand([
        ("p1", "switch p2"),
        ("p2", "switch d2")
    ])
    def test_post_faint_move(self, role, exp):
        agent = PlayerGT(role)
        agent.game = PokeGame(team_specs_for_game2)

        if role == "p1":
            agent.game.game_state.on_field1.cur_hp = agent.game.player1_view.on_field1.cur_hp = agent.game.player2_view.on_field1.cur_hp = int()
        elif role == "p2":
            agent.game.game_state.on_field2.cur_hp = agent.game.player1_view.on_field2.cur_hp = agent.game.player2_view.on_field2.cur_hp = int()

        act = agent.post_faint_move()
        self.assertEqual(exp, act)

    @parameterized.expand([
        ("p1", "switch p3"),
        ("p2", "light_water")
    ])
    def test_make_move_gt(self, player, exp):
        agent = PlayerGT(player)
        act = agent.make_move(PokeGame(team_specs_for_game2))
        self.assertEqual(exp, act)

    def test_player_gt_complete_game(self):
        fail = False
        out = str()
        try:
            nb = 10
            max_rounds = 50
            players = [PlayerRandom("p1"), PlayerGT("p2")]

            for i in range(nb):
                game = PokeGame(team_specs_for_game2)
                turn_nb = 1
                game_finished = False

                # game loop
                while not game_finished and turn_nb < max_rounds:
                    of1, of2 = game.game_state.on_field1, game.game_state.on_field2
                    player1_move = players[0].make_move(game) if of1.cur_hp and of2.cur_hp or not of1.cur_hp else None
                    player2_move = players[1].make_move(game) if of1.cur_hp and of2.cur_hp or not of2.cur_hp else None

                    game.play_round(player1_move, player2_move)
                    game_finished = game.is_end_state(None)

                    if not game_finished and of1.cur_hp > 0 and of2.cur_hp > 0:
                        # turn change once attacks have been applied and fainted Pokemon switched
                        turn_nb += 1
        except Exception as e:
            fail = True
            out = "-> " + e.__repr__()
        self.assertFalse(fail, msg=out)


if __name__ == '__main__':
    unittest.main()
