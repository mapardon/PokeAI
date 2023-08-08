import os

from src.db.dbmanager import available_ml_agents, available_teams

LS = ["Q-learning",
      "SARSA"]

ACT_F = ["sigmoid",
         "hyperbloic tangent",
         "ReLU"]

INITS = ["normal",
         "xavier",
         "normalized-xavier",
         "He"]

MVSEL = ["eps-greedy",
         "softmax-exp"]

ML_TYPES = ["perceptron"]

AGENTS_TYPE = ["ml", "mdm", "random"]


class TrainMenu:
    def __init__(self, ui_input):
        self.params = ui_input

    def menu_loop(self):
        pars = self.params  # alias
        warning = None
        out = False
        inputted = list()

        while warning is not None or not out:
            os.system("clear" if os.name == "posix" else "cls")
            self.display_parameters()
            self.display_instructions()

            print("Warning : {}".format(warning))
            warning = None  # reset
            inputted = input("selection > ").split(" ")

            # launch something inputs
            if inputted[0] == "leave":
                pars.mode = "leave"
                out = True

            elif inputted[0] == "train":
                if None in [pars.agent1type, pars.agent2type]:
                    warning = "Please specify ai type for both agents"
                elif "ml" not in [pars.agent1type, pars.agent2type]:
                    warning = "Please load at least one ml agent"
                elif pars.agent1type == "ml" and pars.ml1 is None or pars.agent1type == "ml2" and pars.ml2 is None:
                    warning = "Please load ai before launching training"
                else:
                    pars.mode = "train"
                    out = True

            # train settings
            elif inputted[0] in ("ai1", "ai2") and len(inputted) == 2:
                if inputted[1] in AGENTS_TYPE:
                    if inputted[0] == "ai1":
                        pars.agent1type = inputted[1]
                    else:
                        pars.agent2type = inputted[1]
                else:
                    warning = "Unknown agent type"

            elif inputted[0] in ("ml1", "ml2") and len(inputted) == 2:
                if inputted[1] in available_ml_agents():
                    if inputted[0] == "ml1":
                        pars.ml1 = inputted[1]
                    else:
                        pars.ml2 = inputted[1]
                else:
                    warning = "Please provide existing agent name"

            elif inputted[0] == "nb" and len(inputted) == 2:
                try:
                    pars.nb = abs(int(inputted[1]))
                except ValueError:
                    warning = "Please provide consistent value for number of trainings"

            elif inputted[0] == "mvsel" and len(inputted) == 2:
                if inputted[1] in MVSEL:
                    pars.mvsel = inputted[1]
                else:
                    warning = "Unknown move selection method"

            elif inputted[0] in ("lr", "eps") and len(inputted) == 2:  # lr
                try:
                    test = round(float(inputted[1]), 2)
                    if 0 <= test <= 1:
                        if inputted[0] == "lr":
                            pars.lr = test
                        else:
                            pars.eps = test
                    else:
                        raise ValueError
                except ValueError:
                    warning = "Please provide consistent value for lambda/eps parameter"

            elif inputted[0] in ("team1", "team2") and len(inputted) == 2:
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
            "Agent 1 type          : {}".format(pars.agent1type),
            "Agent 2 type          : {}".format(pars.agent2type),
            "ML for agent 1 (train): {}".format(pars.ml1),
            "ML for agent 2 (train): {}".format(pars.ml2),
            "Training rounds       : {}".format(pars.nb),
            "Training move select. : {}".format(pars.mvsel),
            "Training learning rate: {}".format(pars.lr),
            "Training random factor: {}".format(pars.eps),
            "team1                 : {}".format(pars.team1),
            "team2                 : {}".format(pars.team2)]

        print(" * Current parameters:\n")
        for c in contexts:
            print("\t" + c)

    def display_instructions(self):
        instructions = [
            "ai1/2 z    # ai type z for agent 1/2 ({})".format(' - '.join(AGENTS_TYPE)),
            "ml1/2 z    # load ml named z from database for role ai1/2 ({})".format(available_ml_agents()),
            "nb n       # set number of games for training",
            "mvsel z    # move selection method for training ".format(' - '.join(MVSEL)),
            "lr f       # set learning rate to f",
            "eps f      # set epsilon greedy to f",
            "team1/2    # toggle team1/2 type",
            "train      # launch training session",
            "leave      # exit program"]

        print("\n * Settings:\n")
        for i in instructions:
            print("\t" + i)
        print()
