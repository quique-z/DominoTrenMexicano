# Baseline class for CPU Players. Handles dealing with chips and some other tasks, but game logic is left to concrete implementations.
import logging
from typing import List, Set

from game import Chip, Board
from players.Player import Player


class CPUPlayer(Player):
    def __init__(self, index: int, name: str = None) -> None:
        super().__init__(index, name)
        self.chips = None
        self.say_one = True
        self.remove_train = True

    def remove_chips(self, chips: Set[Chip]) -> None:
        for chip in chips:
            self.chips.remove(chip)

    def can_play(self, board: Board) -> bool:
        if not super().can_play(board):
            return False
        if board.is_forced():
            return self.can_play_forced(board)
        else:
            return self.can_play_any(board)

    def can_play_forced(self, board: Board) -> bool:
        can_play = self.can_play_numbers(board.get_forced_numbers())
        if can_play:
            logging.info("%s is forced and has a chip to play" % self.name)
        else:
            logging.info("%s is forced and doesn't have a chip to play" % self.name)
        return can_play

    def can_play_any(self, board: Board) -> bool:
        numbers = set()
        for row in board.get_rows():
            if row.get_index() == self.index or (row.has_train() and not board.has_train(self.index)):
                numbers.update(row.get_open_positions())
        return self.can_play_numbers(numbers)

    def can_play_numbers(self, numbers: Set[int]) -> bool:
        available_numbers = set()
        for chip in self.chips:
            available_numbers.update(chip.get_sides())
        return bool(numbers.intersection(available_numbers))

    def get_current_points(self) -> int:
        total = 0
        for chip in self.chips:
            total += chip.get_value()
        return total

    def get_total_points(self) -> int:
        return self.total_points

    def add_up_points(self) -> None:
        self.total_points += self.get_current_points()

    def will_say_one(self) -> bool:
        return self.say_one

    def will_remove_train(self) -> bool:
        return self.remove_train

    def has_chips(self, chips: List[Chip]) -> bool:
        for chip in chips:
            if chip not in self.chips:
                return False
        return True

    def __str__(self) -> str:
        s = ["Name: %s" % self.name,
             " Round points: %s" % self.get_current_points(),
             " Total points: %s" % self.total_points,
             " Chips: "]
        for i in self.chips:
            s.append(i.__str__())
            s.append(" ")
        return ''.join(s)
