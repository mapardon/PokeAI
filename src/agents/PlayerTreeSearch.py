import copy
import random

from src.agents.AbstractPlayer import AbstractPlayer
from src.game.PokeGame import PokeGame


def evaluation_hp_based(player, game, state):
    """ Returns an evaluation of the provided state (GameStruct) for the minimax algorithm. This evaluation is based
     on the hp percentage of both teams."""
    if game.is_end_state(state):
        player1_won = game.first_player_won(state)
        res = float("inf") if player1_won and player == "p1" or not player1_won and player == "p2" else float("-inf")
    else:
        team2_hp = sum([p.cur_hp for p in state.team2])
        team1_hp = sum([p.cur_hp for p in state.team1])
        res = team1_hp - team2_hp if player == "p1" else team2_hp - team1_hp
    return res


class PlayerTreeSearch(AbstractPlayer):

    def __init__(self, role, max_depth, evaluation_mode):
        """
        Minimax agent for the game

        """

        super().__init__(role)
        self.max_depth = max_depth
        self.evaluation_mode = evaluation_mode

    def make_move(self, game):

        best_move = None
        best_eval = float("-inf")

        if self.max_depth:
            view = game.get_player1_view() if self.role == "p1" else game.get_player2_view()
            for m1 in game.get_moves_from_state("p1", view):
                for m2 in game.get_moves_from_state("p2", view):
                    print("running p1 {} p2 {}".format(m1, m2))
                    move_eval = self.tree_search(game, game.apply_player_moves(copy.deepcopy(view), m1, m2)[0], self.max_depth - 1, best_eval)
                    print("best: {}".format(move_eval))
                    if move_eval > best_eval:
                        best_eval = move_eval
                        best_move = m1 if self.role == "p1" else m2

        if best_move is None:
            # all moves lead to defeat or depth == 0
            best_move = random.choice(game.get_moves_from_state(self.role, game.get_player1_view() if self.role == "p1" else game.get_player2_view()))

        return best_move

    def tree_search(self, game, state, cur_depth, cur_best):
        if cur_depth == 0 or game.is_end_state(state):
            cur_best = self.evaluation_mode(self.role, game, state)

        else:
            # all pairs of actions for player1 and player2
            for m1 in game.get_moves_from_state("p1", state):
                for m2 in game.get_moves_from_state("p2", state):
                    move_eval = self.tree_search(game, game.apply_player_moves(copy.deepcopy(state), m1, m2)[0], cur_depth - 1, cur_best)
                    cur_best = max(cur_best, move_eval)

        return cur_best


if __name__ == "__main__":
    team_specs_for_game = [[(("p1", "FIRE", 100, 100, 100, 100, 100, 100),
                             (("light_psychic", "PSYCHIC", 50), ("heavy_fire", "FIRE", 100))),
                            (("p2", "ELECTRIC", 100, 80, 100, 80, 100, 103),
                             (("light_grass", "GRASS", 50), ("heavy_electric", "ELECTRIC", 100)))],
                           [(("d1", "WATER", 100, 100, 100, 100, 100, 101),
                             (("light_steel", "STEEL", 50), ("heavy_water", "WATER", 100))),
                            (("d2", "DRAGON", 100, 80, 100, 80, 100, 102),
                             (("light_bug", "BUG", 50), ("heavy_dragon", "DRAGON", 100)))]]

    game = PokeGame(team_specs_for_game)

    if 1:
        for m1 in ["light_psychic", "heavy_fire", "switch p2"]:
            for m2 in ["light_steel", "heavy_water", "switch d2"]:
                s = game.apply_player_moves(game.get_cur_state(), m1, m2, True)[0]
                print("{} - {} : {} ({}, {})".format(m1, m2, evaluation_hp_based("p1", game, s), s.on_field1.cur_hp, s.on_field2.cur_hp))
                s = game.apply_player_moves(game.get_cur_state(), m1, m2, True)[0]
                print("{} - {} : {} ({}, {})".format(m1, m2, evaluation_hp_based("p2", game, s), s.on_field1.cur_hp, s.on_field2.cur_hp))

    if 1:
        agent1 = PlayerTreeSearch("p1", 1, evaluation_hp_based)
        agent2 = PlayerTreeSearch("p2", 1, evaluation_hp_based)
        print(agent1.make_move(game))
        print(agent2.make_move(game))
