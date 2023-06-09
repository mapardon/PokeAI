import copy
import random

from src.agents.PlayerComputer import PlayerComputer
from src.db.dbmanager import retrieve_team, load_ml_agent, update_ml_agent
from src.game.PokeGame import PokeGame
from src.game.constants import TYPES
from src.agents.PlayerHuman import PlayerHuman
from src.agents.PlayerRandom import PlayerRandom
from src.agents.PlayerML import PlayerML
from src.agents.PlayerMDM import PlayerMDM


class GameEngine:
    def __init__(self, ui_input, from_ui=None, to_ui=None):
        """

        :param ui_input: Inputs retrieved from UI, type 'UIParams'
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

    def get_team_specs(self, team_src):
        """
        Retrieves specifications to build a team. Team is either taken from database or generated randomly.

        :param team_src: name of the team in database or 'random' to generate a team
        :return: specifications of the team (cf. PokeGame to see the shape)
        """

        out = list()
        NB_POKEMONS = 2  # TODO: update
        if team_src == "random":
            # names (can't have duplicates)
            names = list()
            while len(names) < NB_POKEMONS:
                p_name = ''.join([chr(random.randint(ord('a'), ord('z'))) for _ in range(3)])
                if p_name not in names:
                    names.append(p_name)

            for _, p_name in zip(range(NB_POKEMONS), names):
                p_type = random.choice(TYPES)
                p_stats = [random.randint(80, 180) for _ in range(6)]
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

    def init_players(self, ui_input):

        players = list()
        # TODO: train mode, both player in ML and same NN -> share object
        for p, n in zip([ui_input.agent1type, ui_input.agent2type], [1, 2]):
            n = "p" + str(n)
            if p == "random":
                players.append(PlayerRandom(n))

            elif p == "human":
                players.append(PlayerHuman())

            elif p == "mdm":
                players.append(PlayerMDM(n))

            elif p == "ml":
                network, ls, lamb, act_f = load_ml_agent(ui_input.ml1 if n == "p1" else ui_input.ml2)
                lr = ui_input.lr if ui_input.mode == "train" else None
                mvsel = ui_input.mvsel if ui_input.mode == "train" else "eps-greedy"
                players.append(PlayerML(ui_input.mode, n, network, ls, lamb, act_f, ui_input.eps, lr, mvsel))

            elif p == "cpt":
                players.append(PlayerComputer(n))

            else:
                players.append(None)
        return players

    # game loops

    def fight_mode(self, players, ui_input, from_ui, to_ui):
        """
            Game loop for game in terminal, (human vs computer or computer vs computer)
        """

        self.game = PokeGame([self.get_team_specs(ui_input.team1), self.get_team_specs(ui_input.team2)])
        turn_nb = 1

        player1_human = isinstance(players[0], PlayerHuman)
        to_ui.put(player1_human)

        game_finished = False
        to_ui.put(game_finished)

        while not game_finished:
            # send game to ui for display
            game_state = self.game.get_player1_view()
            to_ui.put(game_state)
            playable_moves = self.game.get_moves_from_state("p1", None)
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
            last_moves = [player1_move * turn_res["p1_moved"] + " & " * (turn_res["p1_moved"] and turn_res["p1_fainted"]) + (self.game.game_state.on_field1.name + " fainted") * turn_res["p1_fainted"],
                          player2_move * turn_res["p2_moved"] + " & " * (turn_res["p2_moved"] and turn_res["p2_fainted"]) + (self.game.game_state.on_field2.name + " fainted") * turn_res["p2_fainted"]]
            to_ui.put(last_moves)

            game_finished = self.game.is_end_state(None)
            to_ui.put(game_finished)

            if not game_finished and self.game.game_state.on_field1.cur_hp > 0 and self.game.game_state.on_field2.cur_hp > 0:
                # turn change once attacks have been applied and fainted pokemons switched
                turn_nb += 1

        # send final state
        game_state = self.game.get_player1_view()
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
            if ui_communicate is not None:
                ui_communicate["prog"] += 1

        ui_communicate["res"] = p1_victories / ui_input.nb
