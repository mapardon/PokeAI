import sys

from src.util.UIparameters import TestUIParams

sys.path.append('/home/mathieu/PycharmProjects/PokeAI')

import os
import sys
from math import ceil
from threading import Thread

from src.game.GameEngine import GameEngine

sys.path.append('/home/mathieu/PycharmProjects/PokeAI')

import time

from src.view.TestMenu import TestMenu


class TestController:
    """ Training and creating agents """

    def __init__(self):

        self.ui_input = TestUIParams()
        self.menu = TestMenu(self.ui_input)
        self.menu_loop()

    def menu_loop(self):
        """ Select parameters for training """
        ui_input = {"mode": str()}

        while ui_input["mode"] != "leave":

            self.menu.menu_loop()

            if ui_input["mode"] == "leave":
                break

            elif ui_input["mode"] == "test":
                self.test_phase()

    def test_phase(self):
        """ Run test loop. Exit condition test whether win rate is received (indicate games are all finished) """

        ui_communicate = {"prog": int(), "res": float()}
        cur_prog = int()
        t = Thread(target=GameEngine, args=(self.ui_input, ui_communicate,))
        t.start()

        while 1 <= ui_communicate["prog"] < self.ui_input.nb - 1:
            if cur_prog != ui_communicate["prog"]:
                cur_prog = ui_communicate["prog"]
                os.system("clear")
                n_syms = ceil(20 * cur_prog / self.ui_input.nb)
                print("Progression ({}): {}".format(ui_communicate["prog"], "#" * n_syms + "_" * (20 - n_syms)))

        t.join()
        input("Player win rate: {}%\nPress enter to exit".format(round(100 * ui_communicate["res"], 2)))


if __name__ == '__main__':

    TestController()
