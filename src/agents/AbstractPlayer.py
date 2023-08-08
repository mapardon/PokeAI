from abc import ABC, abstractmethod


class AbstractPlayer(ABC):
    def __init__(self, role):
        """ role: "p1" or "p2" depending on the role (player1 or player2) """
        self.role = role

    @abstractmethod
    def make_move(self, game):
        pass
