import numpy as np
from src.game.GameEngine import NB_MOVES, NB_POKEMON

N_INPUT = (2 * NB_MOVES * NB_POKEMON + 6 * NB_POKEMON) * 2
N_OUT = 1


def init_normal(layer_prev, layer_next):
    return np.random.normal(0, 0.0001, (layer_next, layer_prev))


def init_xavier(layer_prev, layer_next):
    return np.random.uniform(-np.sqrt(6 / (layer_prev + layer_next)), np.sqrt(6 / (layer_prev + layer_next)), (layer_next, layer_prev))


def init_normal_xavier(layer_prev, layer_next):
    return np.random.normal(0, np.sqrt(2 / (layer_prev + layer_next)), (layer_next, layer_prev))


def init_he(layer_prev, layer_next):
    return np.random.normal(0, np.sqrt(2 / layer_prev), (layer_next, layer_prev))


def initialize_NN(shape, init_mode):
    """
    :param shape: list of integers indicating size of intermediate layers (input and output excluded)
    :param init_mode: weights initialization algorithm
    :return: tuple of numpy nd-arrays initialized with specified algorithm
    """

    if shape[0] != N_INPUT:
        shape = [N_INPUT] + shape

    if shape[-1] != N_OUT:
        shape = shape + [N_OUT]

    if len(shape) != 3:
        print("NN init may have received incorrect shapes: {}".format(shape))

    weights = list()

    init = {"normal": init_normal,
            "xavier": init_xavier,
            "normalized-xavier": init_normal_xavier,
            "He": init_he}[init_mode]

    for i in range(len(shape) - 2):
        weights.append(init(shape[i], shape[i+1]))
    weights.append(init(shape[-1], shape[-2])[:, 0])  # last layer considered as a vector to speed up computations

    return weights
