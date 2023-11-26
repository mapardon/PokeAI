import os
from src.db.Storage import Storage

STORAGE_PATH = "stored-networks" if os.name == "posix" else "stored-networks"


# ML agents management


def available_ml_agents() -> list[str]:
    """ Return list of names of stored networks """

    networks = list()
    db = Storage(STORAGE_PATH)
    for k in db.keys():
        networks.append(k)
    return networks


def save_new_rl_agent(network_name: str, network: list, ls: str, act_f: str):
    """ Receive initialized network and identifier in order to store it in the database. Network is stored with
    its strategy and activation function

    :param network_name: Identifier for the network
    :param network: List of numpy arrays (variable lengths for deep learning)
    :param ls: Learning strategy
    :param act_f: Name of activation function used with the network
    """

    db = Storage(STORAGE_PATH)
    db[network_name] = {"network": network, "ls": ls, "act_f": act_f}


def load_rl_agent(network_name: str) -> tuple[list, str, str]:
    """ Retrieve stored weights and associated parameters of RL-trained network"""

    db = Storage(STORAGE_PATH)
    network, ls, act_f = db[network_name]["network"], db[network_name]["ls"], db[network_name]["act_f"]

    return network, ls, act_f


def save_new_ga_agent(network_name: str, network: list, act_f: str):
    """ Receive GA-trained network and identifier in order to store it in the database. Network is stored with
    its activation function

    :param network_name: Identifier for the network
    :param network: List of numpy arrays (variable lengths for deep learning)
    :param act_f: Name of activation function used with the network
    """

    db = Storage(STORAGE_PATH)
    db[network_name] = {"network": network, "act_f": act_f}


def load_ga_agent(network_name: str) -> tuple[list, str, str]:
    """ Retrieve stored weights and associated parameters of GA-trained network """

    db = Storage(STORAGE_PATH)
    network, ls, act_f = db[network_name]["network"], db[network_name]["ls"], db[network_name]["act_f"]

    return network, ls, act_f


def update_ga_agent(network_name: str, network: list | tuple):
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
