import sys
from queue import Queue

from src.util.UIparameters import FightUIParams

sys.path.append('/home/mathieu/PycharmProjects/PokeAI')

from threading import Thread

from src.game.GameEngine import GameEngine
from src.view.FightMenu import FightMenu
from src.view.FightView import FightView


class FightController:
    def __init__(self):

        self.ui_input = FightUIParams()
        self.ui_input.mode = "fight"
        self.ui_input.player1 = "random"
        self.ui_input.player2 = "random"
        self.menu = FightMenu(self.ui_input)
        self.fight_view = FightView()
        self.ge = None

        self.menu_loop()

    def menu_loop(self):
        """ Select parameters for match """
        ui_input = self.ui_input

        while ui_input.mode != "leave":

            # self.menu.menu_loop()

            if ui_input.mode == "leave":
                break

            elif ui_input.mode == "fight":
                self.fight_phase()

                ui_input.mode = str()

    def fight_phase(self):
        from_backend_to_ui = Queue()
        from_ui_to_backend = Queue()
        t_ge = Thread(target=GameEngine, args=(self.ui_input, from_ui_to_backend, from_backend_to_ui,))
        t_fl = Thread(target=self.fight_loop, args=(from_backend_to_ui, from_ui_to_backend,))

        t_ge.start()
        t_fl.start()

        t_ge.join()
        t_fl.join()
        print("joined")

    def fight_loop(self, from_backend, to_backend):

        # wait for player1 type
        player1_human = from_backend.get()
        game_finished = from_backend.get()

        while not game_finished:

            # wait until receiving game state (to display it)
            game_state = from_backend.get()
            playable_moves = from_backend.get()

            # send to view and wait for answer (user move)
            if player1_human:
                user_move = self.fight_view.display_game(game_state, player1_human, playable_moves, 1, False)
                to_backend.put(user_move)
            else:  # no input required, only send for display purposes
                self.fight_view.display_game(game_state, player1_human, playable_moves, 1, False)

            # outcome of turn
            fainted = from_backend.get()
            game_finished = from_backend.get()

            # additional switch required in case of faint
            if not game_finished and fainted:

                p1_has_fainted = from_backend.get()
                game_state = from_backend.get()

                if p1_has_fainted and player1_human:
                    playable_moves = from_backend.get()

                    user_move = self.fight_view.display_game(game_state, player1_human, playable_moves, 1, False)
                    to_backend.put(user_move)

                else:
                    self.fight_view.display_game(game_state, player1_human, playable_moves, 1, False)

        # wait final results
        game_state = from_backend.get()
        result = from_backend.get()

        self.fight_view.display_game(game_state, player1_human, result, 1, True)


if __name__ == "__main__":
    FightController()
