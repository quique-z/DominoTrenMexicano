# This player considers all possible moves and weighs them using a heuristic function. It then chooses the highest ranking move.
from ai.ProbabilityMapList import ProbabilityMapList
from players.SimpleCPUPlayer import SimpleCPUPlayer
from ai.Heuristic import Heuristic


class HeuristicAIPlayer(SimpleCPUPlayer):
    def __init__(self, index, names, highest_double, n_chips_per_player):
        super().__init__(index, names[index])
        self.probability_map_list = ProbabilityMapList(names, highest_double, n_chips_per_player)
        self.heuristic = Heuristic()

    def init_round(self, chips, double_to_skip):
        super().init_round(chips)
        self.probability_map_list.init_round(double_to_skip)
