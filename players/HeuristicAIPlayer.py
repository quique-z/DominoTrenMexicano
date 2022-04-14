# This player considers all possible moves and weighs them using a heuristic function. It then chooses the highest ranking move.

from players.SimpleCPUPlayer import SimpleCPUPlayer
from ai.Heuristic import Heuristic


class HeuristicAIPlayer(SimpleCPUPlayer):
    def __init__(self, index, probability_maps, name=None):
        super().__init__(index, name)
        self.probability_maps = probability_maps
        self.heuristic = Heuristic()

