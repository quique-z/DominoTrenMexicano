# Very basic player. Follows the rules but plays a random move. Mostly for debugging purposes, or for testing an AI against it.
import logging
from typing import List, Self

from numpy.random import permutation

from game import Board
from game.ChipNode import ChipNode
from game.PlayableChipNode import PlayableChipNode
from players.CPUPlayer import CPUPlayer


class RandomCPUPlayer(CPUPlayer):

    def play(self, board: Board, players: List[Self]) -> PlayableChipNode:
        if board.is_forced():
            return self.play_forced(board)
        else:
            return self.play_any(board)

    def play_any(self, board: Board) -> PlayableChipNode:
        for row in permutation(board.get_rows()):
            if row.get_index() == self.index or (row.has_train() and not board.has_train(self.index)):
                for open_number in permutation(row.get_open_positions()):
                    for chip in permutation(list(self.chips)):
                        if open_number in chip:
                            cn = ChipNode(chip, open_number)
                            logging.info(self.name, " plays :", chip)
                            if chip.is_double():
                                for new_chip in permutation(list(self.chips)):
                                    if open_number in new_chip and chip != new_chip:
                                        logging.info(self.name, " follows the double with :", new_chip)
                                        cn.add_next_node(ChipNode(new_chip, open_number))
                                        break
                            return PlayableChipNode(cn, row.get_index())

    def play_forced(self, board: Board) -> PlayableChipNode:
        for number in board.get_forced_numbers():
            for chip in permutation(list(self.chips)):
                if number in chip:
                    logging.info("%s plays :%s" % (self.name, chip))
                    cn = ChipNode(chip, number)
                    return PlayableChipNode(cn, board.get_forced_row_index())

    def __str__(self) -> str:
        s = ["Name: %s" % self.name,
             " Round points: %s" % self.get_current_points(),
             " Total points: %s" % self.total_points,
             " Chips: "]
        for i in self.chips:
            s.append(i.__str__())
            s.append(" ")
        return ''.join(s)
