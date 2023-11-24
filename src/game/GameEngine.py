import copy
import os
from math import ceil
from queue import Queue

from src.agents.PlayerBM import PlayerBM
from src.agents.PlayerGA import PlayerGA
from src.agents.PlayerGT import PlayerGT
from src.agents.PlayerHuman import PlayerHuman
from src.agents.PlayerMDM import PlayerMDM
from src.agents.PlayerNN import PlayerNN
from src.agents.PlayerRL import PlayerRL
from src.agents.PlayerRandom import PlayerRandom
from src.db.dbmanager import retrieve_team, load_ml_agent, update_ml_agent
from src.game.GameEstimation import fill_game_with_estimation
from src.game.PokeGame import PokeGame, gen_random_specs
from src.game.constants import NB_POKEMON, NB_MOVES, MAX_ROUNDS
from src.view.util.UIparameters import FightUIParams, TestUIParams, TrainUIParams


class GameEngine:
    def __init__(self, ui_input: FightUIParams | TestUIParams | TrainUIParams, from_ui: Queue = None,
                 to_ui: Queue = None):
        """

        :param ui_input: UIParams object containing inputs retrieved from UI
        :param from_ui: Shared object to communicate with UI (set to None if not called from UI)
        :param to_ui: Shared object to communicate with UI
        """

        self.ml_names = [ui_input.ml1, ui_input.ml2]

        if ui_input.mode == "fight":
            self.fight_mode(ui_input, from_ui, to_ui)

        elif ui_input.mode == "train":
            self.train_mode(ui_input, to_ui)

        elif ui_input.mode == "test":
            self.test_mode(ui_input, to_ui)

    # init team and players

    @staticmethod
    def get_team_specs(team_src):
        """
        Retrieves specifications to build Pokémon team. Team is either taken from database or generated randomly.

        :param team_src: name of the team in database or 'random' to generate a team
        :return: specifications of the team (cf. PokeGame to see the shape)
        """

        if team_src == "random":
            out = gen_random_specs(NB_POKEMON, NB_MOVES)

        else:
            out = retrieve_team(team_src)

        return out

    @staticmethod
    def init_players(ui_input):
        """
        Initialize Player objects that will be used as agents to play the game.

        :param ui_input: UIParams object containing information to initialize game
        :return: List of two Player objects
        """

        players = list()
        for p, n in zip([ui_input.agent1type, ui_input.agent2type], ["p1", "p2"]):
            if p == "random":
                players.append(PlayerRandom(n))

            elif p == "human":
                players.append(PlayerHuman())

            elif p == "mdm":
                players.append(PlayerMDM(n))

            elif p == "bm":
                players.append(PlayerBM(n))

            elif p == "ml":
                network, ls, lamb, act_f = load_ml_agent(ui_input.ml1 if n == "p1" else ui_input.ml2)
                uip = ui_input
                if uip.agent1type == "ml" and uip.agent2type == "ml" and uip.ml1 == uip.ml2 and p == "p2" and uip.mode == "train":
                    # train mode, both player in ML and same NN -> share object
                    network = players[0].network
                lr = ui_input.lr if ui_input.mode == "train" else None
                mvsel = ui_input.mvsel if ui_input.mode == "train" else "eps-greedy"
                players.append(PlayerRL(n, ui_input.mode, network, ls, lamb, act_f, ui_input.eps, lr, mvsel))

            elif p == "gt":
                players.append(PlayerGT(n))

            elif p == "ga":
                players.append(PlayerGA(n, ui_input.ml1 if n == "p1" else ui_input.ml2, ui_input.ml1 if n == "p2" else ui_input.ml2))

            else:
                players.append(None)

        return players

    # game loops

    def fight_mode(self, ui_input: FightUIParams | TestUIParams | TrainUIParams, from_ui: Queue, to_ui: Queue):
        """
        Game loop for game in terminal, (human vs computer or computer vs computer)

        :param ui_input: FightUIParams object containing inputs retrieved from UI
        :param from_ui: Queue object used to receive messages sent by the controller
        :param to_ui: Queue object used to send messages to the controller
        """

        game = PokeGame([self.get_team_specs(ui_input.team1), self.get_team_specs(ui_input.team2)])
        players = self.init_players(ui_input)
        turn_nb = 1

        player1_human = isinstance(players[0], PlayerHuman)
        to_ui.put(player1_human)

        game_finished = False
        to_ui.put(game_finished)

        while not game_finished:
            # send game to ui for display
            game_state = game.get_player_view("p1")
            playable_moves = game.get_moves_from_state("p1", game.get_cur_state())

            to_ui.put(game_state)
            to_ui.put(playable_moves)
            to_ui.put(turn_nb)

            # player 1 move (wait for input if human, ask AI otherwise)
            if player1_human:
                player1_move = from_ui.get()
            else:
                player1_move = players[0].make_move(game)

            # player 2 move
            player2_move = players[1].make_move(game)

            # send to game
            turn_res = game.play_round(player1_move, player2_move)
            input(turn_res)
            player1_move = "None" if player1_move is None else player1_move
            player2_move = "None" if player2_move is None else player2_move
            last_moves = [player1_move, player2_move]
            to_ui.put(last_moves)
            to_ui.put(turn_res)

            game_finished = game.is_end_state(None)
            to_ui.put(game_finished)

            if not game_finished and game.game_state.on_field1.cur_hp > 0 and game.game_state.on_field2.cur_hp > 0:
                # turn change once attacks have been applied and fainted Pokemon switched
                turn_nb += 1

        # send final state
        game_state = game.get_player_view("p1")
        to_ui.put(game_state)
        result = "player 1 victory" if game.match_result()[0] else "player 2 victory"
        to_ui.put([result])

    def train_mode(self, ui_input, ui_communicate=None):
        """

        :param ui_input: UIParams object for the communication from the menu
        :param ui_communicate: shared object with master thread to communicate progression to UI (unused if not called
            from UI)
        :return: None
        """

        max_rounds = MAX_ROUNDS
        players = self.init_players(ui_input)

        for i in range(ui_input.nb):
            game = PokeGame([self.get_team_specs(ui_input.team1), self.get_team_specs(ui_input.team2)])
            turn_nb = 1
            game_finished = False

            # game loop
            while not game_finished and turn_nb < max_rounds:
                of1, of2 = game.game_state.on_field1, game.game_state.on_field2
                player1_move = players[0].make_move(game) if of1.cur_hp and of2.cur_hp or not of1.cur_hp else None
                player2_move = players[1].make_move(game) if of1.cur_hp and of2.cur_hp or not of2.cur_hp else None

                _ = game.play_round(player1_move, player2_move)
                game_finished = game.is_end_state(None)

                if not game_finished and of1.cur_hp > 0 and of2.cur_hp > 0:
                    turn_nb += 1

            # UI communication
            if ui_communicate is not None:
                ui_communicate["prog"] += 1

            p1_victory, p2_victory = bool(game.match_result())
            # TODO: call backtracking directly
            if isinstance(players[0], PlayerRL):
                players[0].end_game(game, p1_victory)
                update_ml_agent(self.ml_names[0], players[0].network)
            if isinstance(players[1], PlayerRL):
                players[1].end_game(game, p2_victory)
                update_ml_agent(self.ml_names[1], players[1].network)

    def test_mode(self, ui_input, ui_communicate=None):
        """

        :param ui_input: UIParams object for the communication from the menu
        :param ui_communicate: shared object with master thread to communicate progression to UI
        :return: Victory rate of player 1
        """

        players = self.init_players(ui_input)
        p1_victories = int()

        for i in range(ui_input.nb):
            game = PokeGame([self.get_team_specs(ui_input.team1), self.get_team_specs(ui_input.team2)])
            turn_nb = 1
            game_finished = False

            # game loop
            while not game_finished and turn_nb < MAX_ROUNDS:

                if isinstance(players[0], PlayerNN) or isinstance(players[0], PlayerGT):
                    game_p1 = copy.deepcopy(game)
                    fill_game_with_estimation("p1", game_p1)
                else:
                    game_p1 = game

                if isinstance(players[1], PlayerNN) or isinstance(players[1], PlayerGT):
                    game_p2 = copy.deepcopy(game)
                    fill_game_with_estimation("p2", game)
                else:
                    game_p2 = game

                of1, of2 = game.game_state.on_field1, game.game_state.on_field2
                player1_move = players[0].make_move(game_p1) if of1.cur_hp and of2.cur_hp or not of1.cur_hp else None
                player2_move = players[1].make_move(game_p2) if of1.cur_hp and of2.cur_hp or not of2.cur_hp else None

                game.play_round(player1_move, player2_move)
                game_finished = game.is_end_state(None)

                if not game_finished and of1.cur_hp > 0 and of2.cur_hp > 0:
                    # turn change once attacks have been applied and fainted Pokemon switched
                    turn_nb += 1

            p1_victories += game.match_result()[0]

            # UI communication
            if not i % 10:
                if ui_communicate is not None:
                    ui_communicate.put(i)
                elif None:
                    os.system("clear" if os.name == "posix" else "cls")
                    n_syms = ceil(20 * i / ui_input.nb)
                    print("Progression ({}): {}".format(i, "#" * n_syms + "_" * (20 - n_syms)))

        if ui_communicate is not None:
            ui_communicate.put("testing ended")
            ui_communicate.put(p1_victories / ui_input.nb)

        return round(p1_victories / ui_input.nb, 4)
