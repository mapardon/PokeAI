from src.agents.AbstractPlayer import AbstractPlayer


class PlayerMDM(AbstractPlayer):

    def __init__(self, role):
        """
        Most damaging move: select action that will deal the greatest amount of damage
        in the current state
        """

        super().__init__(role)

    def make_move(self, game):
        view = game.get_player1_view if self.role == "p1" else game.get_player2_view

        # 1. get possible moves
        options = game.get_moves_from_state(self.role, view())

        # 2. see the outcome
        res = list()
        for move in options:
            p1_move = move if self.role == "p1" else None
            p2_move = move if self.role == "p2" else None
            tmp = game.apply_player_moves(view(), p1_move, p2_move, force_dmg=False)[0]

            target_cur_hp = tmp.on_field1.cur_hp if self.role == "p2" else tmp.on_field2.cur_hp
            res.append((move, target_cur_hp))

        return min(res, key=lambda x: x[1])[0]

