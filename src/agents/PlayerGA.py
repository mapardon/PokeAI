import random
from typing import Callable, Any

import numpy as np
from line_profiler import profile

from src.agents.PlayerNN import PlayerNN
from src.game.PokeGame import PokeGame
from src.agents.nn_utils import initialize_nn, init_mutation_nn


class PlayerGA(PlayerNN):
    def __init__(self, role, network: tuple[np.array] | list[np.array], act_f: str):
        super().__init__(role, network, act_f)

    # Communication with game loop #

    def make_move(self, game: PokeGame):
        return super().move_selector(game)

    # Learning algorithms #

    @staticmethod
    def evolution(pop_size: int, init_mode: str, net_shape: list[int], n_gen: int, elite_prop: float,
                  stop_criterion: float, fitness_f: Callable, fitness_f_args: tuple, display: bool = False) -> tuple[list[np.array], float]:
        """
            Train the neural network with a genetic algorithm

            :param pop_size: Size of the population
            :param init_mode: Algorithm for individuals initialization
            :param net_shape: Size of the network layers
            :param n_gen: Number of generations for the training loop
            :param elite_prop: Proportion of the population considered as best performing
            :param stop_criterion: Victory rate of a testing phase (compared with the value returned by fitness_f)
            :param fitness_f: Function running a bunch of matches where one of the player is the currently trained
                PlayerGA and returning the victory rate of it
            :param fitness_f_args: Parameters for the fitness function
            :param display: Print progression
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

            population = sorted(population, key=lambda x: x[1], reverse=True)[:round(len(population) * elite_prop)]
            if not c % max((n_gen // 10), 1) and display:
                print("gen {}, score: {}".format(c, population[0][1]))

            # mutation
            softmax_vals = [np.exp(ind1[1]) / sum([np.exp(ind2[1]) for ind2 in population]) for ind1 in population]
            for indiv in random.choices(population[:round(pop_size * elite_prop)], softmax_vals):
                new = list()
                for l1, l2 in zip([np.copy(indiv[0][0]), np.copy(indiv[0][1])], init_mutation_nn(net_shape, 0, 0.00001)):
                    new.append(l1 + l2)
                population.append([new, -1])

            c += 1

        return population[0]
