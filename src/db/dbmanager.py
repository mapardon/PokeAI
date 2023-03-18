import os
import shelve


STORAGE = "./src/db/stored-networks" if os.name == "posix" else ".\\src\\db\\stored-networks"


# ML agents management


def available_ml_agents():
    """ Return list of names of stored networks """

    networks = list()
    with shelve.open(STORAGE) as db:
        for k in db.keys():
            networks.append(k)

    return networks


def update_ml_agent(network_name, network):
    """ Update weight matrices of a stored network (after training)

    :param network_name: name of the network, identifying key inside the shelve
    :param network: tuple of 2 or 3 matrices representing weights of the network """

    with shelve.open(STORAGE, writeback=True) as db:
        db[network_name]["network"] = network


def save_new_agent(network_name, ls, act_f, network, lamb):
    """ Receive initialized network and identifier in order to store it in the database. Network is stored with
    its strategy, activation function and lambda parameter

    :param network: tuple of numpy arrays (variable lengths for deep learning)
    """

    with shelve.open(STORAGE, writeback=True) as db:
        db[network_name] = dict()
        db[network_name]["ls"], db[network_name]["act_f"], db[network_name]["network"], \
            db[network_name]["lamb"] = ls, act_f, network, lamb


def load_ml_agent(network_name):
    """ Retrieve stored weights and associated parameters """

    with shelve.open(STORAGE, writeback=True) as db:
        ls, act_f, network, lamb = db[network_name]["ls"], db[network_name]["act_f"], db[network_name]["network"], \
                                   db[network_name]["lamb"]

    return ls, act_f, network, lamb


def remove_ml_agent(network_name):
    with shelve.open(STORAGE, writeback=True) as db:
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
