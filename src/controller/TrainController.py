import sys

from src.agents.init_NN import initialize_NN
from src.db.dbmanager import save_new_agent
from src.view.util.UIparameters import TrainUIParams

sys.path.append('/home/mathieu/PycharmProjects/PokeAI')

import os
from math import ceil
from threading import Thread

from src.game.GameEngine import GameEngine
from src.view.TrainMenu import TrainMenu


class TrainController:
    """ Training and creating agents """

    def __init__(self):

        self.ui_input = TrainUIParams()
        self.menu = TrainMenu(self.ui_input)
        self.menu_phase()

    def menu_phase(self):
        """ Select parameters for training """
        ui_input = self.ui_input

        while ui_input.mode != "leave":

            self.menu.menu_loop()

            if ui_input.mode == "leave":
                break

            elif ui_input.mode == "create":
                self.create_ai()

            elif ui_input.mode == "train":
                self.train_phase()

    def create_ai(self):
        uip = self.ui_input
        network = initialize_NN(self.ui_input.newshape, self.ui_input.newinit)
        input("creating new agent: {}, {}, {}, {}, {}, {}".format(self.ui_input.newfname, self.ui_input.newshape, self.ui_input.newls, self.ui_input.newlamb, self.ui_input.newactf, self.ui_input.newinit))
        save_new_agent(uip.newfname, network, uip.newls, uip.newlamb, uip.newactf)

        # reset input params
        uip = self.ui_input
        uip.newfname = uip.newls = uip.newactf = uip.newlamb = uip.newinit = uip.newshape = uip.newmltype = None

    def train_phase(self):
        """ Run training loop inside a thread and display progression """

        ui_communicate = {"prog": int()}
        cur_prog = int()
        t = Thread(target=GameEngine, args=(self.ui_input, ui_communicate,))
        t.start()

        while ui_communicate["prog"] < self.ui_input.nb - 1:
            if cur_prog != ui_communicate["prog"]:
                cur_prog = ui_communicate["prog"]
                os.system("clear" if os.name == "posix" else "cls")
                prog_bar = ceil(20 * cur_prog / self.ui_input.nb)
                print("Progression ({}): {}".format(ui_communicate["prog"], "#" * prog_bar + "_" * (20 - prog_bar)))

        t.join()
        input("Press enter to exit")


if __name__ == '__main__':
    TrainController()
