# This player considers all possible moves and weighs them using a heuristic function. It then chooses the highest ranking move.

from players.SimpleCPUPlayer import SimpleCPUPlayer
from ai.Heuristic import Heuristic


class HeuristicAIPlayer(SimpleCPUPlayer):
    def __init__(self, index, name=None):
        super().__init__(index, name)
        self.probability_map_list = None
        self.heuristic = Heuristic()

    def set_probability_map_list(self, pml):
        self.probability_map_list = pml

