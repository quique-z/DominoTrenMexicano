# Baseline class for CPU Players. Handles dealing with chips and some other tasks, but game logic is left to concrete implementations.
import logging
from typing import List, Set

from game import Chip, Board
from game.HiddenChip import HiddenChip
from players.Player import Player
from ui.Input import chip_input


class CPUPlayer(Player):
    def __init__(self, index: int, highest_double: int, n_players: int, name: str = None) -> None:
        super().__init__(index, highest_double, n_players, name)
        self.say_one = True
        self.remove_train = True

    def add_chip(self, chip: Chip) -> None:
        if isinstance(chip, HiddenChip):
            chip = chip_input("Enter drawn chip.", empty_allowed=False)

        self.chips.add(chip)

    def remove_chips(self, chips: Set[Chip]) -> None:
        if chips - self.chips:
            raise Exception(f"tried to remove non-existent chips: {chips - self.chips}")

        self.chips -= chips

    def can_play(self, board: Board) -> bool:
        if not super().can_play(board):
            return False

        return self.can_play_forced(board) if board.is_forced() else self.can_play_any(board)

    def can_play_forced(self, board: Board) -> bool:
        can_play = self.can_play_numbers(board.get_forced_numbers())
        logging.info(f"{self.name} is forced and {'has' if can_play else 'does not have'} a chip to play")
        return can_play

    def can_play_any(self, board: Board) -> bool:
        numbers = set()

        for row in board.get_rows():
            if row.get_index() == self.index or (row.has_train() and not board.has_train(self.index)):
                numbers.update(row.get_open_positions())

        return self.can_play_numbers(numbers)

    def can_play_numbers(self, numbers: Set[int]) -> bool:
        available_numbers = {side for chip in self.chips for side in chip.get_sides()}
        return bool(numbers & available_numbers)

    def get_current_points(self) -> int:
        return sum(chip.get_value() for chip in self.chips)

    def add_up_points(self) -> None:
        self.total_points += self.get_current_points()

    def will_say_one(self) -> bool:
        return self.say_one

    def will_remove_train(self) -> bool:
        return self.remove_train

    def has_chips(self, chips: List[Chip]) -> bool:
        return all(chip in self.chips for chip in chips)

    def get_chips(self) -> Set[Chip]:
        return self.chips

    def __str__(self) -> str:
        s = [f"{self.name}: Round points: {self.get_current_points()}, Total points: {self.total_points}, Chips: "]
        s.extend(f"{chip} " for chip in self.chips)
        return "".join(s)
