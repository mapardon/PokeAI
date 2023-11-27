import os


class MainMenu:

    def menu_loop(self):
        warning = None
        out = None

        while warning is not None or out is None:
            os.system("clear" if os.name == "posix" else "cls")
            self.display_instructions()

            print("Warning : {}".format(warning))
            warning = None  # reset
            inputted = input("selection > ").split(" ")

            # launch something
            if inputted[0] in ("leave", "fight", "train", "test", "manage"):
                out = {"mode": inputted[0]}

        return out

    def display_instructions(self):
        instructions = [
            "fight      # go to fight menu (match)",
            "test       # go to comparison/test menu",
            "leave      # exit program",
            ""]

        print("\n * Welcome...\n")
        for i in instructions:
            print("\t" + i)
