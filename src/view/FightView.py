import os

from src.game.PokeGame import PokeGame


class FightView:

    @staticmethod
    def display_game(player1_view: PokeGame.GameStruct, player1_human: bool, playable_moves: list, played_moves: list,
                     turn_res: dict, turn_nb: int, game_finished: bool):
        """
        Display game state from first player point of view and wait for user choice.

        :param player1_view: 'GameStruct' object, view of player 1
        :param player1_human: boolean indicating if player 1 is played by user
        :param playable_moves: possible choices for player 1
        :param played_moves: last turn players choice
        :param turn_res: dict returned by "play_round" of PokeGame class, containing feedback on last round
        :param turn_nb: integer representing the number of the turn
        :param game_finished: bool values indicating whether the provided state is an end state
        :return: move selected by user if applicable
        """

        user_move = None

        os.system("clear" if os.name == "posix" else "cls")

        print("Turn: {}".format(turn_nb), end='\n\n')
        print("team 2: " + ''.join('\n' + str(p) for p in player1_view.team2))
        print("\nfield team 2: {} ({}/{})".format(player1_view.on_field2.name, player1_view.on_field2.cur_hp, player1_view.on_field2.hp), end='\n\n')
        print("field team 1: {} ({}/{})\n".format(player1_view.on_field1.name, player1_view.on_field1.cur_hp, player1_view.on_field1.hp))
        print("team 1: " + ''.join('\n' + str(p) for p in player1_view.team1))
        print("moves: " + ' - '.join(playable_moves if None not in playable_moves else ["None"]), end="\n\n")

        if turn_res is not None:
            print("Last turn: p1 {} - p2 {}".format(
                  played_moves[0] * turn_res["p1_moved"] + " & " * (turn_res["p1_moved"] and turn_res["p1_fainted"]) + (player1_view.on_field1.name + " fainted") * turn_res["p1_fainted"],
                  played_moves[1] * turn_res["p2_moved"] + " & " * (turn_res["p2_moved"] and turn_res["p2_fainted"]) + (player1_view.on_field2.name + " fainted") * turn_res["p2_fainted"]),
                  sep=" ")

        if not game_finished:
            if player1_human and playable_moves != [None]:
                while str(user_move) not in playable_moves:
                    user_move = input("move choice > ")
            else:
                # no human player or must not choose, just display a little before continuing
                input("continue > ")
                user_move = None

        else:
            print("game ended: {}".format(playable_moves[0]))
            user_move = input("press enter to quit > ")

        return user_move
