

class AbstractParams:
    """ Contain the parameters gathered from menus and forwarded to controllers. Bound to behave as a struct so
    members will be accessed directly. """

    def __init__(self, mode, agent1type, agent2type, eps=0.1, ml1=None, ml2=None, team1="random", team2="random"):
        """
            :param ml1/ml2: Either the name of the network in the database or a tuple with the network and act_f/ls
        """
        self.mode = mode
        self.agent1type = agent1type
        self.agent2type = agent2type
        self.eps = eps
        self.ml1 = ml1
        self.ml2 = ml2
        self.team1 = team1
        self.team2 = team2

    def set_eps(self, val):
        test = round(float(val), 2)
        if 0 <= test <= 1:
            self.eps = test
        else:
            raise ValueError


class TestParams(AbstractParams):
    def __init__(self, mode, agent1type, agent2type, eps=0.1, ml1=None, ml2=None, team1="random", team2="random",
                 nb=1000):
        super().__init__(mode, agent1type, agent2type, eps, ml1, ml2, team1, team2)
        self.nb = nb

    def set_nb(self, val):
        self.nb = abs(int(val))


class TrainParams(AbstractParams):
    def __init__(self, mode, lr, agent1type='ml', agent2type='ml', eps=0.1, ml1=None, ml2=None, team1="random",
                 team2="random", nb=1000):
        super().__init__(mode, agent1type, agent2type, eps, ml1, ml2, team1, team2)
        # train agent
        self.agent1type = agent1type
        self.agent2type = agent2type
        self.nb = nb
        self.lr = lr

    def set_nb(self, val):
        self.nb = abs(int(val))


class FightParams(AbstractParams):
    def __init__(self, mode, agent1type, agent2type, eps=0.1, ml1=None, ml2=None, team1="random", team2="random"):
        super().__init__(mode, agent1type, agent2type, eps, ml1, ml2, team1, team2)
