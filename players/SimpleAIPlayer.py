# Representation of what an average human player may play like. An average human is probably a bit better,
# but this should be close enough for testing and training purposes

from players.BasicPlayer import Player
from ai.SequenceGeneration import *


class SimpleAIPlayer(Player):
    # TODO: Danger of someone else winning is not taken into consideration yet.
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
        chips_not_in_sequence = list(set(self.chips) - set(self.chip_node_list.get_chipset()))

        max_value = -math.inf
        for chip in chips_not_in_sequence:
            for number in board.get_forced_numbers():
                if chip.__contains__(number) and chip.get_value() > max_value:
                    best_chip = chip
                    best_number = number
                    max_value = chip.get_value()

        if best_chip is None:
            min_points_lost = math.inf
            self.needs_to_update_sequence = True
            for chip in self.chip_node_list.get_chipset():
                for number in board.get_forced_numbers():
                    if chip.__contains__(number):
                        new_chips = self.chips.copy()
                        new_chips.remove(chip)
                        new_sequence = generate_sequence(board.get_row(self.index).get_open_positions(), new_chips,
                                                         self.heuristic_value_per_chip, self.front_loaded_index)
                        if new_sequence is not None:
                            points_lost = self.chip_node_list.get_chipset_weighted_value() - new_sequence.get_value() - chip.get_value()
                        if points_lost < min_points_lost:
                            min_points_lost = points_lost
                            best_chip = chip
                            best_number = number

        board.play_chip(best_chip, best_number, board.get_forced_row())
        board.remove_forced(best_number)
        self.chips.remove(best_chip)

    def play_forced_self(self, board):
        if self.chip_node_list.has_number_to_play_immediately(board.get_forced_numbers()):
            chip_node = self.chip_node_list.get_best_numbered_chip_to_play(board.get_forced_numbers())
            board.play_chip(chip_node.get_chip(), chip_node.get_chip_side_to_play(), self.index)
            board.remove_forced(chip_node.get_chip_side_to_play())
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
                            new_excess_value -= new_sequence.get_chain_value()
                        if new_excess_value < min_loss:
                            min_loss = new_excess_value
                            best_chip = chip
                            best_number = number

            board.play_chip(best_chip, best_number, board.get_forced_row())
            if board.get_forced_row() == self.index and len(board.get_forced_numbers()) == 1:
                board.remove_train(self.index)
            board.remove_forced(best_number)
            self.chips.remove(best_chip)

    def play_first(self, board):
        forced_counter = 0
        while self.chip_node_list.has_chip_to_play():
            cn = self.chip_node_list.get_best_chip_to_play()
            chips = cn.get_next_piece()
            for chip in chips:
                print("%s juega ficha %s" % (self.name, chip.__str__()))
                if chip.is_double() and len(chips) == 1:
                    forced_counter += 1
                    board.set_forced(self.index, chip.get_side_a())
                board.play_chip(chip, cn.get_chip_side_to_play(), self.index)
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
        else:
            board.remove_train(self.index)

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
            print(self.name, " updating sequence")
            self.update_sequence(board)

        if board.is_forced():
            print(self.name, " am forced")
            self.play_forced(board)
            self.needs_to_update_sequence = True
            self.end_turn(board)
            return

        if self.chip_node_list.get_chipset_weighted_value() == self.get_current_points() and board.get_row(self.index).can_play_many():
            self.play_first(board)
            self.end_turn(board)
            return

        can_play_elsewhere = not board.has_train(self.index)
        if can_play_elsewhere:
            can_play_elsewhere = self.can_play_cheaply_elsewhere(board)

        if can_play_elsewhere:
            print(self.name, " playing elsewhere")
            self.play_elsewhere(board)
            self.needs_to_update_sequence = True
        elif board.get_row(self.index).can_play_many():
            print(self.name, " playing many")
            self.play_first(board)
        else:
            print(self.name, " playing self, only one")
            self.play_any(board)
        self.end_turn(board)

    def play_any(self, board):
        if self.chip_node_list.has_chip_to_play():
            chip = self.chip_node_list.get_best_chip_to_play()
            side_to_play = chip.get_chip_side_to_play()
            self.play_chips(board, chip.get_next_piece(), side_to_play, self.index)

            if chip.is_chip_double() and len(chip.get_next_piece()) == 1:
                if board.can_draw():
                    drawn_chip = board.draw()
                    self.add_chip(drawn_chip)
                    if drawn_chip.__contains__(side_to_play):
                        self.play_chips(board, [drawn_chip], side_to_play, self.index)
                    else:
                        board.set_train(self.index)
                        board.set_forced(self.index, side_to_play)
                else:
                    board.set_train(self.index)
                    board.set_forced(self.index, chip.get_chip_side_to_play())
            if board.get_forced_row() != self.index:
                board.remove_train(self.index)
        else:
            super().play_any(board)

    def play_elsewhere(self, board):
        max_value = -math.inf
        best_chip = None
        best_side = None
        best_row = None
        doubles_to_resolve = []
        rows_where_doubles_go = []
        chips_not_in_sequence = list(set(self.chips) - set(self.chip_node_list.get_chipset()))

        for chip in chips_not_in_sequence:
            for row in board.get_rows():
                if row.get_index() != self.index and row.has_train():
                    for open_position in row.get_open_positions():
                        if chip.__contains__(open_position):
                            if chip.is_double():
                                doubles_to_resolve.append(chip)
                                rows_where_doubles_go.append(row.get_index())
                            elif chip.get_value() > max_value:
                                max_value = chip.get_value()
                                best_chip = [chip]
                                best_side = open_position
                                best_row = row.get_index()

        for i in range(len(doubles_to_resolve)):
            number = doubles_to_resolve[i].get_side_a()
            value = doubles_to_resolve[i].get_value()
            for chip in chips_not_in_sequence:
                if chip.__contains__(number) and not chip.is_double() \
                        and value + chip.get_value() + self.heuristic_value_per_chip > max_value:
                    max_value = value + chip.get_value()
                    best_chip = [doubles_to_resolve[i], chip]
                    best_side = number
                    best_row = rows_where_doubles_go[i]

        if best_chip is None:
            my_open_positions = board.get_row(self.index).get_open_positions()
            doubles_to_resolve = []
            rows_where_doubles_go = []

            for row in board.get_rows():
                if row.get_index() != self.index and row.has_train():
                    for number in row.get_open_positions():
                        for chip in self.chips:
                            if chip.__contains__(number):
                                if chip.is_double():
                                    doubles_to_resolve.append(chip)
                                    rows_where_doubles_go.append(row.get_index())
                                else:
                                    new_chips = self.chips.copy()
                                    new_chips.remove(chip)
                                    new_sequence = generate_sequence(
                                        my_open_positions, new_chips, self.heuristic_value_per_chip,
                                        self.front_loaded_index)
                                    if new_sequence is not None and new_sequence.get_value() + chip.get_value() >= self.chip_node_list.get_value() and chip.get_value() > max_value:
                                        best_chip = [chip]
                                        best_side = number
                                        best_row = row.get_index()
                                        max_value = chip.get_value()

            for i in range(len(doubles_to_resolve)):
                double = doubles_to_resolve[i]
                number = double.get_side_a()
                row = rows_where_doubles_go[i]
                for chip in self.chips:
                    if chip.__contains__(number) and not chip.is_double():
                        new_chips = self.chips.copy()
                        new_chips.remove(chip)
                        new_chips.remove(double)
                        new_sequence = generate_sequence(my_open_positions, new_chips, self.heuristic_value_per_chip, self.front_loaded_index)

                        if new_sequence is not None \
                                and new_sequence.get_value() + chip.get_value() + double.get_value() >= \
                                self.chip_node_list.get_value() \
                                and chip.get_value() + double.get_value() + self.heuristic_value_per_chip > max_value:
                            best_chip = [double, chip]
                            best_side = number
                            best_row = row
                            max_value = double.get_value() + chip.get_value() + self.heuristic_value_per_chip

        self.play_chips(board, best_chip, best_side, best_row)

    def can_play_cheaply_elsewhere(self, board):
        # TODO: Some high value doubles might be worth playing even if you don't have a follow up. Current
        #  implementation only checks if there is a high-value double without more consideration.
        chips_not_in_sequence = list(set(self.chips) - set(self.chip_node_list.get_chipset()))
        for chip in chips_not_in_sequence:
            if not (chip.is_double() and chip.get_value() >= 20):
                for row in board.get_rows():
                    if row.get_index() != self.index and row.has_train():
                        for open_position in row.get_open_positions():
                            if chip.__contains__(open_position):
                                return True

        my_open_positions = board.get_row(self.index).get_open_positions()

        for row in board.get_rows():
            if row.get_index() != self.index and row.has_train():
                for number in row.get_open_positions():
                    for chip in self.chip_node_list.get_chipset():
                        if chip.__contains__(number):
                            new_chips = self.chips.copy()
                            new_chips.remove(chip)
                            new_sequence = generate_sequence(
                                my_open_positions, new_chips, self.heuristic_value_per_chip, self.front_loaded_index)
                            if new_sequence is not None and new_sequence.get_chipset_weighted_value() + chip.get_value() >= self.chip_node_list.get_chipset_weighted_value():
                                return True

        return False

    def play_chips(self, board, chips, side, row):
        for chip in chips:
            board.play_chip(chip, side, row)
            self.chips.remove(chip)
            print(chip)

    def init_round(self, chips):
        self.needs_to_update_sequence = True
        super().init_round(chips)

    def add_chip(self, chip):
        self.needs_to_update_sequence = True
        super().add_chip(chip)
