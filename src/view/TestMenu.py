import os

from src.db.dbmanager import available_ml_agents, available_teams
from src.util.UIparameters import TestUIParams

AGENTS_TYPE = ["ml", "minimax", "random"]


class TestMenu:
    def __init__(self, ui_input):
        self.params = ui_input

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

            elif inputted[0] == "test":
                types_specified = None not in [pars.agent1type, pars.agent2type]
                agent1_coherent = pars.ml1 is not None if pars.agent1type == "ml" else True
                agent2_coherent = pars.ml2 is not None if pars.agent2type == "ml" else True
                if not types_specified or not (agent1_coherent and agent2_coherent):
                    warning = "Please first fill all required parameters"

                else:
                    pars.mode = inputted[0]
                    out = True

            # training parameters
            elif inputted[0] in ("agent1", "agent2") and len(inputted) == 2:
                if inputted[1] in AGENTS_TYPE:
                    if inputted[0] == "agent1":
                        pars.agent1type = inputted[1]
                    else:
                        pars.agent2type = inputted[1]
                else:
                    warning = "Please provide an existing type of agent"

            elif inputted[0] == "nb" and len(inputted) == 2:
                try:
                    pars.set_nb(inputted[1])
                except ValueError:
                    warning = "Please provide consistent value for number of trainings"

            elif inputted[0] == "eps" and len(inputted) == 2:
                try:
                    pars.set_eps(inputted[1])
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

            # minimax parameters
            elif inputted[0] in ("minimax1", "minimax2") and len(inputted) == 2:
                try:
                    if inputted[0] == "minimax1":
                        pars.minimax1 = abs(int(inputted[1]))
                    else:
                        pars.minimax2 = abs(int(inputted[1]))
                except ValueError:
                    warning = "Please provide consistent value for minimax depth"

            elif inputted[0] in ("team1", "team2") and len(inputted) == 1:
                if inputted[0] in available_teams() + ["random"]:
                    if inputted[0] == "team1":
                        pars.team1 = inputted[1]
                    else:
                        pars.team2 = inputted[1]
                else:
                    warning = "Unrecognized team"

    def display_parameters(self):
        pars = self.params
        contexts = [
            "agent1 type           : {}".format(pars.agent1type),
            "agent2 type           : {}".format(pars.agent2type),
            "Test rounds           : {}".format(pars.nb),
            "Testing random factor : {}".format(self.params.eps),
            "ML agent 1            : {}".format(pars.ml1),
            "ML agent 2            : {}".format(pars.ml2),  # can be several numbers
            "Minimax agent 1 depth : {}".format(pars.minimax1),
            "Minimax agent 2 depth : {}".format(pars.minimax2),
            "team1                 : {}".format(pars.team1),
            "team2                 : {}".format(pars.team2)]

        print(" * Current parameters:\n")
        for c in contexts:
            print("\t" + c)

    def display_instructions(self):
        instructions = [
            "agent1 t   # type of agent 1 (ml or minimax or ...)",
            "agent2 t   # learning strategy for new agent",
            "nb n       # set number of games for training",
            "eps f      # set epsilon greedy to f",
            "ml1 z      # load AI named z from database for role agent1",
            "ml2 z      # load AI named z from database for role agent2",
            "minimax1 n # move selection method for training",
            "minimax2 n # set learning rate to f",
            "team1/2    # toggle team1/2 type",
            "test       # launch test session",
            "leave      # exit program"]

        print("\n * Settings:\n")
        for i in instructions:
            print("\t" + i)
