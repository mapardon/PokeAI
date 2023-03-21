import os
from src.db.Storage import Storage

STORAGE_PATH = "db/stored-networks"


# ML agents management


def available_ml_agents():
    """ Return list of names of stored networks """

    networks = list()
    db = Storage(STORAGE_PATH)
    for k in db.keys():
        networks.append(k)
    return networks


def update_ml_agent(network_name, network):
    """ Update weight matrices of a stored network (after training)

    :param network_name: name of the network, identifying key inside the storage
    :param network: tuple of ndarrays of the new network """

    db = Storage(STORAGE_PATH)
    agent = db[network_name]
    agent["network"] = network
    db[network_name] = agent


def save_new_agent(network_name, network, ls, lamb, act_f):
    """ Receive initialized network and identifier in order to store it in the database. Network is stored with
    its strategy, activation function and lambda parameter

    :param network: list of numpy arrays (variable lengths for deep learning)
    """
    print(os.getcwd())

    db = Storage(STORAGE_PATH)
    db[network_name] = {"network": network, "ls": ls, "lamb": lamb, "act_f": act_f}


def load_ml_agent(network_name):
    """ Retrieve stored weights and associated parameters """

    db = Storage(STORAGE_PATH)
    network, ls, lamb, act_f = db[network_name]["network"], db[network_name]["ls"], db[network_name]["lamb"], \
        db[network_name]["act_f"]

    return network, ls, lamb, act_f


def remove_ml_agent(network_name):
    db = Storage(STORAGE_PATH)
    del db[network_name]


# pokemon teams management

TEAMS_TEMP = {"alpha": [
    (("b", "ground", 80, 80, 125, 80, 125, 80), (("heavy_ground", "ground", 100), ("light_fire", "fire", 50))),
    (("c", "water", 60, 120, 60, 120, 60, 120), (("heavy_water", "water", 100), ("light_psychic", "psychic", 50)))],
    "zeta": [(("y", "electric", 70, 70, 70, 70, 70, 125),
              (("heavy_electric", "electric", 100), ("light_flying", "flying", 50))),
             (("z", "fire", 130, 130, 50, 50, 50, 130),
              (("heavy_fire", "fire", 100), ("light_dragon", "dragon", 50)))]}


def available_teams():
    return TEAMS_TEMP.keys()


def retrieve_team(team_name):
    return TEAMS_TEMP[team_name]
