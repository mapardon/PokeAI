import sys

from src.view.util.UIparameters import TestUIParams

sys.path.append('/home/mathieu/PycharmProjects/PokeAI')

import os
import sys
from math import ceil
from threading import Thread

from src.game.GameEngine import GameEngine

sys.path.append('/home/mathieu/PycharmProjects/PokeAI')

from src.view.TestMenu import TestMenu


class TestController:
    """ Training and creating agents """

    def __init__(self):

        self.ui_input = TestUIParams()
        self.menu = TestMenu(self.ui_input)
        self.menu_loop()

    def menu_loop(self):
        """ Select parameters for training """

        while self.ui_input.mode != "leave":

            self.menu.menu_loop()

            if self.ui_input.mode == "leave":
                break

            elif self.ui_input.mode == "test":
                self.test_phase()

    def test_phase(self):
        """ Run test loop. Exit condition test whether win rate is received (indicate games are all finished) """
        from_backend_to_ui = {"prog": int(), "res": float()}

        t_ge = Thread(target=GameEngine, args=(self.ui_input, None, from_backend_to_ui,))
        t_fl = Thread(target=self.test_loop, args=(from_backend_to_ui,))

        t_ge.start()
        t_fl.start()

        t_ge.join()
        t_fl.join()

    def test_loop(self, from_backend):
        cur_prog = int()

        while from_backend["prog"] < self.ui_input.nb - 1:
            if cur_prog != from_backend["prog"]:
                cur_prog = from_backend["prog"]
                os.system("clear" if os.name == "posix" else "cls")
                n_syms = ceil(20 * cur_prog / self.ui_input.nb)
                print("Progression ({}): {}".format(from_backend["prog"], "#" * n_syms + "_" * (20 - n_syms)))

        input("Player 1 win rate: {}%\nPress enter to exit".format(round(100 * from_backend["res"], 2)))


if __name__ == '__main__':
    TestController()
