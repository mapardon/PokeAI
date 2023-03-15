import copy
import random
import time

from src.db.dbmanager import retrieve_team
from src.game.PokeGame import PokeGame, TYPES
from src.game.agents.PlayerHuman import PlayerHuman
from src.game.agents.PlayerRandom import PlayerRandom


class GameEngine:
    def __init__(self, ui_input, from_ui=None, to_ui=None):
        """

        :param ui_input: Inputs retrieved from UI, type 'UIparams'
        :param from_ui: Shared object to communicate with UI (set to None if not called from UI)
        :param to_ui: Shared object to communicate with UI
        """

        # retrieve specified teams specs from database to initialize game
        self.game = PokeGame([self.get_team_specs(ui_input.team1), self.get_team_specs(ui_input.team2)])
        players = self.init_players(ui_input.player1, ui_input.player2)

        if ui_input.mode == "fight":
            self.fight_mode(players, from_ui, to_ui)

        elif ui_input.mode == "train":
            self.train_mode(players, ui_input.nb, from_ui, to_ui)

        elif ui_input.mode == "test":
            self.test_mode(players, ui_input.nb, from_ui, to_ui)

    # utility methods

    def get_team_specs(self, team_src):
        """
        Retrieves specifications to build a team. Team is either taken from database or generated randomly.

        :param team_src: name of the team in database or 'random' to generate a team
        :return: specifications of the team (cf. PokeGame to see the shape)
        """

        out = list()
        NB_POKEMONS = 2  # TODO: update
        if team_src == "random":
            for _ in range(NB_POKEMONS):
                p_name = ''.join([chr(random.randint(ord('a'), ord('z'))) for _ in range(3)])
                p_type = random.choice(TYPES)
                p_stats = [random.randint(80, 200) for _ in range(6)]
                poke = [tuple([p_name, p_type] + p_stats)]

                temp_mv = list()
                # STAB
                a_type = poke[0][1]
                a_power = random.choice([50, 100])
                a_name = ("light_" if a_power == 50 else "heavy_") + a_type.lower()
                temp_mv.append((a_name, a_type, a_power))

                for _ in range(1):
                    a_type = random.choice(TYPES)
                    a_power = random.choice([50, 100])
                    a_name = ("light_" if a_power == 50 else "heavy_") + a_type.lower()
                    temp_mv.append((a_name, a_type, a_power))
                poke.append(tuple(temp_mv))
                out.append(tuple(poke))

        else:
            out = retrieve_team(team_src)

        return out

    def init_players(self, player1_type, player2_type):
        players = list()
        for p, n in zip([player1_type, player2_type], [1, 2]):
            if p == "random":
                players.append(PlayerRandom(str(n)))
            elif p == "human":
                players.append(PlayerHuman())
            else:
                players.append(None)
        return players

    # game loops

    def fight_mode(self, players, from_ui, to_ui):
        player1_human = isinstance(players[0], PlayerHuman)
        to_ui.put(player1_human)

        game_finished = False
        to_ui.put(game_finished)
        turn_nb = 1

        while not game_finished:
            # send game to ui for display
            game_state = self.game.get_player1_view()
            to_ui.put(copy.deepcopy(game_state))
            playable_moves = self.game.get_player1_moves()
            to_ui.put(playable_moves)
            to_ui.put(turn_nb)

            # player 1 move (wait for input if human, ask AI otherwise)
            if player1_human:
                player1_move = from_ui.get()
            else:
                player1_move = players[0].make_move(self.game)

            # player 2 move
            player2_move = players[1].make_move(self.game)

            # send to game
            turn_res = self.game.apply_player_moves(player1_move, player2_move)
            last_moves = [player1_move * turn_res["p1_moved"] + " & " * (turn_res["p1_moved"] and turn_res["p1_fainted"]) + (self.game.game_state.on_field1.name + " fainted") * turn_res["p1_fainted"],
                          player2_move * turn_res["p2_moved"] + " & " * (turn_res["p2_moved"] and turn_res["p2_fainted"]) + (self.game.game_state.on_field2.name + " fainted") * turn_res["p2_fainted"]]
            to_ui.put(last_moves)
            to_ui.put(turn_res)

            game_finished = self.game.game_finished()
            to_ui.put(game_finished)

            # TODO: handle multiple faints
            # if any side has fainted and game is not over, must choose replacement before next turn
            if not game_finished and (turn_res["p1_fainted"] or turn_res["p2_fainted"]):
                player1_move = None
                player2_move = None

                # notify presence of faints and send intermediate state
                game_state = self.game.get_player1_view()
                to_ui.put(copy.deepcopy(game_state))

                if turn_res["p1_fainted"]:
                    if player1_human:
                        playable_moves = self.game.get_player1_moves()
                        to_ui.put(playable_moves)

                        player1_move = from_ui.get()

                    else:
                        player1_move = players[0].make_move(self.game)

                if turn_res["p2_fainted"]:
                    player2_move = players[1].make_move(self.game)

                self.game.apply_player_moves(player1_move, player2_move)
                last_moves = [player1_move, player2_move]
                to_ui.put(last_moves)

            turn_nb += 1

        # send final state
        game_state = self.game.get_player1_view()
        to_ui.put(game_state)
        result = "player 1 victory" if self.game.first_player_won() else "player 2 victory"
        to_ui.put([result])

    def train_mode(self, players, nb_games, from_ui, to_ui):
        for _ in range(nb_games):
            to_ui["prog"] += 1
            time.sleep(0.1)

    def train_modes(self, players, nb_games, ui_communicate=None):
        """

        :param players: 2-tuple with Player objects that will run "make_move" function
        :param nb_games: number of games to be run
        :param ui_communicate: shared object with master thread to communicate progression to UI (unused if not called
            from UI)
        :return: None
        """

        max_rounds = 50

        for i in range(nb_games):
            n_rounds = int()

            # game loop
            while not self.game.game_finished() and n_rounds < max_rounds:
                player1_move = players[0].make_move(self.game.get_player1_view())
                player2_move = players[1].make_move(self.game.get_player2_view())

                self.game.apply_player_moves(player1_move, player2_move)
                n_rounds += 1

            victory = self.game.first_player_won()
            players[0].end_game(self.game, victory)

            # UI communication
            if ui_communicate is not None:
                ui_communicate["prog"] += 1

    def test_mode(self, players, nb_games, from_ui, to_ui):
        for _ in range(nb_games):
            to_ui["prog"] += 1
            time.sleep(0.1)
        to_ui["res"] = random.random()

    def test_modes(self, players, nb_games, ui_communicate):
        """

        :param players: 2-tuple with Player objects that will run "make_move" function
        :param nb_games: number of games to be run
        :param ui_communicate: shared object with master thread to communicate progression to UI
        :return: None
        """

        max_rounds = 50
        p1_victories = int()

        for i in range(nb_games):
            n_rounds = int()

            # game loop
            while not self.game.game_finished() and n_rounds < max_rounds:
                cur_state = self.game.get_game_state()
                player1_move = players[0].make_move(cur_state)
                player2_move = players[1].make_move(cur_state)

                self.game.apply_player_moves(player1_move, player2_move)
                n_rounds += 1

            victory = self.game.first_player_won()
            players[0].end_game(self.game, victory)
            p1_victories += victory

            # UI communication
            if ui_communicate is not None:
                ui_communicate["prog"] += 1

        ui_communicate["res"] = p1_victories / nb_games
