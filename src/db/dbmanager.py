TEAMS_TEMP = {"alpha": [
    (("b", "ground", 80, 80, 125, 80, 125, 80), (("heavy_ground", "ground", 100), ("light_fire", "fire", 50))),
    (("c", "water", 60, 120, 60, 120, 60, 120), (("heavy_water", "water", 100), ("light_psychic", "psychic", 50)))],
              "zeta": [(("y", "electric", 70, 70, 70, 70, 70, 125),
                        (("heavy_electric", "electric", 100), ("light_flying", "flying", 50))),
                       (("z", "fire", 130, 130, 50, 50, 50, 130),
                        (("heavy_fire", "fire", 100), ("light_dragon", "dragon", 50)))]}


# Interface, operations used by rest of the program #


def available_ml_agents():
    # TODO implement
    return ["p", "protocol_1", "protocol_2", "protocol_z"]


def remove_ml_agent(agent_name):
    # TODO implement
    return


def available_teams():
    return TEAMS_TEMP.keys()


def retrieve_team(team_name):
    return TEAMS_TEMP[team_name]

# Internal operations of database management #
