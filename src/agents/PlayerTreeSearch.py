import random

from src.agents.AbstractPlayer import AbstractPlayer
from src.game.PokeGame import PokeGame


def evaluation_hp_based(player, game):
    """ Returns an evaluation of the provided state (GameStruct) for the minimax algorithm. This evaluation is based
     on the hp percentage of both teams."""
    if game.is_end_state(game.game_state):
        res = float("inf") if game.first_player_won() and player == "1" or not game.first_player_won() and player == "2" else float("-inf")
    else:
        team2_hp = sum([p.cur_hp for p in game.game_state.team2])
        team1_hp = sum([p.cur_hp for p in game.game_state.team1])
        res = (-1) ** (player == "p1") * (team1_hp - team2_hp)
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
        if self.max_depth:
            best_move = self.tree_search(game, game.get_player1_view() if self.role == "p1" else game.get_player2_view(), self.max_depth - 1)[1]

        if best_move is None:
            # all moves lead to defeat or depth == 0
            best_move = random.choice(game.get_moves_from_state(self.role, game.get_player1_view() if self.role == "1" else game.get_player2_view()))

        return best_move

    def tree_search(self, game, state, cur_depth):
        best_eval = float("-inf")
        best_move = None

        # all pairs of actions for player1 and player2
        for m1 in game.get_moves_from_state("p1", state):
            for m2 in game.get_moves_from_state("p2", state):
                if cur_depth == 0:
                    move_eval = self.evaluation_mode(self.role, game.apply_player_moves(state, m1, m2)[0])
                    move = m1 if self.role == "p1" else m2
                else:
                    move_eval, move = self.tree_search(game, game.apply_player_moves(state, m1, m2)[0], cur_depth-1)

                if move_eval > best_eval:
                    best_eval = move_eval
                    best_move = move

        return best_eval, best_move


if __name__ == "__main__":
    team_specs_for_game = [[(("p1", "FIRE", 100, 100, 100, 100, 100, 100),
                             (("light_psychic", "PSYCHIC", 50), ("heavy_fire", "FIRE", 100))),
                            (("p2", "ELECTRIC", 100, 80, 100, 80, 100, 100),
                             (("light_grass", "GRASS", 50), ("heavy_electric", "ELECTRIC", 100)))],
                           [(("d1", "WATER", 100, 100, 100, 100, 100, 100),
                             (("light_steel", "STEEL", 50), ("heavy_water", "WATER", 100))),
                            (("d2", "DRAGON", 100, 80, 100, 80, 100, 100),
                             (("light_bug", "BUG", 50), ("heavy_dragon", "DRAGON", 100)))]]

    game = PokeGame(team_specs_for_game)

    agent1 = PlayerTreeSearch("p1", 1, evaluation_hp_based)
    agent2 = PlayerTreeSearch("p2", 1, evaluation_hp_based)
    print(agent1.make_move(game))
    print(agent2.make_move(game))
