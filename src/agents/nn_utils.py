import numpy as np


# Weights initialization methods #

def init_normal(n_lin: int, n_col: int):
    return np.random.normal(0, 0.0001, (n_lin, n_col))


def init_xavier(n_lin: int, n_col: int):
    return np.random.uniform(-np.sqrt(6 / (n_lin + n_col)), np.sqrt(6 / (n_lin + n_col)), (n_lin, n_col))


def init_normal_xavier(n_lin: int, n_col: int):
    return np.random.normal(0, np.sqrt(2 / (n_lin + n_col)), (n_lin, n_col))


def init_he(n_lin: int, n_col: int):
    return np.random.normal(0, np.sqrt(2 / n_col), (n_lin, n_col))


def initialize_nn(shape: list[int], init_mode: str):
    """
    :param shape: list of integers indicating size of intermediate layers (input and output included)
    :param init_mode: weights initialization algorithm
    :return: tuple of numpy nd-arrays initialized with specified algorithm
    """

    if len(shape) != 3:
        print("NN init may have received incorrect shapes: {}".format(shape))

    weights = list()

    init = {"normal": init_normal,
            "xavier": init_xavier,
            "normalized-xavier": init_normal_xavier,
            "He": init_he}[init_mode]

    for i in range(len(shape) - 2):
        weights.append(init(shape[i+1], shape[i]))
    weights.append(init(shape[-2], shape[-1])[:, 0])  # last layer considered as a vector to speed up computations

    return weights


def init_mutation_nn(shape: list[int], mean: float, std: float):
    """
        Create a neural network with small values, used to represent the mutation of a genetic algorithm.
    """

    weights = list()

    for i in range(len(shape) - 2):
        weights.append(np.random.normal(mean, std, (shape[i+1], shape[i])))
    weights.append(np.random.normal(mean, std, (shape[-2], shape[-1]))[:, 0])

    return weights


# Activation functions #


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def sigmoid_gradient(x):
    return x * (1 - x)


def hyperbolic_tangent(x):
    return np.tanh(x)


def h_tangent_gradient(x):
    return 1 / np.power(np.cosh(x), 2)


def relu(x):
    tmp = np.amax(x)
    return x * (x > 0)


def relu_gradient(x):
    return 1 * (x > 0)
