import os

from src.agents.init_NN import initialize_nn
from src.db.dbmanager import available_ml_agents, remove_ml_agent, save_new_agent
from src.view.util.UIparameters import ManageUIParams

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

AGENTS_TYPE = ["ml"]


class ManageController:
    def __init__(self):

        self.ui_input = ManageUIParams()
        self.menu_phase()

    def menu_phase(self):
        ui_input = self.ui_input

        while ui_input.mode != "leave":

            self.menu_loop()

            if ui_input.mode == "leave":
                break

            elif ui_input.mode == "create":
                self.create_ai()

    def create_ai(self):
        uip = self.ui_input
        network = initialize_nn(self.ui_input.newshape, self.ui_input.newinit)
        input("creating new agent: {}, {}, {}, {}, {}, {}".format(self.ui_input.newfname, self.ui_input.newshape,
                                                                  self.ui_input.newls, self.ui_input.newlamb,
                                                                  self.ui_input.newactf, self.ui_input.newinit))
        save_new_agent(uip.newfname, network, uip.newls, uip.newlamb, uip.newactf)

        # reset input params
        uip = self.ui_input
        uip.newfname = uip.newls = uip.newactf = uip.newlamb = uip.newinit = uip.newshape = uip.newmltype = None

    def menu_loop(self):
        pars = self.ui_input
        warning = None
        out = None
        inputted = list()

        while warning is not None or out is None:
            os.system("clear" if os.name == "posix" else "cls")
            self.display_parameters()
            self.display_instructions(available_ml_agents())

            print("Warning : {}".format(warning))
            warning = None  # reset
            inputted = input("selection > ").split(" ")

            if inputted[0] == "leave":
                pars.mode = "leave"
                out = True

            # new agents parameters
            elif inputted[0] == "new-name" and len(inputted) == 2:
                if inputted[0] not in available_ml_agents():
                    pars.newfname = inputted[1]
                else:
                    warning = "This name is already used in the database"

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

            elif inputted[0] == "create":
                if None in [pars.newfname, pars.newls, pars.newshape, pars.newinit, pars.newactf] + [pars.newlamb] * ("lambda" in pars.newls):
                    warning = "Please first fill all required parameters"

                else:
                    pars.mode = "create"
                    out = True

            elif inputted[0] == "delete" and len(inputted) == 2:
                if inputted[1] not in available_ml_agents():
                    warning = "Agent not found"
                else:
                    remove_ml_agent(inputted[1])

    def display_parameters(self):
        pars = self.ui_input
        contexts = [
            "New AI filename       : {}".format(pars.newfname),
            "New AI learning strat : {}".format(pars.newls),
            "New AI shape          : {}".format(pars.newshape),  # can be several numbers
            "New AI init method    : {}".format(pars.newinit),
            "New AI activation fun : {}".format(pars.newactf),
            "New AI lambda param.  : {}".format(pars.newlamb)]

        print(" * Current parameters:\n")
        for c in contexts:
            print("\t" + c)

    def display_instructions(self, agents):
        instructions = [
            "new-name z # new agent will be identified z",
            "new-ls z   # learning strategy for new agent ({})".format(' - '.join(LS)),
            "new-shape m n ... z",
            "           # dimensions for new NN",
            "new-init z # network initialization method ({})".format(' - '.join(INITS)),
            "new-actf z # network activation function ({})".format(' - '.join(ACT_F)),
            "new-lamb f # set lambda value for TD-lambda",
            "create     # create new agent with specified params",
            "delete z   # remove agent z from database"
        ]

        print("\n * Settings:\n")
        for i in instructions:
            print("\t" + i)
        print()

        print("\n * Available agents:")
        for i in agents:
            print("\t - " + i)
        print()


if __name__ == '__main__':
    ManageController()
