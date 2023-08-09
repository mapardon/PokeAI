from abc import ABC, abstractmethod

from src.game.PokeGame import PokeGame


class AbstractPlayer(ABC):
    def __init__(self, role: str):
        """ role: "p1" or "p2" depending on the role (player1 or player2) """
        self.role = role

    @abstractmethod
    def make_move(self, game: PokeGame):
        pass
