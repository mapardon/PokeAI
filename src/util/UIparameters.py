

class AbstractUIParams:
    """ Contain the parameters gathered from UI. Bound to behave as a C struct so members will
     be accessed directly. """

    def __init__(self):
        self.mode = str()
        self.eps = 0.1
        self.ml1 = None
        self.ml2 = None
        self.team1 = "random"
        self.team2 = "random"

    def set_eps(self, val):
        test = round(float(val), 2)
        if 0 <= test <= 1:
            self.eps = test
        else:
            raise ValueError


class TestUIParams(AbstractUIParams):
    def __init__(self):
        super().__init__()
        self.agent1 = None
        self.agent2 = None
        self.nb = 1000
        self.minimax1 = 1
        self.minimax2 = 1

    def set_nb(self, val):
        self.nb = abs(int(val))


class TrainUIParams(AbstractUIParams):
    def __init__(self):
        super().__init__()
        self.newfname = None
        self.newls = None
        self.newshape = None
        self.newinit = None
        self.newactf = None
        self.newlamb = None
        self.nb = 1000
        self.mvsel = "eps-greedy"
        self.lr = 0.3

    def set_nb(self, val):
        self.nb = abs(int(val))


class FightUIParams(AbstractUIParams):
    def __init__(self):
        super().__init__()
        self.player1 = None
        self.player2 = None
        self.minimax1 = 1
        self.minimax2 = 1
