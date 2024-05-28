# Very basic player. Follows the rules but plays a random move. Mostly for debugging purposes, or for testing an AI against it.
import logging
from typing import List, Self, Optional

from numpy.random import permutation

from game import Board
from game.Chip import Chip
from game.ChipNode import ChipNode
from game.PlayableChipNode import PlayableChipNode
from players.CPUPlayer import CPUPlayer


class RandomCPUPlayer(CPUPlayer):

    def play(self, board: Board, players: List[Self]) -> PlayableChipNode:
        return self.play_forced(board) if board.is_forced() else self.play_any(board)

    def play_forced(self, board: Board) -> PlayableChipNode:
        for number in permutation(list(board.get_forced_numbers())):
            for chip in permutation(list(self.chips)):
                if number in chip:
                    logging.info(f"{self.name} plays: {chip}")
                    cn = ChipNode(chip, number)
                    return PlayableChipNode(cn, board.get_forced_row_index())

    def play_any(self, board: Board) -> PlayableChipNode:
        for row in permutation(board.get_rows()):
            if row.get_index() == self.index or (row.has_train() and not board.has_train(self.index)):
                for open_number in permutation(row.get_open_positions()):
                    for chip in permutation(list(self.chips)):
                        if open_number in chip:
                            cn = ChipNode(chip, open_number)
                            logging.info(f"{self.name} plays {chip}")

                            if chip.is_double():
                                if new_chip := self.follow_up_double(chip, open_number):
                                    cn.add_next_node(ChipNode(new_chip, open_number))

                            return PlayableChipNode(cn, row.get_index())

    def follow_up_double(self, original_chip: Chip, open_number: int) -> Optional[Chip]:
        for new_chip in permutation(list(self.chips)):
            if open_number in new_chip and original_chip != new_chip:
                logging.info(f"{self.name} follows the double with: {new_chip}")
                return new_chip
        return None
