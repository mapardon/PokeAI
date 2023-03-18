import numpy as np

N_INPUT = 128
N_OUT = 1


def initialize_NNx(shape, init_mode):
    """
²   :param shape: list of integers indicating size of intermediate layers """

    shape = [N_INPUT] + shape + [N_OUT]
    weights = list()

    if init_mode == "normal":
        for i in range(len(shape) - 1):
            weights.append(np.random.normal(0, 0.0001, (n_hidden, N_INPUT)))

    elif init_mode == "xavier":
        pass

    elif init_mode == "normalized xavier":
        pass

    elif init_mode == "He":
        pass

    return weights

def initialize_NN(n_hidden, init_mode):
    """ NB: w_out is considered as a vector and not input_size x 1 matrix to simplify some notations """

    if init_mode == "normal":
        w_int = np.random.normal(0, 0.0001, (n_hidden, N_INPUT))
        w_out = np.random.normal(0, 0.0001, (n_hidden, 1))[:, 0]

    elif init_mode == "xavier":
        w_int = np.random.uniform(-np.sqrt(6 / (N_INPUT + n_hidden)), np.sqrt(6 / (N_INPUT + n_hidden)), (n_hidden, N_INPUT))
        w_out = np.random.uniform(-np.sqrt(6 / (n_hidden + 1)), np.sqrt(6 / (n_hidden + 1)), (n_hidden, 1))[:, 0]

    elif init_mode == "normalized xavier":
        w_int = np.random.normal(0, np.sqrt(2 / (N_INPUT + n_hidden)), (N_INPUT, n_hidden))
        w_out = np.random.normal(0, np.sqrt(2 / (n_hidden + 1)), (n_hidden, 1))

    elif init_mode == "He":
        w_int = np.random.normal(0, np.sqrt(2/N_INPUT), (n_hidden, N_INPUT))
        w_out = np.random.normal(0, np.sqrt(2/n_hidden), (n_hidden, 1))[:, 0]

    return w_int, w_out


def initialize_DN(n_hidden1, n_hidden2, init_mode):

    if init_mode == "normal":
        w_1 = np.random.normal(0, 0.0001, (n_hidden1, N_INPUT))
        w_2 = np.random.normal(0, 0.0001, (n_hidden2, n_hidden1))
        w_out = np.random.normal(0, 0.0001, (n_hidden2, 1))[:, 0]

    elif init_mode == "xavier":
        w_1 = np.random.uniform(-1/np.sqrt(N_INPUT), 1/np.sqrt(N_INPUT), (n_hidden1, N_INPUT))
        w_2 = np.random.uniform(-1/np.sqrt(n_hidden1), 1/np.sqrt(n_hidden1), (n_hidden2, n_hidden1))
        w_out = np.random.uniform(-1/np.sqrt(n_hidden2), 1/np.sqrt(n_hidden2), (n_hidden2, 1))[:, 0]

    elif init_mode == "He":
        w_1 = np.random.normal(0, np.sqrt(2/N_INPUT), (n_hidden1, N_INPUT))
        w_2 = np.random.normal(0, np.sqrt(2/n_hidden1), (n_hidden2, n_hidden1))
        w_out = np.random.normal(0, np.sqrt(2/n_hidden2), (n_hidden2, 1))[:, 0]

    return w_1, w_2, w_out
