import os

from src.db.dbmanager import available_ml_agents, remove_ml_agent


class ManageController:
    def __init__(self):

        self.menu_phase()

    def menu_phase(self):
        ui_input = str()
        warning = None
        out = None

        while warning is not None or out is None:
            os.system("clear" if os.name == "posix" else "cls")
            self.display_instructions(available_ml_agents())

            print("Warning : {}".format(warning))
            warning = None  # reset
            ui_input = input("selection > ").split(" ")

            if ui_input[0] == "leave":
                break

            elif ui_input[0] == "delete" and len(ui_input) == 2:
                if ui_input[1] not in available_ml_agents():
                    warning = "Agent not found"
                else:
                    remove_ml_agent(ui_input[1])

    def display_instructions(self, agents):
        print("\n * Available agents:\n")
        for i in agents:
            print("\t - " + i)
        print("\ndelete z   # remove agent z from database", end='\n\n')


if __name__ == '__main__':

    ManageController()
