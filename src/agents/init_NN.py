import numpy as np

N_INPUT = 5
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
²   :param shape: list of integers indicating size of intermediate layers (input and output excluded) """

    shape = [N_INPUT] + shape + [N_OUT]
    weights = list()

    init = {"normal": init_normal,
            "xavier": init_xavier,
            "normalized-xavier": init_normal_xavier,
            "He": init_he}[init_mode]

    for i in range(len(shape) - 2):
        weights.append(init(shape[i], shape[i+1]))
    weights.append(init(shape[-1], shape[-2])[:, 0])  # last layer considered as a vector to speed up computations

    return weights
