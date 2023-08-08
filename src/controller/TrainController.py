import sys

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

            elif ui_input.mode == "train":
                self.train_phase()

    def train_phase(self):
        """ Run training loop inside a thread and display progression """

        from_backend_to_ui = {"prog": int()}
        t_ge = Thread(target=GameEngine, args=(self.ui_input, None, from_backend_to_ui,))
        t_fl = Thread(target=self.train_loop, args=(from_backend_to_ui,))

        t_ge.start()
        t_fl.start()

        t_ge.join()
        t_fl.join()

    def train_loop(self, from_backend):

        cur_prog = int()

        while from_backend["prog"] < self.ui_input.nb - 1:
            if cur_prog != from_backend["prog"]:
                cur_prog = from_backend["prog"]
                os.system("clear" if os.name == "posix" else "cls")
                prog_bar = ceil(20 * cur_prog / self.ui_input.nb)
                print("Progression ({}): {}".format(from_backend["prog"], "#" * prog_bar + "_" * (20 - prog_bar)))

        input("Press enter to exit")


if __name__ == '__main__':
    TrainController()
