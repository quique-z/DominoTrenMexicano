# Baseline abstract class for a Player. Both Human and CPU players inherit from here.
import logging
from typing import List, Self

from game import Chip, Board, ChipNodeList


class Player:

    def __init__(self, index: int, name: str = None) -> None:
        self.name = name
        if not name:
            self.name = index.__str__()
        self.chips = []
        self.index = index
        self.has_won = False
        self.total_points = 0
        self.eligible_to_win = False

    def init_round(self, chips: List[Chip] = None, double_to_skip: int = None) -> None:
        self.has_won = False
        self.eligible_to_win = False
        self.chips = chips

    def init_turn(self, board: Board) -> None:
        pass

    def end_turn(self, board: Board) -> None:
        if not self.chips:
            if board.get_forced_culprit_index() == self.index:
                self.eligible_to_win = True
                logging.info(
                    "%s is out of chips but the board is forced because of them, so they can't win yet." % self.name)
            else:
                self.has_won = True
                logging.info("%s wins this round!" % self.name)

    def add_chip(self, chip: Chip) -> None:
        self.chips.append(chip)
        logging.info("%s draws: %s" % (self.name, chip.__str__()))

    def remove_chip(self, chip: Chip) -> None:
        raise NotImplementedError

    def can_play(self, board: Board) -> bool:
        return NotImplemented

    def play(self, board: Board, players: List[Self]) -> [ChipNodeList, int]:
        return NotImplemented

    def get_current_points(self) -> int:
        return NotImplemented

    def get_total_points(self) -> int:
        return NotImplemented

    def add_up_points(self) -> None:
        pass

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
        pass
