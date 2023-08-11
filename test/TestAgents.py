import copy
import unittest, random

from parameterized import parameterized

from src.agents.PlayerBM import PlayerBM
from src.agents.PlayerGT import PlayerGT
from src.agents.PlayerMDM import PlayerMDM
from src.agents.PlayerRandom import PlayerRandom
from src.agents.init_NN import initialize_NN, N_INPUT
from src.agents.PlayerML import PlayerML
from src.game.PokeGame import PokeGame
from src.game.constants import MIN_POW

random.seed(19)

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
           (("p2", "NOTYPE", 100, 80, 100, 100),
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
          [(("d1", "WATER", 100, 102, 115, 99),
            (("light_steel", "STEEL", 50), ("light_water", "WATER", 50))),
           (("d2", "NOTYPE", 175, 100, 100, 100),
            (("light_notype", "NOTYPE", 50), (None, None, None)))]],
         [[(("p1", "FIRE", 100, 100, 100, 100),
            (("light_psychic", "PSYCHIC", 50), ("light_fire", "FIRE", 50))),
           (("p2", "NOTYPE", 100, 80, 100, 100),
            (("light_notype", "NOTYPE", 50), (None, None, None)))],
          [(("d1", "WATER", 100, 102, 115, 99),
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

        self.assertEqual((exp_p1, exp_p2), (a1.game.player1_view, a1.game.player2_view))

    @parameterized.expand([
        ("p1", {'light_psychic': {'light_water': (-3.333, 3.333), 'light_notype': (-0.228, 0.228), 'switch d2': (0.456, -0.456), 'switch d3': (0.456, -0.456)},
                'light_fire': {'light_water': (-3.333, 3.333), 'light_notype': (-0.339, 0.339), 'switch d2': (0.689, -0.689), 'switch d3': (0.689, -0.689)},
                'light_bug': {'light_water': (-3.333, 3.333), 'light_notype': (-0.228, 0.228), 'switch d2': (0.456, -0.456), 'switch d3': (0.456, -0.456)},
                'switch p2': {'light_water': (-1.033, 1.033), 'light_notype': (-0.683, 0.683), 'switch d2': (0.0, 0.0), 'switch d3': (0.0, 0.0)},
                'switch p3': {'light_water': (-0.517, 1.033), 'light_notype': (-0.683, 0.683), 'switch d2': (0.0, 0.0), 'switch d3': (0.0, 0.0)}}),
        ("p2", {'light_steel': {'light_fire': (-0.061, 0.061), 'light_notype': (-0.228, 0.228), 'switch p2': (0.456, -0.456), 'switch p3': (0.456, -0.456)},
                'light_water': {'light_fire': (2.778, -2.778), 'light_notype': (2.778, -2.778), 'switch p2': (0.689, -0.689), 'switch p3': (0.689, -0.689)},
                'light_fairy': {'light_fire': (-0.294, 0.061), 'light_notype': (-0.461, 0.228), 'switch p2': (0.456, -0.456), 'switch p3': (0.456, -0.456)},
                'switch d2': {'light_fire': (-0.517, 1.033), 'light_notype': (-0.683, 0.683), 'switch p2': (0.0, 0.0), 'switch p3': (0.0, 0.0)},
                'switch d3': {'light_fire': (-3.333, 1.033), 'light_notype': (-0.683, 0.683), 'switch p2': (0.0, 0.0), 'switch p3': (0.0, 0.0)}})
    ])
    def test_gt_build_payoff_matrix(self, test_player, exp_mat):
        game = PokeGame(team_specs_for_game2)
        gt = PlayerGT(test_player)

        gt.game = copy.deepcopy(game)
        gt.fill_game_with_estimation()
        gt.build_payoff_matrix()
        test_mat = gt.payoff_mat

        if test_mat != exp_mat:
            for m in (test_mat, exp_mat):
                for k in m.keys():
                    print(k, m[k])

        self.assertDictEqual(exp_mat, test_mat)


if __name__ == '__main__':
    unittest.main()
