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
from src.db.dbmanager import load_ml_agent, update_ml_agent
from src.game.GameEstimation import fill_game_with_estimation
from src.game.PokeGame import PokeGame, gen_random_specs
from src.game.constants import NB_POKEMON, NB_MOVES, MAX_ROUNDS
from src.game.GameEngineParams import FightParams, TestParams, TrainParams


class GameEngine:
    def __init__(self, ge_params: FightParams | TestParams | TrainParams, from_ui: Queue | None = None,
                 to_ui: Queue | None = None):
        """
        :param ge_params: "Params" object containing parameters required to run game mode
        :param from_ui: Shared object to communicate with UI (set to None if not called from UI)
        :param to_ui: Shared object to communicate with UI
        """

        self.ge_params = ge_params
        self.from_ui = from_ui
        self.to_ui = to_ui

    # init team and players

    @staticmethod
    def get_team_specs(team_src: list | str):
        """
        Retrieves specifications to build Pokémon team (NB: specs are retrieved for 1 team, not both players)

        :param team_src: Actual team specs or 'random' to call random team specs generator
        :return: Specifications of the team (cf. PokeGame to see the shape)
        """

        if team_src == "random":
            out = gen_random_specs(NB_POKEMON, NB_MOVES)

        else:
            out = team_src

        return out

    @staticmethod
    def init_players(ge_params):
        """
        Initialize Player objects that will be used as agents to play the game.

        :param ge_params: "Params" object containing information to initialize the game
        :return: List of two "Player" objects
        """

        players = list()
        pars = ge_params
        for p, n in zip([pars.agent1type, pars.agent2type], ["p1", "p2"]):
            if p == "random":
                players.append(PlayerRandom(n))

            elif p == "human":
                players.append(PlayerHuman())

            elif p == "mdm":
                players.append(PlayerMDM(n))

            elif p == "bm":
                players.append(PlayerBM(n))

            elif p == "gt":
                players.append(PlayerGT(n))

            elif p == "rl":
                if n == "p1":
                    network, act_f, ls = load_ml_agent(pars.ml1) if type(pars.ml1) == str else pars.ml1
                elif n == "p2":
                    network, act_f, ls = load_ml_agent(pars.ml2) if type(pars.ml2) == str else pars.ml2

                if pars.agent1type == "ml" and pars.agent2type == "ml" and pars.ml1 == pars.ml2 and p == "p2" and pars.mode == "train":
                    # train mode, both player in ML and same NN -> share object
                    network = players[0].network
                lr = pars.lr if pars.mode == "train" else None
                players.append(PlayerRL(n, pars.mode, network, ls, act_f, pars.eps, lr))

            elif p == "ga":
                if n == "p1":
                    network, act_f = load_ml_agent(pars.ml1)[:2] if type(pars.ml1) == str else pars.ml1
                elif n == "p2":
                    network, act_f, _ = load_ml_agent(pars.ml2)[:2] if type(pars.ml2) == str else pars.ml2
                players.append(PlayerGA(n, network, act_f))

            elif p == "ml":
                if n == "p1":
                    network, act_f, _ = load_ml_agent(pars.ml1) if type(pars.ml1) == str else pars.ml1
                elif n == "p2":
                    network, act_f, _ = load_ml_agent(pars.ml2) if type(pars.ml2) == str else pars.ml2
                players.append(PlayerNN(n, network, act_f))

            else:
                players.append(None)

        return players

    # game loops

    def fight_mode(self):
        """
        Game loop for game in terminal, (human vs computer or computer vs computer)
        """

        pars = self.ge_params
        game = PokeGame([self.get_team_specs(pars.team1), self.get_team_specs(pars.team2)])
        players = self.init_players(pars)
        turn_nb = 1

        player1_human = isinstance(players[0], PlayerHuman)
        self.to_ui.put(player1_human)

        game_finished = False
        self.to_ui.put(game_finished)

        while not game_finished:
            # send game to ui for display
            game_state = game.get_player_view("p1")
            playable_moves = game.get_moves_from_state("p1", game.get_cur_state())

            self.to_ui.put(game_state)
            self.to_ui.put(playable_moves)
            self.to_ui.put(turn_nb)

            # Some agents require None values to be estimated
            if isinstance(players[0], PlayerNN) or isinstance(players[0], PlayerGT):
                game_p1 = copy.deepcopy(game)
                fill_game_with_estimation("p1", game_p1)
            else:
                game_p1 = game

            if isinstance(players[1], PlayerNN) or isinstance(players[1], PlayerGT):
                game_p2 = copy.deepcopy(game)
                fill_game_with_estimation("p2", game_p2)
            else:
                game_p2 = game

            # player 1 move (wait for input if human, ask AI otherwise)
            if player1_human:
                player1_move = self.from_ui.get()
            else:
                player1_move = players[0].make_move(game_p1)

            # player 2 move
            player2_move = players[1].make_move(game_p2)

            # send to game
            turn_res = game.play_round(player1_move, player2_move)
            input(turn_res)
            player1_move = "None" if player1_move is None else player1_move
            player2_move = "None" if player2_move is None else player2_move
            last_moves = [player1_move, player2_move]
            self.to_ui.put(last_moves)
            self.to_ui.put(turn_res)

            game_finished = game.is_end_state(None)
            self.to_ui.put(game_finished)

            if not game_finished and game.game_state.on_field1.cur_hp > 0 and game.game_state.on_field2.cur_hp > 0:
                # turn change once attacks have been applied and fainted Pokemon switched
                turn_nb += 1

        # send final state
        game_state = game.get_player_view("p1")
        self.to_ui.put(game_state)
        result = "player 1 victory" if game.match_result()[0] else "player 2 victory"
        self.to_ui.put([result])

    def train_mode(self, display: bool = False) -> None:
        """
            :param display: Indicates whether a display of the progression is required
        """

        pars = self.ge_params
        players = self.init_players(pars)

        for i in range(pars.nb):
            game = PokeGame([self.get_team_specs(pars.team1), self.get_team_specs(pars.team2)])
            turn_nb = 1
            game_finished = False

            # game loop
            while not game_finished and turn_nb < MAX_ROUNDS:

                # Some agents require None values to be estimated
                if isinstance(players[0], PlayerNN) or isinstance(players[0], PlayerGT):
                    game_p1 = copy.deepcopy(game)
                    fill_game_with_estimation("p1", game_p1)
                else:
                    game_p1 = game

                if isinstance(players[1], PlayerNN) or isinstance(players[1], PlayerGT):
                    game_p2 = copy.deepcopy(game)
                    fill_game_with_estimation("p2", game_p2)
                else:
                    game_p2 = game

                # Actual game
                of1, of2 = game.game_state.on_field1, game.game_state.on_field2
                player1_move = players[0].make_move(game_p1) if of1.cur_hp and of2.cur_hp or not of1.cur_hp else None
                player2_move = players[1].make_move(game_p2) if of1.cur_hp and of2.cur_hp or not of2.cur_hp else None

                _ = game.play_round(player1_move, player2_move)
                game_finished = game.is_end_state(None)

                # End-of-turn weights update
                if not game_finished:
                    if isinstance(players[0], PlayerRL):
                        players[0].backpropagation(game.get_numeric_repr(player="p1"), False, None)
                    if isinstance(players[1], PlayerRL):
                        players[1].backpropagation(game.get_numeric_repr(player="p2"), False, None)

                if not game_finished and of1.cur_hp > 0 and of2.cur_hp > 0:
                    turn_nb += 1

            # Display progression
            if display:
                os.system("clear" if os.name == "posix" else "cls")
                print("Training: {}/{}".format(i, pars.nb))

            # Endgame weights update
            p1_victory, p2_victory = game.match_result()
            if isinstance(players[0], PlayerRL):
                players[0].backpropagation(game.get_numeric_repr(player="p1"), True, p1_victory)
                if type(pars.ml1) == str:
                    update_ml_agent(pars.ml1, players[0].network)
            if isinstance(players[1], PlayerRL):
                players[0].backpropagation(game.get_numeric_repr(player="p2"), True, p1_victory)
                if type(pars.ml2) == str:
                    update_ml_agent(pars.ml2, players[1].network)

    def test_mode(self, display: bool = False) -> float:
        """
        :param display: Indicates whether a display of the progression is required
        :return: Victory rate of player 1
        """

        pars = self.ge_params
        players = self.init_players(pars)
        p1_victories = int()

        for i in range(pars.nb):
            game = PokeGame([self.get_team_specs(pars.team1), self.get_team_specs(pars.team2)])
            turn_nb = 1
            game_finished = False

            # game loop
            while not game_finished and turn_nb < MAX_ROUNDS:

                # Some agents require None values to be estimated
                if isinstance(players[0], PlayerNN) or isinstance(players[0], PlayerGT):
                    game_p1 = copy.deepcopy(game)
                    fill_game_with_estimation("p1", game_p1)
                else:
                    game_p1 = game

                if isinstance(players[1], PlayerNN) or isinstance(players[1], PlayerGT):
                    game_p2 = copy.deepcopy(game)
                    fill_game_with_estimation("p2", game_p2)
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
                if self.to_ui is not None:
                    self.to_ui.put(i)
                elif display:
                    os.system("clear" if os.name == "posix" else "cls")
                    n_syms = ceil(20 * i / pars.nb)
                    print("Progression ({}): {}".format(i, "#" * n_syms + "_" * (20 - n_syms)))

        if self.to_ui is not None:
            self.to_ui.put("testing ended")
            self.to_ui.put(p1_victories / pars.nb)
        elif display:
            print("testing ended\np1 victories: {}".format(p1_victories / pars.nb))

        return round(p1_victories / pars.nb, 4)
