"""
    Alternative implementations for the requirements of some experiments
"""

import copy
import os
from math import ceil

from src.agents.PlayerBM import PlayerBM
from src.agents.PlayerGA import PlayerGA
from src.agents.PlayerGT import PlayerGT
from src.agents.PlayerHuman import PlayerHuman
from src.agents.PlayerMDM import PlayerMDM
from src.agents.PlayerNN import PlayerNN
from src.agents.PlayerRL import PlayerRL
from src.agents.PlayerRandom import PlayerRandom
from src.db.dbmanager import load_ml_agent
from src.game.GameEngine import GameEngine
from src.game.GameEstimation import fill_game_with_estimation
from src.game.PokeGame import PokeGame
from src.game.constants import TYPES, TYPES_INDEX, MAX_HP, MAX_STAT, MIN_STAT, MAX_ROUNDS
from src.game.GameEngineParams import TestParams


class PokeGameAlt1(PokeGame):
    def __init__(self, team_specs):
        super().__init__(team_specs)

    def __copy__(self):
        return super().cp(self)

    def __deepcopy__(self, memodict={}):
        return self.__copy__()

    def get_numeric_repr(self, state: PokeGame.GameStruct = None, player: str = None) -> list[int]:
        """
            Alternative numeric representation, one-hot encoding: categorical variables (types) are deflated and
        bucketing is performed on continuous variables (statistics).

        :param state: GameStruct object to be converted. If None, use object attributes
        :param player: "p1" or "p2", indicating which view must be converted. If None, use self.game_state
        :return: list of int representing schematically the state
        """

        if state is None:
            if player == "p1":
                state = self.player1_view
            elif player == "p2":
                state = self.player2_view
            else:
                state = self.game_state

        num_state = list()
        for t, of in zip([state.team1, state.team2], [state.on_field1, state.on_field2]):
            for p in [of] + [p for p in t if p.name != of.name]:
                mvs = list()
                for m in p.moves:
                    if m.name is None:
                        mvs += [0] * (len(TYPES) + 2)
                    else:
                        mvs += [int(i == TYPES_INDEX[m.move_type]) for i in range(len(TYPES))] + [
                            int(m.base_pow == 50), int(m.base_pow == 100)]
                if p.name is None:
                    num_state += [0] * (len(TYPES) + 11 + 8 + 8 + 8) + mvs
                else:
                    num_state += [int(i == TYPES_INDEX[p.poke_type]) for i in range(len(TYPES))]
                    num_state += [int(ceil(p.cur_hp / (MAX_HP / 10)) == i) for i in range(11)]
                    for stat in (p.atk, p.des, p.spe):
                        if stat is None:
                            num_state += [0] * 8
                        else:
                            num_state += [int(min(7, stat // ((MAX_STAT - MIN_STAT) / 8)) == i) for i in range(8)]
                    num_state += mvs

        return num_state


class PokeGameAlt2(PokeGame):
    def __init__(self, team_specs):
        super().__init__(team_specs)

    def __copy__(self):
        return PokeGame.cp(self)

    def __deepcopy__(self, memodict={}):
        return self.__copy__()

    def get_numeric_repr(self, state: PokeGame.GameStruct = None, player: str = None) -> list[int]:
        """
            Alternative numeric representation, one-hot encoding: categorical variables (types) are deflated but no
        bucketing is performed on continuous variables (statistics) which are kept as integers.

        :param state: GameStruct object to be converted. If None, use object attributes
        :param player: "p1" or "p2", indicating which view must be converted. If None, use self.game_state
        :return: list of int representing schematically the state
        """

        if state is None:
            if player == "p1":
                state = self.player1_view
            elif player == "p2":
                state = self.player2_view
            else:
                state = self.game_state

        num_state = list()
        for t, of in zip([state.team1, state.team2], [state.on_field1, state.on_field2]):
            for p in [of] + [p for p in t if p.name != of.name]:
                mvs = list()
                for m in p.moves:
                    if m.name is None:
                        mvs += [0] * (len(TYPES) + 2)
                    else:
                        mvs += [int(i == TYPES_INDEX[m.move_type]) for i in range(len(TYPES))] + [
                            int(m.base_pow == 50), int(m.base_pow == 100)]

                if p.name is None:
                    num_state += [0] * (len(TYPES) + 4) + mvs
                else:
                    num_state += [int(i == TYPES_INDEX[p.poke_type]) for i in range(len(TYPES))]
                    for stat in (p.cur_hp, p.atk, p.des, p.spe):
                        num_state.append(0 if stat is None else stat)
                    num_state += mvs

        return num_state


class TestParamsAlt(TestParams):
    """
    self, mode, agent1type, agent2type, eps=0.1, ml1=None, ml2=None, team1="random", team2="random", nb=1000
    """
    def __init__(self, mode, agent1type, agent2type, eps=0.1, ml1=None, ml2=None, team1="random", team2="random",
                 nb=1000, player_gt_alt_weights=(1, 1, 1, 1)):
        super().__init__(mode, agent1type, agent2type, eps, ml1, ml2, team1, team2, nb)
        self.player_gt_alt_weights = player_gt_alt_weights


class GameEngineAlt(GameEngine):
    """
        Alternate GameEngine to use alternative implementations (defined here)
    """
    def __init__(self, ui_input, poke_game_type):
        super().__init__(ui_input, None, None)
        self.poke_game_type = poke_game_type

    @staticmethod
    def init_players(ge_params):
        """
        Initialize Player objects that will be used as agents to play the game.

        :param ge_params: UIParams object containing information to initialize game
        :return: List of two Player objects
        """

        players = list()
        for p, n in zip([ge_params.agent1type, ge_params.agent2type], ["p1", "p2"]):
            if p == "random":
                players.append(PlayerRandom(n))

            elif p == "human":
                players.append(PlayerHuman())

            elif p == "mdm":
                players.append(PlayerMDM(n))

            elif p == "bm":
                players.append(PlayerBM(n))

            elif p == "ml":
                network, act_f, ls = load_ml_agent(ge_params.ml1 if n == "p1" else ge_params.ml2)
                uip = ge_params
                if uip.agent1type == "ml" and uip.agent2type == "ml" and uip.ml1 == uip.ml2 and p == "p2" and uip.mode == "train":
                    # train mode, both player in ML and same NN -> share object
                    network = players[0].network
                lr = ge_params.lr if ge_params.mode == "train" else None
                players.append(PlayerRL(n, ge_params.mode, network, ls, act_f, ge_params.eps, lr))

            elif p == "gt":
                players.append(PlayerGT(n))

            elif p == "ga":
                uip = ge_params
                if n == "p1":
                    network, act_f = load_ml_agent(uip.ml1) if type(uip.ml1) == str else uip.ml1
                elif n == "p2":
                    network, act_f = load_ml_agent(uip.ml2) if type(uip.ml2) == str else uip.ml2
                players.append(PlayerGA(n, network, act_f))

            elif p == "gtalt":
                players.append(PlayerGTAlt(n, ge_params.player_gt_alt_weights))

            else:
                players.append(None)

        return players

    def test_mode(self, display: bool = False):
        """
        :param display: Indicates whether a display of the progression is required
        :return: Victory rate of player 1
        """

        pars = self.ge_params
        players = self.init_players(pars)
        p1_victories = int()

        for i in range(pars.nb):
            game = self.poke_game_type([self.get_team_specs(pars.team1), self.get_team_specs(pars.team2)])
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


class PlayerGTAlt(PlayerGT):
    """
        Alternate PlayerGT agent that uses parameter specified weights for payoffs computation
    """
    def __init__(self, role: str, weights: tuple[int, int, int, int, int, int]):
        super().__init__(role)
        self.weights = weights

    def compute_player_payoff(self, state: PokeGame.GameStruct, player: str):
        p1_hp, p2_hp = sum([p.cur_hp for p in state.team1]), sum([p.cur_hp for p in state.team2])
        p1_max, p2_max = sum([p.hp for p in state.team1]), sum([p.hp for p in state.team2])
        p1_alive, p2_alive = sum([p.is_alive() for p in state.team1]), sum([p.is_alive() for p in state.team2])

        w = self.weights
        payoff = (-1) ** (player == "p2") * ((w[0] * p1_hp / p1_max) + (w[1] * p1_alive / len(state.team1))) + \
                 (-1) ** (player == "p1") * ((w[2] * p2_hp / p2_max) + (w[3] * p2_alive / len(state.team2)))

        return payoff
