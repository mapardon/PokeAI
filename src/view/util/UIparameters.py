

class AbstractUIParams:
    """ Contain the parameters gathered from menus and forwarded to controllers. Bound to behave as a struct so
    members will be accessed directly. """

    def __init__(self):
        self.mode = str()
        self.eps = 0.1
        self.agent1type = None
        self.agent2type = None
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
        self.nb = 1000

    def set_nb(self, val):
        self.nb = abs(int(val))


class TrainUIParams(AbstractUIParams):
    def __init__(self):
        super().__init__()
        # train agent
        self.agent1type = "ml"
        self.agent2type = "ml"
        self.nb = 1000
        self.mvsel = "eps-greedy"
        self.lr = 0.3

    def set_nb(self, val):
        self.nb = abs(int(val))


class ManageUIParams:
    def __init__(self):
        # create new agent
        self.mode = str()
        self.newfname = None
        self.newmltype = None
        self.newls = None  # ls will be fixed with a NN
        self.newshape = None
        self.newinit = None
        self.newactf = None
        self.newlamb = None


class FightUIParams(AbstractUIParams):
    def __init__(self):
        super().__init__()
