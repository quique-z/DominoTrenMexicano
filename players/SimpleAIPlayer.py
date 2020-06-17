from players.BasicPlayer import Player
from ai.SequenceGeneration import *


class SimpleAIPlayer(Player):

    def __init__(self, index):
        super().__init__(index)
        self.chip_sequence = None
        self.heuristic_value_per_chip = 12.55

    def play_forced(self, board):
        if board.get_forced_row() == self.index:
            super().play_forced(board)
            return

        best_chip = None
        best_number = None
        chips_not_in_sequence = []

        if self.chip_sequence is None:
            chips_not_in_sequence = self.chips
        else:
            for chip in self.chips:
                if not self.chip_sequence.__contains__(chip):
                    chips_not_in_sequence.append(chip)

        max_value = -math.inf
        for chip in chips_not_in_sequence:
            for number in board.get_forced_numbers():
                if chip.__contains__(number) and chip.get_value() > max_value:
                    best_chip = chip
                    best_number = number
                    max_value = chip.get_value()

        if best_chip is None:
            min_loss = math.inf
            open_positions = board.get_row(self.index).get_open_positions()
            current_value = self.chip_sequence.get_value()
            for chip in self.chip_sequence.get_chipset():
                for number in board.get_forced_numbers():
                    if chip.__contains__(number):
                        new_chips = self.chips.copy()
                        new_chips.remove(chip)
                        new_sequence = generate_sequence(
                            open_positions, new_chips, self.heuristic_value_per_chip, 0)
                        loss = 0
                        if new_sequence is not None:
                            loss = current_value - new_sequence.get_value()
                        if loss < min_loss:
                            min_loss = loss
                            best_chip = chip
                            best_number = number

        board.play_chip(best_chip, best_number, board.get_forced_row())
        board.remove_forced(best_number)
        self.chips.remove(best_chip)

    def update_sequence(self, board):
        self.chip_sequence = generate_sequence(
            board.get_row(self.index).get_open_positions(), self.chips, self.heuristic_value_per_chip, 0)

    def play(self, board):
        self.update_sequence(board)
        super().play(board)
