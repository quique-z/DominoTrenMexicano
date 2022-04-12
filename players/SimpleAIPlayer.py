# Representation of what an average human player may play like. An average human is probably a bit better,
# but this should be close enough for testing and training purposes

from players.BasicPlayer import Player
from ai.SequenceGeneration import *


class SimpleAIPlayer(Player):
    # TODO: Danger of someone else winning is not taken into consideration yet.
    def __init__(self, index, name=None):
        super().__init__(index, name)
        self.chip_node_list = None
        self.needs_to_update_sequence = True
        self.heuristic_value_per_chip = 7
        self.front_loaded_index = 0.99
        self.play_chip_elsewhere_multiplier = 1.5
        self.penalty_for_playing_lone_double = 12

    def play_forced(self, board):
        if board.get_forced_row() == self.index:
            print("%s playing forced self" % self.name)
            self.play_forced_self(board)
        else:
            print("%s playing forced elsewhere" % self.name)
            self.play_forced_elsewhere(board)

    # TODO: Test using sequence.get_chipset_weighted_value() instead of regular sequence.get_chipset_value()
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

        min_points_lost = math.inf
        current_sequence_value = self.chip_node_list.get_chipset_value()

        if best_chip is not None:
            min_points_lost = -best_chip.get_value()

        for chip in self.chip_node_list.get_chipset():
            for number in board.get_forced_numbers():
                if chip.__contains__(number):
                    new_chips = self.chips.copy()
                    new_chips.remove(chip)
                    new_sequence = generate_sequence(board.get_row(self.index).get_open_positions(), new_chips,
                                                     self.heuristic_value_per_chip, self.front_loaded_index)

                    if new_sequence is None:
                        points_lost = current_sequence_value - chip.get_value()
                    else:
                        points_lost = current_sequence_value - new_sequence.get_chipset_value() - chip.get_value()

                    if points_lost < min_points_lost or (points_lost == min_points_lost and chip.get_value() > best_chip.get_value()):
                        self.needs_to_update_sequence = True
                        min_points_lost = points_lost
                        best_number = number
                        best_chip = chip

        board.play_chip(best_chip, best_number, board.get_forced_row())
        board.remove_forced(best_number)
        self.chips.remove(best_chip)

    # TODO: Test with sequence.get_chipset_weighted_value()
    def play_forced_self(self, board):
        best_chip = None
        best_number = None

        if self.chip_node_list.has_number_to_play_immediately(board.get_forced_numbers()):
            chip_node = self.chip_node_list.get_best_numbered_chip_to_play(board.get_forced_numbers())
            best_chip = chip_node.get_chip()
            best_number = chip_node.get_chip_side_to_play()
        else:
            self.needs_to_update_sequence = True
            best_sequence_plus_chip_value = 0
            my_open_positions = board.get_row(self.index).get_open_positions()

            for chip in self.chips:
                for number in board.get_forced_numbers():
                    if chip.__contains__(number):
                        new_chips = self.chips.copy()
                        new_chips.remove(chip)
                        new_open_positions = my_open_positions.copy()
                        new_open_positions.remove(number)
                        new_open_positions.append(chip.get_other_side(number))
                        new_sequence_plus_chip_value = chip.get_value()

                        new_sequence = generate_sequence(new_open_positions, new_chips,
                                                         self.heuristic_value_per_chip, self.front_loaded_index)

                        if new_sequence is not None:
                            new_sequence_plus_chip_value += new_sequence.get_chipset_value()

                        if new_sequence_plus_chip_value > best_sequence_plus_chip_value:
                            best_sequence_plus_chip_value = new_sequence_plus_chip_value
                            best_number = number
                            best_chip = chip

        board.play_chip(best_chip, best_number, self.index)
        board.remove_forced(best_number)
        self.chips.remove(best_chip)

        if not board.is_forced():
            board.remove_train(self.index)

    def play_first(self, board):
        forced_counter = 0

        while self.chip_node_list.has_chip_to_play():
            cn = self.chip_node_list.get_best_chip_to_play()
            chips = cn.get_next_piece()
            for chip in chips:
                print("%s plays chip %s" % (self.name, chip.__str__()))
                if chip.is_double() and len(chips) == 1:
                    forced_counter += 1
                    board.set_forced(self.index, chip.get_side_a(), self.index)
                board.play_chip(chip, cn.get_chip_side_to_play(), self.index)
                self.chips.remove(chip)

        if forced_counter > 0:
            new_chips = []
            for i in range(forced_counter):
                if board.can_draw():
                    new_chips.append(board.draw())
                    print("%s draws chip %s" % (self.name, chip.__str__()))

            for number in board.get_forced_numbers():
                for chip in new_chips:
                    if chip.__contains__(number):
                        board.play_chip(chip, number, self.index)
                        board.remove_forced(number)
                        forced_counter -= 1
                        new_chips.remove(chip)
                        break

            if forced_counter > 0:
                board.set_train(self.index)
                self.chips.extend(new_chips)
            else:
                board.remove_train(self.index)

    def play(self, board):
        if self.needs_to_update_sequence or board.get_forced_row() == self.index:
            print("%s is updating sequence" % self.name)
            self.update_sequence(board)

        if board.is_forced():
            print("%s is forced" % self.name)
            self.play_forced(board)
        elif self.can_play_all_my_chips_if_i_play_many(board):
            print("%s is playing all their chips" % self.name)
            self.play_first(board)
        elif self.can_play_cheaply_elsewhere(board):
            print("%s is playing elsewhere" % self.name)
            self.play_cheaply_elsewhere(board)
        elif board.get_row(self.index).can_play_many():
            print("%s is playing many" % self.name)
            self.play_first(board)
        else:
            print("%s is playing on their row, only one chip" % self.name)
            self.play_any(board)
        self.end_turn(board)

    def play_any(self, board):
        if self.chip_node_list.has_chip_to_play():
            chip = self.chip_node_list.get_best_chip_to_play()
            side_to_play = chip.get_chip_side_to_play()
            self.play_chips(board, chip.get_next_piece(), side_to_play, self.index)

            if chip.is_chip_double() and len(chip.get_next_piece()) == 1:
                print("%s played a double but has no second chip" % self.name)
                if board.can_draw():
                    drawn_chip = board.draw()
                    print("%s draws %s" % (self.name, drawn_chip))
                    if drawn_chip.__contains__(side_to_play):
                        print("The drawn chip is playable!")
                        self.play_chips(board, [drawn_chip], side_to_play, self.index)
                    else:
                        self.add_chip(drawn_chip)
                        board.set_train(self.index)
                        board.set_forced(self.index, side_to_play, self.index)
                else:
                    board.set_train(self.index)
                    board.set_forced(self.index, side_to_play, self.index)
            if board.get_forced_row() != self.index:
                board.remove_train(self.index)
        else:
            print("I should not be here")
            super().play_any(board)

    def can_play_cheaply_elsewhere(self, board, min_acceptable_value=0):
        if board.has_train(self.index):
            return False

        chips_not_in_sequence = list(set(self.chips) - set(self.chip_node_list.get_chipset()))
        my_open_positions = board.get_row(self.index).get_open_positions()
        my_current_chain_value = self.chip_node_list.get_chipset_value()
        doubles = dict()

        for chip in chips_not_in_sequence:
            if chip.is_double():
                doubles[chip.get_side_a()] = chip
                for row in board.get_rows():
                    if row.get_index() != self.get_index() and row.has_train():
                        for position in row.get_open_positions():
                            if chip.__contains__(position):
                                value = chip.get_value() * self.play_chip_elsewhere_multiplier - self.penalty_for_playing_lone_double
                                if value > min_acceptable_value:
                                    return True

        for row in board.get_rows():
            if row.get_index() != self.get_index() and row.has_train():
                for position in row.get_open_positions():
                    for chip in chips_not_in_sequence:
                        if chip.__contains__(position) and not chip.is_double():
                            current_chip = [chip]
                            current_value = chip.get_value() * self.play_chip_elsewhere_multiplier
                            if doubles.__contains__(position):
                                current_chip.insert(0, doubles.get(position))
                                current_value += doubles.get(position).get_value() * self.play_chip_elsewhere_multiplier + self.heuristic_value_per_chip
                            if current_value > min_acceptable_value:
                                return True

        for chip in self.chip_node_list.get_chipset():
            if chip.is_double():
                doubles[chip.get_side_a()] = chip
                for row in board.get_rows():
                    if row.get_index() != self.get_index() and row.has_train():
                        for position in row.get_open_positions():
                            if chip.__contains__(position):
                                value = chip.get_value() * self.play_chip_elsewhere_multiplier - self.penalty_for_playing_lone_double
                                if value > min_acceptable_value:
                                    return True

        for row in board.get_rows():
            if row.get_index() != self.get_index() and row.has_train():
                for position in row.get_open_positions():
                    for chip in self.chip_node_list.get_chipset():
                        if chip.__contains__(position) and not chip.is_double():
                            new_chips = self.chips.copy()
                            new_chips.remove(chip)
                            new_sequence = generate_sequence(my_open_positions, new_chips, self.heuristic_value_per_chip, self.front_loaded_index)
                            current_chip = [chip]
                            current_value = chip.get_value() * self.play_chip_elsewhere_multiplier + new_sequence.get_chipset_value() - my_current_chain_value

                            if doubles.__contains__(position):
                                new_chips.remove(doubles.get(position))
                                new_sequence = generate_sequence(my_open_positions, new_chips, self.heuristic_value_per_chip, self.front_loaded_index)
                                value_with_double = (chip.get_value() + doubles.get(position).get_value()) * self.play_chip_elsewhere_multiplier \
                                                    + self.heuristic_value_per_chip + new_sequence.get_chipset_value() - my_current_chain_value
                                if value_with_double > current_value:
                                    current_value = value_with_double
                                    current_chip.insert(0, doubles.get(position))

                            if current_value > min_acceptable_value:
                                return True

        return False

    def play_cheaply_elsewhere(self, board):
        chips_not_in_sequence = list(set(self.chips) - set(self.chip_node_list.get_chipset()))
        my_open_positions = board.get_row(self.index).get_open_positions()
        my_current_chain_value = self.chip_node_list.get_chipset_value()
        doubles = dict()

        best_value = -math.inf
        best_chip = []
        best_side = -1
        best_row = -1

        for chip in chips_not_in_sequence:
            if chip.is_double():
                doubles[chip.get_side_a()] = chip
                for row in board.get_rows():
                    if row.get_index() != self.get_index() and row.has_train():
                        for position in row.get_open_positions():
                            if chip.__contains__(position):
                                value = chip.get_value() * self.play_chip_elsewhere_multiplier - self.penalty_for_playing_lone_double
                                if value > best_value:
                                    best_value = value
                                    best_chip = [chip]
                                    best_side = position
                                    best_row = row.get_index()

        for row in board.get_rows():
            if row.get_index() != self.get_index() and row.has_train():
                for position in row.get_open_positions():
                    for chip in chips_not_in_sequence:
                        if chip.__contains__(position) and not chip.is_double():
                            current_chip = [chip]
                            current_value = chip.get_value() * self.play_chip_elsewhere_multiplier
                            if doubles.__contains__(position):
                                current_chip.insert(0, doubles.get(position))
                                current_value += doubles.get(position).get_value() * self.play_chip_elsewhere_multiplier + self.heuristic_value_per_chip
                            if current_value > best_value:
                                best_value = current_value
                                best_chip = current_chip
                                best_side = position
                                best_row = row.get_index()

        for chip in self.chip_node_list.get_chipset():
            if chip.is_double():
                doubles[chip.get_side_a()] = chip
                for row in board.get_rows():
                    if row.get_index() != self.get_index() and row.has_train():
                        for position in row.get_open_positions():
                            if chip.__contains__(position):
                                value = chip.get_value() * self.play_chip_elsewhere_multiplier - self.penalty_for_playing_lone_double
                                if value > best_value:
                                    best_value = value
                                    best_chip = [chip]
                                    best_side = position
                                    best_row = row.get_index()

        for row in board.get_rows():
            if row.get_index() != self.get_index() and row.has_train():
                for position in row.get_open_positions():
                    for chip in self.chip_node_list.get_chipset():
                        if chip.__contains__(position) and not chip.is_double():
                            new_chips = self.chips.copy()
                            new_chips.remove(chip)
                            new_sequence = generate_sequence(my_open_positions, new_chips, self.heuristic_value_per_chip, self.front_loaded_index)
                            current_chip = [chip]
                            current_value = chip.get_value() * self.play_chip_elsewhere_multiplier + new_sequence.get_chipset_value() - my_current_chain_value

                            if doubles.__contains__(position):
                                new_chips.remove(doubles.get(position))
                                new_sequence = generate_sequence(my_open_positions, new_chips, self.heuristic_value_per_chip, self.front_loaded_index)
                                value_with_double = (chip.get_value() + doubles.get(position).get_value()) * self.play_chip_elsewhere_multiplier \
                                    + self.heuristic_value_per_chip + new_sequence.get_chipset_value() - my_current_chain_value
                                if value_with_double > current_value:
                                    current_value = value_with_double
                                    current_chip.insert(0, doubles.get(position))

                            if current_value > best_value:
                                self.needs_to_update_sequence = True
                                best_value = current_value
                                best_chip = current_chip
                                best_side = position
                                best_row = row.get_index()

        self.play_chips(board, best_chip, best_side, best_row)

    def can_play_all_my_chips_if_i_play_many(self, board):
        if not board.get_row(self.index).can_play_many():
            return False
        if self.chip_node_list.get_chipset_value() == self.get_current_points():
            return True
        return False

    def update_sequence(self, board):
        self.needs_to_update_sequence = False
        self.chip_node_list = generate_sequence(
            board.get_row(self.index).get_open_positions(),
            self.chips,
            self.heuristic_value_per_chip,
            self.front_loaded_index)

    def play_chips(self, board, chips, side, row):
        for chip in chips:
            board.play_chip(chip, side, row)
            self.chips.remove(chip)
            print("%s plays %s" % (chip, self.name))

    def init_round(self, chips):
        super().init_round(chips)
        self.needs_to_update_sequence = True

    def add_chip(self, chip):
        super().add_chip(chip)
        self.needs_to_update_sequence = True
