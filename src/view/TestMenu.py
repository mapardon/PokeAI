import os

from src.db.dbmanager import available_ml_agents
from src.view.InputFieldsValues import AGENT_TYPES


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
                if inputted[1] in AGENT_TYPES:
                    if inputted[0] == "agent1":
                        pars.agent1type = inputted[1]
                    else:
                        pars.agent2type = inputted[1]
                else:
                    warning = "Please provide an existing type of agent"

                if inputted[0] == "agent1":
                    if inputted[1] == "ga":
                        pars.ml1 = "ga-ultimate"
                    elif inputted[1] == "rl":
                        pars.ml1 = "rl-complete-run"
                    else:
                        pars.ml1 = None
                elif inputted[0] == "agent2":
                    if inputted[1] == "ga":
                        pars.ml2 = "ga-ultimate"
                    elif inputted[1] == "rl":
                        pars.ml2 = "rl-complete-run"
                    else:
                        pars.ml2 = None

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

    def display_parameters(self):
        pars = self.params
        contexts = [
            "agent1 type           : {}".format(pars.agent1type),
            "agent2 type           : {}".format(pars.agent2type),
            "Test rounds           : {}".format(pars.nb),
            "Random move frequency : {}".format(self.params.eps),
            "ML agent 1            : {}".format(pars.ml1),  # can be several numbers
            "ML agent 2            : {}".format(pars.ml2)]

        print(" * Current parameters:\n")
        for c in contexts:
            print("\t" + c)

    def display_instructions(self):
        instructions = [
            "agent1 t   # type of agent 1 {}".format(" - ".join(AGENT_TYPES)),
            "agent2 t   # type of agent 2 {}".format(" - ".join(AGENT_TYPES)),
            "nb n       # set number of games for training",
            "eps f      # random move for epsilon greedy",
            #"ml1 z      # load AI named z from database for agent1({})".format(' - '.join(available_ml_agents())),
            #"ml2 z      # load AI named z from database for agent2({})".format(' - '.join(available_ml_agents())),
            "test       # launch test session",
            "leave      # exit program",
            ""]

        print("\n * Settings:\n")
        for i in instructions:
            print("\t" + i)
