# This player considers all possible moves and weighs them using a heuristic function. It then chooses the highest ranking move.
from typing import Set

from ai.Heuristic import Heuristic
from ai.ProbabilityTracker import ProbabilityTracker
from game.Chip import Chip
from players.SmartCPUPlayer import SmartCPUPlayer


class HeuristicCPUPlayer(SmartCPUPlayer):
    def __init__(self, index: int, highest_double: int, n_players: int, name: str = None) -> None:
        super().__init__(index, highest_double, n_players, name)
        self.highest_double = highest_double
        self.probability_tracker = None
        self.n_players = n_players

    def init_round(self, chips: Set[Chip] = None, double_to_skip: int = None) -> None:
        super().init_round(chips, double_to_skip)
        self.probability_tracker = ProbabilityTracker(chips, self.highest_double, double_to_skip, self.n_players, self.index)

    def init_turn(self, board):
        super().init_turn(board)
        # Cycles through all players starting after self.index, excluding self.index


    def add_chip(self, chip):
        super().add_chip(chip)

    def __str__(self):
        s = [super().__str__(), str(self.probability_tracker)]
        return "".join(s)
