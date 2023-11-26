import os, sys
import threading

sys.path.append(
    '/home/mathieu/PycharmProjects/PokeAI' if os.name == 'posix' else 'C:\\Users\\mathi\\PycharmProjects\\PokeAI')

from src.agents.nn_utils import initialize_nn
from src.agents.PlayerRL import PlayerRL
from src.agents.PlayerGA import PlayerGA
from src.game.GameEngine import GameEngine
from src.game.GameEstimation import fill_game_with_estimation
from src.experiments.AltImplementations import GameEngineAlt, PokeGameAlt1, PokeGameAlt2, TestUIParamsAlt
from src.game.PokeGame import PokeGame
from src.view.util.UIparameters import TestUIParams, TrainUIParams

SHORT = True
if SHORT:
    # Run tests with small repetitions to check if everything goes right
    GT_STATE_EVAL = 10
    ML_TRAIN_LOOPS = 1
    RL_N_TRAIN = 10
    RL_N_TEST = 10
    GA_N_TEST = 10
    GA_POP_SIZE = 2
    GA_N_GEN = 2
    GA_STATE_VEC_TEST = 10
    GA_STATE_VEC_LOOPS = 1
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


class Experiments:
    """
        Implements experiments made to evaluate optimal values of hyperparameters of different models developed in the
        project
    """

    @staticmethod
    def run_all_tests():
        Experiments.weights_for_gt_state_eval()
        Experiments.training_rl_agent()
        Experiments.training_ga_agent()
        Experiments.state_vector_for_ga()
        Experiments.training_params_for_ga()

    @staticmethod
    def weights_for_gt_state_eval():
        """
            Test performance of PlayerGT agent with different weights for the parameters of payoff computation
        """
        print("\nExperiment: weights for GT\n")

        def tune_weights(test_weights):
            best_res = None
            for weights in test_weights:
                uip = TestUIParamsAlt("test", "gt", "random", 0.1, None, None, "random", "random", GT_STATE_EVAL, weights)
                ge = GameEngine(uip)

                res = ge.test_mode(uip, None)
                print("Config: {}, res={}%".format(weights, 100 * res))

        test_weights = [(i, j, k, l) for i in range(2) for j in range(2) for k in range(2) for l in range(2)] + \
            [(i, j, k, l) for i in [2, 5] for j in [2, 5] for k in [2, 5] for l in [2, 5]]

        l = len(test_weights)
        t1 = threading.Thread(target=tune_weights, args=(test_weights[:l // 4],))
        t2 = threading.Thread(target=tune_weights, args=(test_weights[l // 4:l // 2],))
        t3 = threading.Thread(target=tune_weights, args=(test_weights[l // 2:3 * l // 4],))
        t4 = threading.Thread(target=tune_weights, args=(test_weights[3 * l // 4:],))

        for t in [t1, t2, t3, t4]:
            t.start()

        for t in [t1, t2, t3, t4]:
            t.join()

    @staticmethod
    def agent_estimations(ts, agent):
        """
            See the estimation that an agent using a neural network makes for its possible choices
        """

        out = str()
        g = PokeGame(ts)
        fill_game_with_estimation("p1", g)
        for m in g.get_moves_from_state("p1", state=g.game_state):
            for n in g.get_moves_from_state("p2", state=g.game_state):
                s = g.apply_player_moves(g.get_cur_state(), m, n)
                out += "{} - {}: {}\n".format(m, n, round(agent.forward_pass(g.get_numeric_repr(s, "p1")), 5))
        print(out)

    @staticmethod
    def training_rl_agent():
        """
            Test the performance of an agent using a neural network trained with gradient descent
        """
        print("\nExperiment: RL training\n")

        # First, test with a simplified game (1 vs 1 w/ 2 attacks, one attack has no effect, which should be noticed
        # by the agent). The team compositions never change so the agent must not deal with generalization
        ts_1 = [[(("p1", "POISON", 500, 100, 100, 101),
                  (("light_poison", "POISON", 50), ("light_fighting", "FIGHTING", 50)))],
                [(("d1", "STEEL", 500, 100, 100, 100),
                  (("light_steel", "STEEL", 50), ("light_bug", "BUG", 50)))]]

        print("Simple game")
        for i in range(ML_TRAIN_LOOPS):
            nn = initialize_nn([18, 60, 1], "xavier")

            # train
            uip = TrainUIParams("train", 0.0015, "rl", "rl", 0.1, (nn, "SARSA", "sigmoid"), (nn, "SARSA", "sigmoid"), ts_1[0], ts_1[1], RL_N_TRAIN)
            ge = GameEngine(uip)
            ge.train_mode(uip, None)

            # test
            uip = TestUIParams("test", "rl", "random", 0.1, (nn, "SARSA", "sigmoid"), None, ts_1[0], ts_1[1], RL_N_TEST)
            ge = GameEngine(uip, None, None)
            print("Loop {}, score: {}".format(i, ge.test_mode(uip)))
            Experiments.agent_estimations(ts_1, PlayerRL("p1", "test", nn, "SARSA", "sigmoid", 0.0, 0.0))

        # Slightly more complicated game
        ts_2 = [[(("p1", "FIRE", 200, 100, 100, 100),
                  (("heavy_fire", "FIRE", 100), ("light_steel", "STEEL", 100))),
                 (("p2", "GRASS", 200, 100, 100, 100),
                  (("heavy_grass", "GRASS", 100), ("light_electric", "ELECTRIC", 100)))],
                [(("d1", "WATER", 200, 100, 100, 100),
                  (("heavy_water", "WATER", 100), ("light_ground", "GROUND", 100))),
                 (("d2", "BUG", 200, 80, 100, 100),
                  (("heavy_bug", "BUG", 100), ("light_fire", "FIRE", 100)))]]

    @staticmethod
    def training_ga_agent():
        """
            Test the performance of an agent using a neural network trained with a genetic algorithm
        """
        print("\nExperiment: GA training\n")

        def fitness_eval(network, act_f, ts_p1, ts_p2):
            """
                Fitness function for the GA
            """
            uip = TestUIParams("test", "ga", "random", 0.0, (network, act_f), None, ts_p1, ts_p2, GA_N_TEST)
            ge = GameEngine(uip)
            ret = ge.test_mode(uip, None)
            return ret

        # First, test with a simplified game (1 vs 1 w/ 2 attacks, one attack has no effect, which should be noticed
        # by the agent). The team compositions never change so the agent must not deal with generalization
        ts_1 = [[(("p1", "POISON", 500, 100, 100, 101),
                  (("light_poison", "POISON", 50), ("light_fighting", "FIGHTING", 50)))],
                [(("d1", "STEEL", 500, 100, 100, 100),
                  (("light_steel", "STEEL", 50), ("light_bug", "BUG", 50)))]]

        print("Simple game")
        for i in range(ML_TRAIN_LOOPS):
            # train (& test)
            res = PlayerGA.evolution(GA_POP_SIZE, "xavier", [18, 60, 1], GA_N_GEN, 1 / 3, 0.0, fitness_eval, ("sigmoid", ts_1[0], ts_1[1]))
            print("Loop {}, score: {}".format(i, res[1]))
            Experiments.agent_estimations(ts_1, PlayerGA("p1", res[0], "sigmoid"))

        # Slightly more complicated game
        ts_2 = [[(("p1", "FIRE", 200, 100, 100, 100),
                  (("heavy_fire", "FIRE", 100), ("light_steel", "STEEL", 100))),
                 (("p2", "GRASS", 200, 100, 100, 100),
                  (("heavy_grass", "GRASS", 100), ("light_electric", "ELECTRIC", 100)))],
                [(("d1", "WATER", 200, 100, 100, 100),
                  (("heavy_water", "WATER", 100), ("light_ground", "GROUND", 100))),
                 (("d2", "BUG", 200, 80, 100, 100),
                  (("heavy_bug", "BUG", 100), ("light_fire", "FIRE", 100)))]]

    @staticmethod
    def state_vector_for_ga():
        """
            Test performance of neural networks using different numeric representation of the game while training with
            the genetic algorithm (10 generations of populations of 10 individuals). NB: complete run takes quite a
            long time.
        """

        class FitnessEval:
            def __init__(self, poke_game_type):
                self.poke_game_type = poke_game_type

            def __call__(self, nn):
                uip = TestUIParams("test", "ga", "random", 0.1, (nn, "sigmoid"), None, "random", "random", GA_STATE_VEC_TEST)
                ge = GameEngineAlt(uip, self.poke_game_type)
                ret = ge.test_mode(uip, None)
                return ret

        print("\nExperiment: state vector for GA\n")

        for s, pg_type, dims in (("Regular PokeGame", PokeGame, [66, 75, 1]), ("Full ohe", PokeGameAlt1, [678, 338, 1]), ("Types ohe", PokeGameAlt2, [492, 246, 1])):
            fitness_eval = FitnessEval(pg_type)
            print(s)
            for _ in range(GA_STATE_VEC_LOOPS):
                res = PlayerGA.evolution(GA_POP_SIZE, "xavier", dims, GA_N_GEN, 1 / 3, 0.0, fitness_eval, tuple())
                print(res[1])

    @staticmethod
    def training_params_for_ga():
        """

        """


if __name__ == '__main__':

    Experiments.state_vector_for_ga()
