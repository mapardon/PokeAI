import os
import time


class FightView:

    @staticmethod
    def display_game(game_config, player1_human, playable_moves, played_moves, turn_nb, game_finished):
        """ Display game state from first player point of view and wait for user choice.

            :param game_config: 'GameStruct' type (under view of player 1)
            :param player1_human: boolean indicating if player 1 is played by user
            :param playable_moves: possible choices for player 1
            :param played_moves: last turn players choice
            turn_nb and game_finished speak for themselves
            :return: move selected by user if applicable
        """
        user_move = None

        os.system("clear" if os.name == "posix" else "cls")

        print("Turn: {}".format(turn_nb), end='\n\n')
        print("team 2: " + ' | '.join("{} ({}/{})".format(p.name, p.cur_hp, p.hp) for p in game_config.team2))
        print("field team 2: {} ({}/{})".format(game_config.on_field2.name, game_config.on_field2.cur_hp, game_config.on_field2.hp), end='\n\n')
        print("field team 1: {} ({}/{})".format(game_config.on_field1.name, game_config.on_field1.cur_hp, game_config.on_field1.hp))
        print("team 1: " + ' | '.join("{} ({}/{})".format(p.name, p.cur_hp, p.hp) for p in game_config.team1))
        print("moves: " + ' - '.join(playable_moves), end="\n\n")

        print("Last turn: p1 {} - p2 {}".format(*played_moves))
        if not game_finished:
            if player1_human:
                while user_move not in playable_moves:
                    user_move = input("move choice > ")
            else:
                # no human player, just display a little before continuing
                user_move = input("move choice > ")
                #time.sleep(0)
        else:
            print("game ended: {}".format(playable_moves[0]))
            user_move = input("press enter to quit > ")

        return user_move
