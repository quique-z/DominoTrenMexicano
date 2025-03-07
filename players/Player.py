# Baseline abstract class for a Player. Both Human and CPU players inherit from here.
import logging
from typing import List, Self, Set

from game import Chip, Board, PlayableChipNode


class Player:

    def __init__(self, index: int, highest_double: int, n_players: int, name: str = None) -> None:
        self.name = name if name else str(index)
        self.eligible_to_win = False
        self.total_points = 0
        self.has_won = False
        self.index = index
        self.chips = set()

    def init_round(self, chips: Set[Chip] = None, double_to_skip: int = None) -> None:
        self.has_won = False
        self.eligible_to_win = False
        self.chips = chips

    def init_turn(self, board: Board) -> None:
        pass

    def end_turn(self, board: Board) -> None:
        if self.chips:
            return

        if board.get_forced_culprit_index() == self.index:
            self.eligible_to_win = True
            logging.info(f"{self.name} is out of chips but the board is forced because of them, so they can't win yet.")
        else:
            self.has_won = True
            logging.info(f"{self.name} wins this round!")

    def add_chip(self, chip: Chip) -> None:
        raise NotImplemented

    def remove_chips(self, chips: Set[Chip]) -> None:
        raise NotImplementedError

    def can_play(self, board: Board) -> bool:
        if not self.chips:
            logging.info(f"{self.name} doesn't have chips, but it is their turn.")
            return False
        return True

    def play(self, board: Board, players: List[Self]) -> PlayableChipNode:
        return NotImplemented

    def get_current_points(self) -> int:
        return NotImplemented

    def get_total_points(self) -> int:
        return self.total_points

    def add_up_points(self) -> None:
        raise NotImplemented

    def get_name(self) -> str:
        return self.name

    def is_round_winner(self) -> bool:
        return self.has_won

    def declare_as_round_winner(self) -> None:
        self.has_won = True

    def is_eligible_to_win(self) -> bool:
        return self.eligible_to_win

    def set_name(self, name: str) -> None:
        self.name = name

    def get_index(self) -> int:
        return self.index

    def get_chip_count(self) -> int:
        return len(self.chips)

    def will_say_one(self) -> bool:
        return NotImplemented

    def will_remove_train(self) -> bool:
        return NotImplemented

    def has_chips(self, chips) -> bool:
        return NotImplemented

    def get_chips(self) -> Set[Chip]:
        return NotImplemented
