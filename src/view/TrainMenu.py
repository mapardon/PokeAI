import os

from src.db.dbmanager import available_ml_agents, available_teams

LS = ["Q-learning",
      "TD-lambda"]

ACT_F = ["sigmoid",
         "ReLU"]

INITS = ["normal",
         "xavier",
         "normalized-xavier",
         "He"]

MVSEL = ["eps-greedy",
         "softmax-exp"]

ML_TYPES = ["perceptron"]


class TrainMenu:
    def __init__(self, ui_input):
        self.params = ui_input

    def menu_loop(self):
        pars = self.params  # alias
        warning = None
        out = False
        inputted = ["Be Stronger"]

        # TODO delete
        pars.newfname = "test-gene"
        pars.newmltype = "perceptron"
        pars.newls = "TD-lambda"
        pars.newshape = ["20"]
        pars.newinit = "normal"
        pars.newactf = "sigmoid"
        pars.newlamb = 0.5
        #############

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

            elif inputted[0] == "create":
                if None in [pars.newfname, pars.newmltype, pars.newls, pars.newshape, pars.newinit, pars.newactf,
                            pars.newlamb]:
                    warning = "Please first fill all required parameters"

                else:
                    pars.mode = "create"
                    out = True

            elif inputted[0] == "train":
                if pars.ml1 is None:
                    warning = "Must at least load one AI"
                else:
                    pars.mode = "train"
                    out = True

            # new agents parameters
            elif inputted[0] == "new-name" and len(inputted) == 2:
                if inputted[0] not in available_ml_agents():
                    pars.newfname = inputted[1]
                else:
                    warning = "This name is already used in the database"

            elif inputted[0] == "new-type" and len(inputted) == 2:
                if inputted[1] in ML_TYPES:
                    pars.newmltype = inputted[1]
                else:
                    warning = "Unknown machine learning type"

            elif inputted[0] == "new-ls" and len(inputted) == 2:
                if inputted[1] in LS:
                    pars.newls = inputted[1]
                else:
                    warning = "Unknown learning strategy"

            elif inputted[0] == "new-shape" and len(inputted) > 1:
                try:
                    pars.newshape = list()
                    for s in inputted[1:]:
                        pars.newshape.append(abs(int(s)))
                except ValueError:
                    warning = "Please provide consistent value for number of neurons"

            elif inputted[0] == "new-init" and len(inputted) == 2:
                if inputted[1] not in INITS:
                    print("Unknown initialization mode")
                else:
                    pars.newinit = inputted[1]

            elif inputted[0] == "new-actf" and len(inputted) == 2:
                if inputted[1] not in ACT_F:
                    print("Unknown activation function")
                else:
                    pars.newactf = inputted[1]

            elif inputted[0] == "new-lamb" and len(inputted) == 2:
                try:
                    test = round(float(inputted[1]), 2)
                    if 0 <= test <= 1:
                        pars.newlamb = test
                    else:
                        raise ValueError
                except ValueError:
                    warning = "Please provide consistent value for lambda parameter"

            # train settings
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
            "New AI filename       : {}".format(pars.newfname),
            "New agent type        : {}".format(pars.newmltype),
            "New AI learning strat : {}".format(pars.newls),
            "New AI shape          : {}".format(pars.newshape),  # can be several numbers
            "New AI init method    : {}".format(pars.newinit),
            "New AI activation fun : {}".format(pars.newactf),
            "New AI lambda param.  : {}".format(pars.newlamb),
            "",
            "Training first AI     : {}".format(pars.ml1),
            "Training second AI    : {}".format(pars.ml2),
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
            "new-name z # new agent will be identified z",
            "new-type z # type of ml for new agent ({})".format(' - '.join(ML_TYPES)),
            "new-ls z   # learning strategy for new agent ({})".format(' - '.join(LS)),
            "new-shape m n ... z",
            "           # dimensions for new NN",
            "new-init z # network initialization method ({})".format(' - '.join(INITS)),
            "new-actf z # network activation function ({})".format(' - '.join(ACT_F)),
            "new-lamb f # set lambda value for TD-lambda",
            "create     # create new agent with specified params",
            "",
            "ai1 z      # load AI named z from database for role ai1",
            "ai2 z      # load AI named z from database for role ai2",
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
