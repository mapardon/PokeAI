import random
from typing import Callable

import numpy as np

from src.agents.PlayerNN import PlayerNN
from src.game.PokeGame import PokeGame
from src.agents.nn_utils import initialize_nn, init_mutation_nn


class PlayerGA(PlayerNN):
    def __init__(self, role, network: tuple[np.array] | list[np.array], act_f: str):
        super().__init__(role, network, act_f)

    # Communication with game loop #

    def make_move(self, game: PokeGame):
        """
            This method performs the same actions as its mother's, but for the sake of clarity in certain situations
            (e.g., comparison of the performance of this agent against other neural networks-based agents) a version of
            this method is kept in this class.
        """
        return super().make_move(game)

    # Learning algorithms #

    def evolution(self, pop_size: int, init_mode: str, net_shape: list[int], n_gen: int, elite_prop: float,
                  fitness_f: Callable, fitness_f_args: tuple, mu_mean: float = 0, mu_std: float = 0.00001,
                  display: bool = False, comm: list = None) -> list[list[np.array], float]:
        """
            Train the neural network with a genetic algorithm

            :param pop_size: Size of the population
            :param init_mode: Algorithm for individuals initialization
            :param net_shape: Size of the network layers
            :param n_gen: Number of generations for the training loop
            :param elite_prop: Proportion of the population considered as best performing
            :param fitness_f: Function running a bunch of matches where one of the player is the currently trained
                PlayerGA and returning the victory rate of it
            :param fitness_f_args: Parameters for the fitness function
            :param mu_mean: Mean of normal random distribution used for mutation term
            :param mu_std: Standard deviation of normal random distribution used for mutation term
            :param display: Display of progression
            :param comm: If provided, store intermediary results every 10 generations
            :return: Network having achieved the best performance on the fitness function during the training and the
                performance
        """

        # init population
        population = list()
        for _ in range(pop_size):
            population.append([initialize_nn(net_shape, init_mode), -1.0])

        # evolution phase
        c = int()
        while c < n_gen:
            # fitness computation and selection
            for indiv in population:
                if indiv[-1] < 0:
                    indiv[1] = fitness_f(indiv[0], *fitness_f_args)

            elite_idx = max(round(len(population) * elite_prop), 1)
            population = sorted(population, key=lambda x: x[1], reverse=True)[:elite_idx]
            if not c % max((n_gen // 10), 1) and display:
                print("gen {}, score: {}".format(c, population[0][1]))

            # store intermediary results
            if isinstance(comm, list) and not c % 10:
                comm.append(population[0][1])

            # mutation
            softmax_vals = [np.exp(ind1[1]) / sum([np.exp(ind2[1]) for ind2 in population]) for ind1 in population]
            for indiv in random.choices(population[:elite_idx], softmax_vals, k=(pop_size - elite_idx)):
                new = list()
                for l1, l2 in zip([np.copy(indiv[0][0]), np.copy(indiv[0][1])], init_mutation_nn(net_shape, mu_mean, mu_std)):
                    new.append(l1 + l2)
                population.append([new, -1])
            c += 1

        self.network = population[0][0]
        return population[0]
