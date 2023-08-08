from src.controller.FightController import FightController
from src.controller.TrainController import TrainController
from src.controller.TestController import TestController
from src.controller.ManageController import ManageController
from src.view.MainMenu import MainMenu


class MainController:
    def __init__(self):

        self.main_controller()

    def main_controller(self):
        ui_input = {"mode": str()}

        while ui_input["mode"] != "leave":

            ui_input = MainMenu().menu_loop()

            # dispatch main menu input

            if ui_input["mode"] == "leave":
                break

            elif ui_input["mode"] == "fight":
                FightController()

            elif ui_input["mode"] == "train":
                TrainController()

            elif ui_input["mode"] == "test":
                TestController()

            elif ui_input["mode"] == "manage":
                ManageController()
