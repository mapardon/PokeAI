import os

from src.db.dbmanager import available_ml_agents, available_teams
from src.view.util.InputFieldsValues import PLAYER_TYPES


class FightMenu:
    def __init__(self, ui_params):
        self.params = ui_params

    def menu_loop(self):
        pars = self.params  # alias
        warning = None
        out = False

        while warning is not None or not out:
            os.system("clear" if os.name == "posix" else "cls")
            self.display_parameters()
            self.display_instructions()

            print("Warning : {}".format(warning))
            warning = None  # reset
            inputted = input("selection > ").split(" ")

            # launch something
            if inputted[0] == "leave":
                pars.mode = "leave"
                out = True

            elif inputted[0] == "fight":
                types_specified = None not in [pars.player1, pars.player2]
                agent1_coherent = pars.ml1 is not None if pars.player1 == "ml" else True
                agent2_coherent = pars.ml2 is not None if pars.player2 == "ml" else True

                if not types_specified or not (agent1_coherent and agent2_coherent):
                    warning = "Please first fill all required parameters"
                else:
                    pars.mode = "fight"
                    out = True

            # training parameters
            elif inputted[0] in ("player1", "player2") and len(inputted) == 2:
                if inputted[0] == "player2" and inputted[1] == "human":
                    warning = "Player 2 can only be artificial player"
                elif inputted[1] in PLAYER_TYPES:
                    if inputted[0] == "player1":
                        pars.agent1type = inputted[1]
                    else:
                        pars.agent2type = inputted[1]
                else:
                    warning = "Please provide an existing type of agent"

            elif inputted[0] == "eps" and len(inputted) == 2:
                try:
                    test = round(float(inputted[1]), 2)
                    if 0 <= test <= 1:
                        pars.eps = test
                    else:
                        raise ValueError
                except ValueError:
                    warning = "Please provide consistent value for lambda/eps parameter"

            # ml agents parameters
            elif inputted[0] in ("ml1", "ml2") and len(inputted) == 2:
                if inputted[1] in available_ml_agents():
                    if inputted[0] == "ml1":
                        pars.ml1 = inputted[1]
                    else:
                        pars.ml2 = inputted[1]
                else:
                    warning = "Please provide existing agent name"

            elif inputted[0] in ("team1", "team2") and len(inputted) == 2:
                if inputted[1] in available_teams() + ["random"]:
                    if inputted[0] == "team1":
                        pars.team1 = inputted[1]
                    else:
                        pars.team2 = inputted[1]
                else:
                    warning = "Unrecognized team"

    def display_parameters(self):
        pars = self.params
        contexts = [
            "player1 type          : {}".format(pars.agent1type),
            "player2 type          : {}".format(pars.agent2type),
            "Testing random factor : {}".format(self.params.eps),
            "ML player 1           : {}".format(pars.ml1),
            "ML player 2           : {}".format(pars.ml2),
            "team1                 : {}".format(pars.team1),
            "team2                 : {}".format(pars.team2)
        ]

        print(" * Current parameters:\n")
        for c in contexts:
            print("\t" + c)

    def display_instructions(self):
        instructions = [
            "player1 t  # type of agent for player 1 {}".format(' - '.join(PLAYER_TYPES)),
            "player2 t  # type of agent for player 2 {}".format(' - '.join(PLAYER_TYPES[1:])),
            "eps f      # set epsilon greedy to f",
            "ml1 z      # load AI named z from database for agent1",
            "ml2 z      # load AI named z from database for agent2",
            "team1/2 t  # give team t to player1/2",
            "fight      # launch match",
            "leave      # exit program"]

        print("\n * Settings:\n")
        for i in instructions:
            print("\t" + i)
