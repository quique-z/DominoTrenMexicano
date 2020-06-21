from players.BasicPlayer import Player
from ai.SequenceGeneration import *


class SimpleAIPlayer(Player):

    def __init__(self, index):
        super().__init__(index)
        self.chip_node_list = None
        self.needs_to_update_sequence = True
        self.heuristic_value_per_chip = 7
        self.front_loaded_index = 0.99

    def play_forced(self, board):
        if board.get_forced_row() == self.index:
            self.play_forced_self(board)
        else:
            self.play_forced_elsewhere(board)

    def play_forced_elsewhere(self, board):
        best_chip = None
        best_number = None
        max_value = -math.inf
        chips_not_in_sequence = list(set(self.chips) - set(self.chip_node_list.get_chipset()))

        for chip in chips_not_in_sequence:
            for number in board.get_forced_numbers():
                if chip.__contains__(number) and chip.get_value() > max_value:
                    best_chip = chip
                    best_number = number
                    max_value = chip.get_value()

        if best_chip is None:
            min_loss = math.inf
            open_positions = board.get_row(self.index).get_open_positions()
            for chip in self.chips:
                for number in board.get_forced_numbers():
                    if chip.__contains__(number):
                        new_chips = self.chips.copy()
                        new_chips.remove(chip)
                        new_sequence = generate_sequence(
                            open_positions, new_chips, self.heuristic_value_per_chip, self.front_loaded_index)
                        new_excess_value = self.get_current_points() - chip.get_value()
                        if new_sequence is not None:
                            new_excess_value -= new_sequence.get_value()
                        if new_excess_value < min_loss:
                            min_loss = new_excess_value
                            best_chip = chip
                            best_number = number

        board.play_chip(best_chip, best_number, board.get_forced_row())
        board.remove_forced(best_number)
        self.chips.remove(best_chip)

    def play_forced_self(self, board):
        if self.chip_node_list.has_number_to_play_immediately(board.get_forced_numbers()):
            chip_node = self.chip_node_list.get_best_numbered_chip_to_play(board.get_forced_numbers())
            board.play_chip(chip_node.get_chip(), chip_node.get_side_to_play(), self.index)
            board.remove_forced(chip_node.get_side_to_play())
            self.chips.remove(chip_node.get_chip())
        else:
            min_loss = math.inf
            open_positions = board.get_row(self.index).get_open_positions()
            for chip in self.chips:
                for number in board.get_forced_numbers():
                    if chip.__contains__(number):
                        new_chips = self.chips.copy()
                        new_chips.remove(chip)
                        new_open_positions = open_positions.copy()
                        new_open_positions.remove(number)
                        new_open_positions.append(chip.get_other_side(number))
                        new_sequence = generate_sequence(
                            new_open_positions, new_chips, self.heuristic_value_per_chip, self.front_loaded_index)
                        new_excess_value = self.get_current_points() - chip.get_value()
                        if new_sequence is not None:
                            new_excess_value -= new_sequence.get_value()
                        if new_excess_value < min_loss:
                            min_loss = new_excess_value
                            best_chip = chip
                            best_number = number

            board.play_chip(best_chip, best_number, board.get_forced_row())
            board.remove_forced(best_number)
            self.chips.remove(best_chip)

    def play_first(self, board):
        forced_counter = 0
        while self.chip_node_list.has_chip_to_play():
            cn = self.chip_node_list.get_best_chip_to_play()
            chips = cn.get_next_piece()
            for chip in chips:
                print("%s juega ficha %s" %(self.name, chip.__str__()))
                if chip.is_double() and len(chips) == 1:
                    forced_counter += 1
                    board.set_forced(self.index, chip.get_side_a())
                board.play_chip(chip, cn.get_side_to_play(), self.index)
                self.chips.remove(chip)

        if forced_counter > 0:
            for i in range(forced_counter):
                if board.can_draw():
                    chip = board.draw()
                    self.chips.append(chip)
                    print("%s roba ficha %s" % (self.name, chip.__str__()))
                    for number in board.get_forced_numbers():
                        if chip.__contains__(number):
                            board.play_chip(chip, number, self.index)
                            board.remove_forced(number)
                            self.chips.remove(chip)
                            forced_counter -= 1
                            break
            if forced_counter > 0:
                board.set_train(self.index)

    def play_any(self, board):
        super().play_any(board)

    def update_sequence(self, board):
        self.needs_to_update_sequence = False
        self.chip_node_list = generate_sequence(
            board.get_row(self.index).get_open_positions(),
            self.chips,
            self.heuristic_value_per_chip,
            self.front_loaded_index)

    def play(self, board):
        print(self.name + " juega: ")
        if self.needs_to_update_sequence or board.get_forced_row() == self.index:
            self.update_sequence(board)
        if board.is_forced():
            self.play_forced(board)
            self.needs_to_update_sequence = True
        elif board.get_row(self.index).can_play_many() and not self.can_play_cheaply_elsewhere(board):
            self.play_first(board)
        else:
            self.play_any(board)
            self.needs_to_update_sequence = True

    def can_play_cheaply_elsewhere(self, board):
        chips_not_in_sequence = list(set(self.chips) - set(self.chip_node_list.get_chipset()))
        for chip in chips_not_in_sequence:
            if not chip.is_double():
                for row in board.get_rows():
                    if row.get_index() != self.index and row.has_train():
                        for open_position in row.get_open_positions():
                            if chip.__contains__(open_position):
                                return True

        my_open_positions = board.get_row(self.index).get_open_positions()
        current_excess_value = self.get_current_points() - self.chip_node_list.get_value()

        for row in board.get_rows():
            if row.get_index() != self.index and row.has_train():
                for number in row.get_open_positions():
                    for chip in self.chip_node_list.get_chipset():
                        if chip.__contains__(number):
                            new_chips = self.chips.copy()
                            new_chips.remove(chip)
                            new_sequence = generate_sequence(
                                my_open_positions, new_chips, self.heuristic_value_per_chip, self.front_loaded_index)
                            new_excess_value = self.get_current_points() - chip.get_value()
                            if new_sequence is not None:
                                new_excess_value -= new_sequence.get_value()
                            if new_excess_value <= current_excess_value:
                                return True

        return False

    def init_round(self, chips):
        self.needs_to_update_sequence = True
        super().init_round(chips)

    def add_chip(self, chip):
        self.needs_to_update_sequence = True
        super().add_chip(chip)