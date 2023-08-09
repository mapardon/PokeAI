import random
from queue import Queue
from typing import Union

from src.agents import AbstractPlayer
from src.agents.PlayerBM import PlayerBM
from src.agents.PlayerHuman import PlayerHuman
from src.agents.PlayerMDM import PlayerMDM
from src.agents.PlayerML import PlayerML
from src.agents.PlayerRandom import PlayerRandom
from src.db.dbmanager import retrieve_team, load_ml_agent, update_ml_agent
from src.game.PokeGame import PokeGame
from src.game.constants import TYPES, MIN_HP, MAX_HP, MIN_STAT, MAX_STAT, MIN_POW, MAX_POW
from src.view.util.UIparameters import FightUIParams, TestUIParams, TrainUIParams

NB_POKEMON = 3
NB_MOVES = 3


class GameEngine:
    def __init__(self, ui_input: Union[FightUIParams, TestUIParams, TrainUIParams], from_ui: Queue = None,
                 to_ui: Queue = None):
        """

        :param ui_input: UIParams object containing inputs retrieved from UI
        :param from_ui: Shared object to communicate with UI (set to None if not called from UI)
        :param to_ui: Shared object to communicate with UI
        """

        # retrieve specified teams specs from database to initialize game
        self.game = None
        players = self.init_players(ui_input)
        self.ml_names = [ui_input.ml1, ui_input.ml2]

        if ui_input.mode == "fight":
            self.fight_mode(players, ui_input, from_ui, to_ui)

        elif ui_input.mode == "train":
            self.train_mode(players, ui_input, to_ui)

        elif ui_input.mode == "test":
            self.test_mode(players, ui_input, to_ui)

    # init team and players

    @staticmethod
    def get_team_specs(team_src):
        """
        Retrieves specifications to build Pokémon team. Team is either taken from database or generated randomly.

        :param team_src: name of the team in database or 'random' to generate a team
        :return: specifications of the team (cf. PokeGame to see the shape)
        """

        out = list()
        if team_src == "random":
            # NB: names can't have duplicates
            names = list()

            while len(names) < NB_POKEMON:
                p_name = ''.join([chr(random.randint(ord('a'), ord('z'))) for _ in range(3)])
                if p_name not in names:
                    names.append(p_name)

            for _, p_name in zip(range(NB_POKEMON), names):
                # Pokemon
                p_type = random.choice(TYPES)
                p_stats = [random.randint(MIN_HP, MAX_HP)] + [random.randint(MIN_STAT, MAX_STAT) for _ in range(3)]
                poke = [tuple([p_name, p_type] + p_stats)]

                # Attacks
                temp_mv = list()
                stab = poke[0][1]
                cp_types = [t for t in TYPES if t != stab]

                # STAB
                a_type = stab
                a_power = MIN_POW
                a_name = "light_" + a_type.lower()
                temp_mv.append((a_name, a_type, a_power))

                for _ in range(NB_MOVES - 1):
                    a_type = cp_types.pop(random.randrange(len(cp_types)))
                    a_power = random.choice([MIN_POW, MAX_POW])
                    a_name = ("light_" if a_power == 50 else "heavy_") + a_type.lower()
                    temp_mv.append((a_name, a_type, a_power))
                poke.append(tuple(temp_mv))
                out.append(tuple(poke))

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
                players.append(PlayerML(ui_input.mode, n, network, ls, lamb, act_f, ui_input.eps, lr, mvsel))

            else:
                players.append(None)

        return players

    # game loops

    def fight_mode(self, players: list[AbstractPlayer, AbstractPlayer],
                   ui_input: Union[FightUIParams, TestUIParams, TrainUIParams], from_ui: Queue, to_ui: Queue):
        """
        Game loop for game in terminal, (human vs computer or computer vs computer)

        :param players: List of two initialized Player objects
        :param ui_input: FightUIParams object containing inputs retrieved from UI
        :param from_ui: Queue object used to receive messages sent by the controller
        :param to_ui: Queue object used to send messages to the controller
        """

        self.game = PokeGame([self.get_team_specs(ui_input.team1), self.get_team_specs(ui_input.team2)])
        turn_nb = 1

        player1_human = isinstance(players[0], PlayerHuman)
        to_ui.put(player1_human)

        game_finished = False
        to_ui.put(game_finished)

        while not game_finished:
            # send game to ui for display
            game_state = self.game.get_player_view("p1")
            playable_moves = self.game.get_moves_from_state("p1", None)

            to_ui.put(game_state)
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
            turn_res = self.game.play_round(player1_move, player2_move)
            input(turn_res)
            player1_move = "None" if player1_move is None else player1_move
            player2_move = "None" if player2_move is None else player2_move
            last_moves = [player1_move, player2_move]
            to_ui.put(last_moves)
            to_ui.put(turn_res)

            game_finished = self.game.is_end_state(None)
            to_ui.put(game_finished)

            if not game_finished and self.game.game_state.on_field1.cur_hp > 0 and self.game.game_state.on_field2.cur_hp > 0:
                # turn change once attacks have been applied and fainted Pokemon switched
                turn_nb += 1

        # send final state
        game_state = self.game.get_player_view("p1")
        to_ui.put(game_state)
        result = "player 1 victory" if self.game.first_player_won() else "player 2 victory"
        to_ui.put([result])

    def train_mode(self, players, ui_input, ui_communicate=None):
        """

        :param players: 2-tuple with Player objects that will run "make_move" function
        :param ui_input: UIParams object for the communication from the menu
        :param ui_communicate: shared object with master thread to communicate progression to UI (unused if not called
            from UI)
        :return: None
        """

        max_rounds = 50
        p1_victories = int()

        for i in range(ui_input.nb):
            self.game = PokeGame([self.get_team_specs(ui_input.team1), self.get_team_specs(ui_input.team2)])
            turn_nb = 1
            game_finished = False

            # game loop
            while not game_finished and turn_nb < max_rounds:
                player1_move = players[0].make_move(self.game)
                player2_move = players[1].make_move(self.game)

                turn_res = self.game.play_round(player1_move, player2_move)
                game_finished = self.game.is_end_state(None)

                if not game_finished and self.game.game_state.on_field1.cur_hp > 0 and self.game.game_state.on_field2.cur_hp > 0:
                    turn_nb += 1

            p1_victories += game_finished and self.game.first_player_won()

            # UI communication
            if ui_communicate is not None:
                ui_communicate["prog"] += 1

            victory = bool(self.game.first_player_won())
            if isinstance(players[0], PlayerML):
                players[0].end_game(self.game, victory)
                update_ml_agent(self.ml_names[0], players[0].network)
            if isinstance(players[1], PlayerML):
                players[1].end_game(self.game, not victory)
                update_ml_agent(self.ml_names[1], players[1].network)

    def test_mode(self, players, ui_input, ui_communicate=None):
        """

        :param players: 2-tuple with Player objects that will run "make_move" function
        :param ui_input: UIParams object for the communication from the menu
        :param ui_communicate: shared object with master thread to communicate progression to UI
        :return: None
        """

        max_rounds = 50
        p1_victories = int()

        for i in range(ui_input.nb):
            self.game = PokeGame([self.get_team_specs(ui_input.team1), self.get_team_specs(ui_input.team2)])
            turn_nb = 1
            game_finished = False

            # game loop
            while not game_finished and turn_nb < max_rounds:
                player1_move = players[0].make_move(self.game)
                player2_move = players[1].make_move(self.game)

                self.game.play_round(player1_move, player2_move)
                game_finished = self.game.is_end_state(None)

                if not game_finished and self.game.game_state.on_field1.cur_hp > 0 and self.game.game_state.on_field2.cur_hp > 0:
                    # turn change once attacks have been applied and fainted Pokemon switched
                    turn_nb += 1

            p1_victories += game_finished and self.game.first_player_won()

            # UI communication
            if ui_communicate is not None and not i % 10:
                ui_communicate.put(i)

        if ui_communicate is not None:
            ui_communicate.put("testing ended")
            ui_communicate.put(p1_victories / ui_input.nb)
