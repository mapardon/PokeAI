import os, sys

sys.path.append(os.getcwd() + '/..')

import copy
import multiprocessing
import time

from matplotlib import pyplot as plt

from src.db.dbmanager import save_new_ml_agent
from src.agents.nn_utils import initialize_nn
from src.agents.PlayerRL import PlayerRL
from src.agents.PlayerGA import PlayerGA
from src.game.GameEngine import GameEngine
from src.game.GameEstimation import fill_game_with_estimation
from src.experiments.AltImplementations import GameEngineAlt, TestParamsAlt
from src.game.PokeGame import PokeGame
from src.game.GameEngineParams import TestParams, TrainParams

SHORT = False
if SHORT:
    # Run tests with small repetitions to check if everything goes right
    GT_STATE_EVAL = 5
    ML_TRAIN_LOOPS = 1
    RL_N_TRAIN = 10
    RL_N_TEST = 10
    GA_N_TEST = 10
    GA_POP_SIZE = 2
    GA_N_GEN = 2
    GA_STATE_VEC_TEST = 10
    GA_STATE_VEC_LOOPS = 1
    GA_TRAIN_PARS = 2, "xavier", [66, 77, 1], 1, 1 / 3, 0.0, 0.00001
    POP_SIZE_FULL_GAME = 2
    PLOT_NAMES = ("testrl.pdf", "testga.pdf")
else:
    # Run complete tests
    GT_STATE_EVAL = 1000
    ML_TRAIN_LOOPS = 3
    RL_N_TRAIN = 10000
    RL_N_TEST = 1000
    GA_N_TEST = 1000
    GA_POP_SIZE = 10
    GA_N_GEN = 10
    GA_STATE_VEC_TEST = 1000
    GA_STATE_VEC_LOOPS = 10
    GA_TRAIN_PARS = 10, "xavier", [66, 77, 1], 10, 1 / 3, 0.0, 0.00001
    POP_SIZE_FULL_GAME = 10
    PLOT_NAMES = ("plots/rl_perf.pdf", "plots/ga_perf.pdf")


class Experiments:
    """
        Implements experiments made to evaluate optimal values of hyperparameters of different models developed in the
        project
    """

    @staticmethod
    def run_all_tests():

        ts = [
            multiprocessing.Process(target=Experiments.weights_for_gt_state_eval, args=()),
            multiprocessing.Process(target=Experiments.training_rl_agent, args=()),
            multiprocessing.Process(target=Experiments.training_ga_agent, args=()),
            multiprocessing.Process(target=Experiments.training_params_for_rl, args=()),
            multiprocessing.Process(target=Experiments.state_vector_with_ga, args=()),
            multiprocessing.Process(target=Experiments.training_params_for_ga, args=()),
            multiprocessing.Process(target=Experiments.full_game_rl_perf, args=()),
            multiprocessing.Process(target=Experiments.full_game_ga_perf, args=())
        ]

        for t in ts:
            t.start()

        for t in ts:
            t.join()

    """
        *
        * Game theory
        *
    """

    @staticmethod
    def weights_for_gt_state_eval():
        """
            Test performance of PlayerGT agent with different weights for the parameters of payoff computation
        """

        def tune_weights(test_weights):
            out = "\nExperiment: weights for GT\n\n"
            for weights in test_weights:
                pars = TestParamsAlt("test", "gtalt", "random", 0.1, None, None, "random", "random", GT_STATE_EVAL,
                                     weights)
                ge = GameEngineAlt(pars, PokeGame)

                res = ge.test_mode(False)
                out += "Config: {}, res={}%\n".format(weights, 100 * res)

            print(out)

        test_weights = [(i, j, k, l) for i in range(2) for j in range(2) for k in range(2) for l in range(2)] + \
                       [(i, j, k, l) for i in [2, 5] for j in [2, 5] for k in [2, 5] for l in [2, 5]]

        l = len(test_weights)
        t1 = multiprocessing.Process(target=tune_weights, args=(test_weights[:l // 4],))
        t2 = multiprocessing.Process(target=tune_weights, args=(test_weights[l // 4:l // 2],))
        t3 = multiprocessing.Process(target=tune_weights, args=(test_weights[l // 2:3 * l // 4],))
        t4 = multiprocessing.Process(target=tune_weights, args=(test_weights[3 * l // 4:],))

        for t in [t1, t2, t3, t4]:
            t.start()

        for t in [t1, t2, t3, t4]:
            t.join()

    """
        *
        * NN training on simple games
        *
    """

    @staticmethod
    def agent_estimations(ts, agent):
        """
            Show the estimation that an agent using a neural network makes for its possible moves.

            :param ts: Team specs to build the game
            :param agent: Agent to evaluate (PlayerNN, PlayerRL or PlayerGA)
        """

        out = str()
        for full, p in zip([True, False], ["full view", "player view"]):
            g = PokeGame(ts)
            for m in g.get_moves_from_state("p1", state=g.game_state):
                for n in g.get_moves_from_state("p2", state=g.game_state):
                    game_cp = copy.deepcopy(g)
                    _ = game_cp.play_round(m, n)
                    fill_game_with_estimation("p1", game_cp)
                    if full:
                        s = game_cp.get_cur_state()
                    else:
                        s = game_cp.get_player_view("p1")
                    out += "({})   {} - {}: {}\n".format(p, m, n,
                                                         round(agent.forward_pass(g.get_numeric_repr(s, "p1")), 5))
        return out

    @staticmethod
    def training_rl_agent():
        """
            Test the performance of an agent using a neural network trained with gradient descent
        """

        def simple_game():
            out = "\nExperiment: RL training\n\n"
            # First, test with a simplified game (1 vs 1 w/ 2 attacks, one attack has no effect, which should be noticed
            # by the agent). The team compositions never change so the agent must not deal with generalization
            ts_1 = [[(("p1", "POISON", 500, 100, 100, 101),
                      (("light_poison", "POISON", 50), ("light_fighting", "FIGHTING", 50)))],
                    [(("d1", "STEEL", 500, 100, 100, 100),
                      (("light_steel", "STEEL", 50), ("light_bug", "BUG", 50)))]]

            out += "Simple game\n"
            for i in range(ML_TRAIN_LOOPS):
                nn = initialize_nn([18, 60, 1], "xavier")

                # train
                pars = TrainParams("train", 0.0015, "rl", "rl", 0.1, (nn, "sigmoid", "SARSA"), (nn, "sigmoid", "SARSA"),
                                   ts_1[0], ts_1[1], RL_N_TRAIN)
                ge = GameEngine(pars)
                ge.train_mode(False)

                # test
                pars = TestParams("test", "rl", "random", 0.0, (nn, "sigmoid", "SARSA"), None, ts_1[0], ts_1[1],
                                  RL_N_TEST)
                ge = GameEngine(pars, None, None)
                out += "Loop {}, score: {}\n".format(i, ge.test_mode())
                out += Experiments.agent_estimations(ts_1, PlayerRL("p1", "test", nn, "SARSA", "sigmoid", 0.0, 0.0))
            print(out)

        def more_complicated_game():
            out = "\nExperiment: RL training\n\n"
            # Slightly more complicated game
            ts_2 = [[(("p1", "FIRE", 200, 100, 100, 100),
                      (("heavy_fire", "FIRE", 100), ("light_steel", "STEEL", 100))),
                     (("p2", "GRASS", 200, 100, 100, 100),
                      (("heavy_grass", "GRASS", 100), ("light_electric", "ELECTRIC", 100)))],
                    [(("d1", "WATER", 200, 100, 100, 100),
                      (("heavy_water", "WATER", 100), ("light_ground", "GROUND", 100))),
                     (("d2", "BUG", 200, 80, 100, 100),
                      (("heavy_bug", "BUG", 100), ("light_fire", "FIRE", 100)))]]

            out += "More complicated game\n"
            for i in range(ML_TRAIN_LOOPS):
                nn = initialize_nn([36, 72, 1], "xavier")

                # train
                pars = TrainParams("train", 0.0015, "rl", "rl", 0.1, (nn, "sigmoid", "SARSA"), (nn, "sigmoid", "SARSA"),
                                   ts_2[0], ts_2[1], RL_N_TRAIN)
                ge = GameEngine(pars)
                ge.train_mode(False)

                # test
                pars = TestParams("test", "rl", "random", 0.0, (nn, "sigmoid", "SARSA"), None, ts_2[0], ts_2[1],
                                  RL_N_TEST)
                ge = GameEngine(pars, None, None)
                out += "Loop {}, score: {}\n".format(i, ge.test_mode())
                out += Experiments.agent_estimations(ts_2, PlayerRL("p1", "test", nn, "SARSA", "sigmoid", 0.0, 0.0))
            print(out)

        processes = [multiprocessing.Process(target=simple_game, args=()),
                     multiprocessing.Process(target=more_complicated_game(), args=())]

        for p in processes:
            p.start()

        for p in processes:
            p.join()

    @staticmethod
    def training_ga_agent():
        """
            Test the performance of an agent using a neural network trained with a genetic algorithm
        """

        def fitness_eval(network, act_f, ts_p1, ts_p2):
            """
                Fitness function for the GA
            """
            pars = TestParams("test", "ga", "random", 0.0, (network, act_f), None, ts_p1, ts_p2, GA_N_TEST)
            ge = GameEngine(pars)
            ret = ge.test_mode()
            return ret

        def simple_game():
            out = "\nExperiment: GA training\n\n"
            # First, test with a simplified game (1 vs 1 w/ 2 attacks, one attack has no effect, which should be noticed
            # by the agent). The team compositions never change so the agent must not deal with generalization
            ts_1 = [[(("p1", "POISON", 500, 100, 100, 101),
                      (("light_poison", "POISON", 50), ("light_fighting", "FIGHTING", 50)))],
                    [(("d1", "STEEL", 500, 100, 100, 100),
                      (("light_steel", "STEEL", 50), ("light_bug", "BUG", 50)))]]

            out += "Simple game\n"
            agent = PlayerGA("p1", initialize_nn([18, 60, 1], "normal"), "sigmoid")
            for i in range(ML_TRAIN_LOOPS):
                # train (& test)
                res = agent.evolution(GA_POP_SIZE, "xavier", [18, 60, 1], GA_N_GEN, 1 / 3, fitness_eval,
                                      ("sigmoid", ts_1[0], ts_1[1]))
                out += "Loop {}, score: {}\n".format(i, res[1])
                out += Experiments.agent_estimations(ts_1, PlayerGA("p1", res[0], "sigmoid"))
            print(out)

        def more_complicated_game():
            out = "\nExperiment: GA training\n\n"
            # Slightly more complicated game
            ts_2 = [[(("p1", "FIRE", 200, 100, 100, 100),
                      (("heavy_fire", "FIRE", 100), ("light_steel", "STEEL", 100))),
                     (("p2", "GRASS", 200, 100, 100, 100),
                      (("heavy_grass", "GRASS", 100), ("light_electric", "ELECTRIC", 100)))],
                    [(("d1", "WATER", 200, 100, 100, 100),
                      (("heavy_water", "WATER", 100), ("light_ground", "GROUND", 100))),
                     (("d2", "BUG", 200, 80, 100, 100),
                      (("heavy_bug", "BUG", 100), ("light_fire", "FIRE", 100)))]]

            out += "More complicated game\n"
            agent = PlayerGA("p1", initialize_nn([36, 72, 1], "normal"), "sigmoid")
            for i in range(ML_TRAIN_LOOPS):
                # train (& test)
                res = agent.evolution(GA_POP_SIZE, "xavier", [36, 72, 1], GA_N_GEN, 1 / 3, fitness_eval,
                                      ("sigmoid", ts_2[0], ts_2[1]))
                out += "Loop {}, score: {}\n".format(i, res[1])
                out += Experiments.agent_estimations(ts_2, PlayerGA("p1", res[0], "sigmoid"))
            print(out)

        processes = [multiprocessing.Process(target=simple_game, args=()),
                     multiprocessing.Process(target=more_complicated_game, args=())]

        for p in processes:
            p.start()

        for p in processes:
            p.join()

    """
        *
        * Training parameters
        *
    """

    @staticmethod
    def training_params_for_rl():
        """
            Test the performance of neural networks trained with the Rl algorithm and varying parameter values
        """

        def exp_init_mode():
            out = "\nExperiment: training parameters for RL\n\n"
            out += "Init mode\n"

            for im in ["xavier", "normalized-xavier", "normal", "He"]:
                nn = initialize_nn([66, 77, 1], im)

                # train
                pars = TrainParams("train", 0.0015, "rl", "rl", 0.1, (nn, "sigmoid", "SARSA"),
                                   (nn, "sigmoid", "SARSA"), "random", "random", RL_N_TRAIN)
                ge = GameEngine(pars, None, None)
                ge.train_mode(False)

                # test
                pars = TestParams("test", "rl", "random", 0.0, (nn, "sigmoid", "SARSA"), None, "random", "random",
                                  RL_N_TEST)
                ge = GameEngine(pars, None, None)
                out += "Init mode {}, score: {}\n".format(im, ge.test_mode())

            print(out)

        def exp_hidden_layer_size():
            out = "\nExperiment: training parameters for RL\n\n"
            out += "Hidden layer size\n"

            for hl_size in [33, 66, 77, 198, 264]:
                nn = initialize_nn([66, hl_size, 1], "xavier")

                # train
                pars = TrainParams("train", 0.0015, "rl", "rl", 0.1, (nn, "sigmoid", "SARSA"),
                                   (nn, "sigmoid", "SARSA"), "random", "random", RL_N_TRAIN)
                ge = GameEngine(pars, None, None)
                ge.train_mode(False)

                # test
                pars = TestParams("test", "rl", "random", 0.0, (nn, "sigmoid", "SARSA"), None, "random", "random",
                                  RL_N_TEST)
                ge = GameEngine(pars, None, None)
                out += "Hidden layer size {}, score: {}\n".format(hl_size, ge.test_mode())

            print(out)

        def exp_eps_greedy_value():
            out = "\nExperiment: training parameters for RL\n\n"
            out += "EPS-greedy\n"

            for eps in [0.05, 0.1, 0.15, 0.25, 0.4]:
                nn = initialize_nn([66, 77, 1], "xavier")

                # train
                pars = TrainParams("train", 0.0015, "rl", "rl", eps, (nn, "sigmoid", "SARSA"),
                                   (nn, "sigmoid", "SARSA"), "random", "random", RL_N_TRAIN)
                ge = GameEngine(pars, None, None)
                ge.train_mode(False)

                # test
                pars = TestParams("test", "rl", "random", 0.0, (nn, "sigmoid", "SARSA"), None, "random", "random",
                                  RL_N_TEST)
                ge = GameEngine(pars, None, None)
                out += "Eps-greedy {}, score: {}\n".format(eps, ge.test_mode())

            print(out)

        def exp_lr_value():
            out = "\nExperiment: training parameters for RL\n\n"
            out += "LR value\n"

            for lr in [0.0015, 0.005, 0.0075, 0.01]:
                nn = initialize_nn([66, 77, 1], "xavier")

                # train
                pars = TrainParams("train", lr, "rl", "rl", 0.1, (nn, "sigmoid", "SARSA"),
                                   (nn, "sigmoid", "SARSA"), "random", "random", RL_N_TRAIN)
                ge = GameEngine(pars, None, None)
                ge.train_mode(False)

                # test
                pars = TestParams("test", "rl", "random", 0.0, (nn, "sigmoid", "SARSA"), None, "random", "random",
                                  RL_N_TEST)
                ge = GameEngine(pars, None, None)
                out += "Lr value {}, score: {}\n".format(lr, ge.test_mode())

            print(out)

        ps = [multiprocessing.Process(target=exp_init_mode, args=()),
              multiprocessing.Process(target=exp_hidden_layer_size, args=()),
              multiprocessing.Process(target=exp_eps_greedy_value, args=()),
              multiprocessing.Process(target=exp_lr_value, args=())]

        for p in ps:
            p.start()

        for p in ps:
            p.join()

    @staticmethod
    def state_vector_with_ga():
        """
            Test performance of neural networks using different numeric representation of the game while training with
            the genetic algorithm (10 generations of populations of 10 individuals).
        """

        class FitnessEval:
            def __init__(self, poke_game_type):
                self.poke_game_type = poke_game_type

            def __call__(self, nn):
                pars = TestParams("test", "ga", "random", 0.1, (nn, "sigmoid"), None, "random", "random",
                                  GA_STATE_VEC_TEST)
                ge = GameEngineAlt(pars, self.poke_game_type)
                ret = ge.test_mode(False)
                return ret

        def run_exp(s, pg_type, dims):
            out = "\nExperiment: state vector for GA\n"

            t = time.perf_counter()
            fitness_eval = FitnessEval(pg_type)
            out += s
            agent = PlayerGA("p1", [66, 77, 1], "sigmoid")
            # for i in range(GA_STATE_VEC_LOOPS):
            for i in range(1):
                res = agent.evolution(GA_POP_SIZE, "xavier", dims, GA_N_GEN, 1 / 3, fitness_eval, tuple())
                out += "Loop {}: {}\n".format(i, str(res[1]))
            print(dims, time.perf_counter() - t)
            print(out)

        ps = [multiprocessing.Process(target=run_exp, args=("Regular PokeGame\n", PokeGame, [66, 77, 1])),
              #multiprocessing.Process(target=run_exp, args=("Types ohe\n", PokeGameAlt2, [492, 246, 1])),
              #multiprocessing.Process(target=run_exp, args=("Full ohe\n", PokeGameAlt1, [678, 338, 1]))
              ]

        for p in ps:
            p.start()

        for p in ps:
            p.join()

    @staticmethod
    def training_params_for_ga():
        """
            Test the performance of neural networks trained with the GA algorithm and varying parameter values
        """

        def fitness_eval(network, act_f, ts_p1, ts_p2):
            """
                Fitness function for the GA
            """
            pars = TestParams("test", "ga", "random", 0.0, (network, act_f), None, ts_p1, ts_p2, GA_N_TEST)
            ge = GameEngine(pars)
            ret = ge.test_mode()
            return ret

        # Base parameters
        pop_size, init_mode, net_shape, n_gen, elite_pro, mu_mean, mu_std = GA_TRAIN_PARS
        fitness_f, fitness_f_args = fitness_eval, ("sigmoid", "random", "random")

        def exp_hidden_layer_size():
            out = "\nExperiment: training parameters for GA\n\n"
            out += "Hidden layer size\n"
            agent = PlayerGA("p1", initialize_nn([18, 60, 1], "normal"), "sigmoid")
            for hl_size in [33, 66, 77, 198, 264]:
                res = agent.evolution(10, init_mode, [66, hl_size, 1], n_gen, elite_pro, fitness_f,
                                      fitness_f_args, mu_mean, mu_std)
                out += "pop size {}, score: {}\n".format(hl_size, res[1])
            print(out)

        def exp_pop_size():
            out = "\nExperiment: training parameters for GA\n\n"
            out += "Population size\n"
            agent = PlayerGA("p1", initialize_nn([18, 60, 1], "normal"), "sigmoid")
            for ps in [5, 10, 15, 20, 30]:
                res = agent.evolution(ps, init_mode, net_shape, n_gen, elite_pro, fitness_f, fitness_f_args,
                                      mu_mean, mu_std)
                out += "pop size {}, score: {}\n".format(ps, res[1])
            print(out)

        def exp_init_mode():
            out = "\nExperiment: training parameters for GA\n\n"
            out += "Init mode\n"
            agent = PlayerGA("p1", initialize_nn([18, 60, 1], "normal"), "sigmoid")
            for im in ["xavier", "normalized-xavier", "normal", "He"]:
                res = agent.evolution(pop_size, im, net_shape, n_gen, elite_pro, fitness_f, fitness_f_args,
                                      mu_mean, mu_std)
                out += "init mode {}, score: {}\n".format(im, res[1])
            print(out)

        def exp_nb_gens():
            out = "\nExperiment: training parameters for GA\n\n"
            out += "# of generations\n"
            agent = PlayerGA("p1", initialize_nn([18, 60, 1], "normal"), "sigmoid")
            for ng in [5, 10, 15, 20, 30]:
                res = agent.evolution(pop_size, init_mode, net_shape, ng, elite_pro, fitness_f, fitness_f_args,
                                      mu_mean, mu_std)
                out += "# gens {}, score: {}\n".format(ng, res[1])
            print(out)

        def exp_elite_prop():
            out = "\nExperiment: training parameters for GA\n\n"
            out += "Elite proportion\n"
            agent = PlayerGA("p1", initialize_nn([18, 60, 1], "normal"), "sigmoid")
            for ep in [1 / 10, 1 / 5, 1 / 3, 1 / 2]:
                res = agent.evolution(pop_size, init_mode, net_shape, n_gen, ep, fitness_f, fitness_f_args,
                                      mu_mean, mu_std)
                out += "elite prop {}, score: {}\n".format(ep, res[1])
            print(out)

        def exp_mu_pars():
            out = "\nExperiment: training parameters for GA\n\n"
            out += "Mu std\n"
            agent = PlayerGA("p1", initialize_nn([18, 60, 1], "normal"), "sigmoid")
            for mu, std in [(0.0, 0.00001), (0.0, 0.0001), (0.0, 0.000001), (0.0001, 0.00001), (-0.0001, 0.00001)]:
                res = agent.evolution(pop_size, init_mode, net_shape, n_gen, elite_pro, fitness_f, fitness_f_args,
                                      mu, std)
                out += "mu/std ({}, {}), score: {}\n".format(mu, std, res[1])
            print(out)

        ps = [multiprocessing.Process(target=exp_hidden_layer_size, args=()),
              multiprocessing.Process(target=exp_pop_size, args=()),
              multiprocessing.Process(target=exp_init_mode, args=()),
              multiprocessing.Process(target=exp_nb_gens, args=()),
              multiprocessing.Process(target=exp_elite_prop, args=()),
              multiprocessing.Process(target=exp_mu_pars, args=())
              ]

        for p in ps:
            p.start()

        for p in ps:
            p.join()

    """
        *
        * Final performance
        *
    """

    @staticmethod
    def full_game_rl_perf():
        """
            Test performance of network trained with RL with best values of parameters (determined in previous test)
            over longer training.
        """

        out = "\nExperiment: RL training\n\n"
        # Complete game 3 vs 3 with random teams
        out += "RL - Complete game\n"

        n_train = 10
        perfs = list()

        # network initialization NB: here we use the same network trained on several episodes
        nn = initialize_nn([66, 77, 1], "xavier")

        # first test, no training
        pars = TestParams("test", "rl", "random", 0.0, (nn, "sigmoid", "SARSA"), None, "random", "random", RL_N_TEST)
        ge = GameEngine(pars, None, None)
        perfs.append(round(100 * ge.test_mode(), 2))

        for i in range(n_train):
            # train
            pars = TrainParams("train", 0.0015, "rl", "rl", 0.1, (nn, "sigmoid", "SARSA"), (nn, "sigmoid", "SARSA"),
                               "random", "random", RL_N_TRAIN)
            ge = GameEngine(pars, None, None)
            ge.train_mode(False)

            # test
            pars = TestParams("test", "rl", "random", 0.0, (nn, "sigmoid", "SARSA"), None, "random", "random",
                              RL_N_TEST)
            ge = GameEngine(pars, None, None)
            perf = round(100 * ge.test_mode(), 2)
            perfs.append(perf)
            out += "Loop {}, score: {}\n".format(i, perf)

        # plot
        print(perfs)
        fig, ax = plt.subplots()
        ax.plot([i for i in range(len(perfs))], perfs, marker='o', label=["RL"])
        ax.set_title(
            "Victory rate of network trained with SARSA algorithm against random agent after several training episodes")
        ax.set_xlabel("Training epochs (e+4)")
        ax.set_ylabel("Victory rate (%)")
        plt.legend()
        plt.savefig(PLOT_NAMES[0])
        #plt.show()
        save_new_ml_agent("rl-complete-run", nn, "sigmoid", "SARSA")

        print(out)

    @staticmethod
    def full_game_ga_perf():
        """
            Test performance of network trained with GA with best values of parameters (determined in previous test)
            over longer training.
        """

        def fitness_eval(network, act_f, ts_p1, ts_p2):
            """
                Fitness function for the GA
            """
            pars = TestParams("test", "ga", "random", 0.0, (network, act_f), None, ts_p1, ts_p2, GA_N_TEST)
            ge = GameEngine(pars)
            ret = ge.test_mode()
            return ret

        out = "\nExperiment: GA training\n\n"
        # Complete game
        out += "GA - Complete game\n"
        t = time.perf_counter()

        perfs = list()

        # train (& test)
        agent = PlayerGA("p1", initialize_nn([66, 77, 1], "normal"), "sigmoid")
        res = agent.evolution(POP_SIZE_FULL_GAME, "normal", [66, 77, 1], 50, 0.2,
                              fitness_eval, ("sigmoid", "random", "random"), comm=perfs)
        perfs.append(res[1])
        print("perfs: ", perfs)
        perfs = [round(100 * p, 2) for p in perfs]
        for i, p in enumerate(perfs):
            out += "Loop {}, score: {}\n".format(i, p)

        print("t: {}".format(time.perf_counter() - t))

        # plot
        fig, ax = plt.subplots()
        ax.plot([i for i in range(len(perfs))], perfs, marker='o', label=["GA"])
        ax.set_title(
            "Victory rate of network trained with Genetic Algorithm against random agent after several training epochs")
        ax.set_xlabel("Generations (e+1)")
        ax.set_ylabel("Victory rate (%)")
        plt.legend()
        plt.savefig(PLOT_NAMES[1])
        save_new_ml_agent("ga-ultimate", res[0], "sigmoid", None)
        #plt.show()

        print(out)

    @staticmethod
    def perf_hybrid_agent():
        """
            Test the performance of the hybrid agent using ml state evaluation and game theory
        """

        print("\nExperiment: performance of hybrid agent\n")


if __name__ == '__main__':

    Experiments.run_all_tests()
