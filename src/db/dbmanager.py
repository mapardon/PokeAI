import numpy as np

from src.db.Storage import Storage

STORAGE_PATH = "db/stored-networks"


# ML agents management


def available_ml_agents() -> list[str]:
    """ Return list of names of stored networks """

    networks = list()
    db = Storage(STORAGE_PATH)
    for k in db.keys():
        networks.append(k)
    return networks


def save_new_ml_agent(network_name: str, network: list[np.array], act_f: str, ls: str | None = None) -> None:
    """ Receive initialized network and identifier in order to store it in the database. Network is stored with
    its strategy and activation function. Learning strategy is only required for Rl agent.

    :param network_name: Identifier for the network
    :param network: List of numpy arrays (variable lengths for deep learning)
    :param act_f: Name of activation function used with the network
    :param ls: Learning strategy
    """

    db = Storage(STORAGE_PATH)
    db[network_name] = {"network": network, "act_f": act_f, "ls": ls}


def load_ml_agent(network_name: str) -> tuple[list[np.array], str, str | None]:
    """
        Retrieve stored weights and associated parameters. Learning strategy can be None for agents not requiring it.
    """

    db = Storage(STORAGE_PATH)
    network, act_f, ls = db[network_name]["network"], db[network_name]["act_f"], db[network_name]["ls"]

    return network, act_f, ls


def update_ml_agent(network_name: str, network: list[np.array]) -> None:
    """ Update weight matrices of a stored network

    :param network_name: Identifier for the network, identifying key inside the storage
    :param network: List of arrays of the new network """

    db = Storage(STORAGE_PATH)
    agent = db[network_name]
    agent["network"] = network
    db[network_name] = agent


def remove_ml_agent(network_name: str):
    """ Delete specified agent from the database """

    db = Storage(STORAGE_PATH)
    if network_name in db:
        del db[network_name]
