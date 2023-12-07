# Representation of what an average human player may play like. An average human is likely a bit better,
# but this should be close enough for testing and training purposes.
import logging
import math

from ai.SequenceGeneration import generate_sequence
from game.ChipNode import ChipNode
from game.ChipNodeList import ChipNodeList
from players.CPUPlayer import CPUPlayer


class SmartCPUCPUPlayer(CPUPlayer):
    def __init__(self, index, name=None):
        super().__init__(index, name)
        self.play_chip_elsewhere_multiplier = 1.3
        self.penalty_for_playing_lone_double = 8
        self.needs_to_update_sequence = True
        self.heuristic_value_per_chip = 7
        self.front_loaded_index = 0.99
        self.chip_node_list = None
        self.danger_threshold = 2

    def init_round(self, chips, double_to_skip=None):
        super().init_round(chips)
        self.needs_to_update_sequence = True

    def add_chip(self, chip):
        super().add_chip(chip)
        self.needs_to_update_sequence = True

    def update_sequence(self, board, max_depth=math.inf):
        self.needs_to_update_sequence = False
        self.chip_node_list = generate_sequence(
            board.get_row(self.index).get_open_positions(),
            self.chips,
            self.heuristic_value_per_chip,
            self.front_loaded_index,
            max_depth)

    def play(self, board, players):
        if self.needs_to_update_sequence or board.has_train(self.index):
            logging.info("%s is updating sequence" % self.name)
            self.update_sequence(board)
        if board.is_forced():
            logging.info("%s is forced" % self.name)
            return self.play_forced(board)
        if self.can_play_all_my_chips_if_i_play_many(board):
            logging.info("%s is playing all their chips" % self.name)
            return self.play_first(board, True)
        if self.danger_of_other_players_winning(players):
            logging.info("%s is playing many points quickly" % self.name)
            return self.play_many_points_quickly(board, other_players_min_chip_count(players))
        if self.can_play_cheaply_elsewhere(board):
            logging.info("%s is playing elsewhere" % self.name)
            return self.play_cheaply_elsewhere(board)
        if self.can_play_many(board):
            logging.info("%s is playing many" % self.name)
            return self.play_first(board)  # Sometimes it is best to keep one for next turn.
        if self.chip_node_list.has_chip_to_play():
            logging.info("%s is playing on their row, only one chip" % self.name)
            return self.play_self()
        if self.can_play_self(board):
            raise Exception("What's going on?")
        logging.info("%s is playing elsewhere." % self.name)
        return self.play_cheaply_elsewhere(board)

    def play_forced(self, board):
        if board.get_forced_row_index() == self.index:
            logging.info("%s playing forced self" % self.name)
            return self.play_forced_self(board)
        else:
            logging.info("%s playing forced elsewhere" % self.name)
            return self.play_forced_elsewhere(board)

    # TODO: Test with sequence.get_chipset_weighted_value()
    def play_forced_self(self, board):
        if self.chip_node_list.has_number_to_play_immediately(board.get_forced_numbers()):
            chip_node = self.chip_node_list.get_best_numbered_chip_to_play(board.get_forced_numbers())
            return [ChipNodeList([chip_node]), self.index]

        best_sequence_plus_chip_value = 0
        best_number = None
        best_chip = None
        my_open_positions = board.get_row(self.index).get_open_positions()

        for chip in self.chips:
            for number in board.get_forced_numbers():
                if number in chip:
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
                        self.chip_node_list = new_sequence
                        best_sequence_plus_chip_value = new_sequence_plus_chip_value
                        best_number = number
                        best_chip = chip

        return [ChipNodeList([ChipNode(best_chip, best_number)]), self.index]

    # TODO: Test using sequence.get_chipset_weighted_value() instead of regular sequence.get_chipset_value()
    def play_forced_elsewhere(self, board):
        chips_not_in_sequence = list(set(self.chips) - set(self.chip_node_list.get_chipset()))
        max_value = -math.inf
        best_number = None
        best_chip = None

        for chip in chips_not_in_sequence:
            for number in board.get_forced_numbers():
                if number in chip and chip.get_value() > max_value:
                    max_value = chip.get_value()
                    best_number = number
                    best_chip = chip

        my_current_sequence_value = self.chip_node_list.get_chipset_value()
        min_points_lost = math.inf

        if best_chip is not None:
            min_points_lost = -best_chip.get_value()

        for chip in self.chip_node_list.get_chipset():
            for number in board.get_forced_numbers():
                if number in chip:
                    new_chips = self.chips.copy()
                    new_chips.remove(chip)
                    new_sequence = generate_sequence(board.get_row(self.index).get_open_positions(), new_chips,
                                                     self.heuristic_value_per_chip, self.front_loaded_index)

                    if new_sequence is None:
                        points_lost = my_current_sequence_value - chip.get_value()
                    else:
                        points_lost = my_current_sequence_value - new_sequence.get_chipset_value() - chip.get_value()

                    if points_lost < min_points_lost or (points_lost == min_points_lost and chip.get_value() > best_chip.get_value()):
                        self.chip_node_list = new_sequence
                        min_points_lost = points_lost
                        best_number = number
                        best_chip = chip

        return [ChipNodeList([ChipNode(best_chip, best_number)]), board.get_forced_row_index()]

    def can_play_many(self, board):
        return board.get_row(self.index).can_play_many() and self.chip_node_list.has_chip_to_play()

    def can_play_all_my_chips_if_i_play_many(self, board):
        return board.get_row(self.index).can_play_many() and self.chip_node_list.get_chipset_value() == self.get_current_points()

    def play_first(self, board, play_all=True):
        cnl = self.chip_node_list
        self.chip_node_list = ChipNodeList()
        return [cnl, self.index]

    def can_play_self(self, board):
        for position in board.get_row(self.index).get_open_positions():
            for chip in self.chips:
                if position in chip:
                    return True
        return False

    def play_self(self):
        chip_node = self.chip_node_list.get_best_chip_to_play()
        return [ChipNodeList([chip_node]), self.index]

    def danger_of_other_players_winning(self, players):
        for player in players:
            if player.get_chip_count() <= self.danger_threshold:
                return True
        return False

    def play_many_points_quickly(self, board, min_chip_count):
        best_value = 0
        best_move = None

        if self.can_play_many(board):
            best_value = self.chip_node_list.get_chipset_weighted_value()
            best_move = self.chip_node_list

        turns_remaining = max(min_chip_count, 1)
        self.update_sequence(board, turns_remaining)
        self.needs_to_update_sequence = True

        if self.chip_node_list.has_chip_to_play() and best_move is None:
            best_move = ChipNodeList([self.chip_node_list.get_best_chip_to_play()])
            best_value = best_move.get_chipset_weighted_value()

        if self.can_play_cheaply_elsewhere(board, best_value, True):
            return self.play_cheaply_elsewhere(board)

        if best_move is not None:
            return [best_move, self.index]

        return self.play_cheaply_elsewhere(board)

    def can_play_cheaply_elsewhere(self, board, min_acceptable_value=0, play_lone_double_acceptable=False):
        if board.has_train(self.index):
            return False

        penalty_for_playing_lone_double = self.penalty_for_playing_lone_double
        if not play_lone_double_acceptable:
            penalty_for_playing_lone_double = 0

        chips_not_in_sequence = list(set(self.chips) - set(self.chip_node_list.get_chipset()))
        my_open_positions = board.get_row(self.index).get_open_positions()
        my_current_sequence_value = self.chip_node_list.get_chipset_value()
        doubles = dict()

        # Check for doubles that are not in the sequence
        for chip in chips_not_in_sequence:
            if chip.is_double():
                doubles[chip.get_side_a()] = chip
                for row in board.get_rows():
                    if row.get_index() != self.get_index() and row.has_train():
                        for position in row.get_open_positions():
                            if position in chip:
                                value = chip.get_value() * self.play_chip_elsewhere_multiplier - penalty_for_playing_lone_double
                                if value > min_acceptable_value:
                                    return True

        # Check for the rest of the chips that are not in the sequence
        for row in board.get_rows():
            if row.get_index() != self.get_index() and row.has_train():
                for position in row.get_open_positions():
                    for chip in chips_not_in_sequence:
                        if position in chip and not chip.is_double():
                            current_value = chip.get_value() * self.play_chip_elsewhere_multiplier
                            if position in doubles:
                                current_value += doubles.get(position).get_value() * self.play_chip_elsewhere_multiplier + self.heuristic_value_per_chip
                            if current_value > min_acceptable_value:
                                return True

        # Check for the doubles in the sequence
        for chip in self.chip_node_list.get_chipset():
            if chip.is_double():
                doubles[chip.get_side_a()] = chip
                for row in board.get_rows():
                    if row.get_index() != self.get_index() and row.has_train():
                        for position in row.get_open_positions():
                            if position in chip:
                                value = chip.get_value() * self.play_chip_elsewhere_multiplier - penalty_for_playing_lone_double
                                if value > min_acceptable_value:
                                    return True

        # Check for the rest of the chips in the sequence
        for row in board.get_rows():
            if row.get_index() != self.get_index() and row.has_train():
                for position in row.get_open_positions():
                    for chip in self.chip_node_list.get_chipset():
                        if position in chip and not chip.is_double():
                            new_chips = self.chips.copy()
                            new_chips.remove(chip)
                            new_sequence = generate_sequence(my_open_positions, new_chips, self.heuristic_value_per_chip, self.front_loaded_index)
                            current_value = chip.get_value() * self.play_chip_elsewhere_multiplier + new_sequence.get_chipset_value() - my_current_sequence_value

                            if position in doubles:
                                new_chips.remove(doubles.get(position))
                                new_sequence = generate_sequence(my_open_positions, new_chips, self.heuristic_value_per_chip, self.front_loaded_index)
                                value_with_double = (chip.get_value() + doubles.get(position).get_value()) * self.play_chip_elsewhere_multiplier + self.heuristic_value_per_chip + new_sequence.get_chipset_value() - my_current_sequence_value
                                if value_with_double > current_value:
                                    current_value = value_with_double

                            if current_value > min_acceptable_value:
                                return True
        return False

    def play_cheaply_elsewhere(self, board):
        self.needs_to_update_sequence = True
        chips_not_in_sequence = list(set(self.chips) - set(self.chip_node_list.get_chipset()))
        my_open_positions = board.get_row(self.index).get_open_positions()
        my_current_sequence_value = self.chip_node_list.get_chipset_value()
        doubles = dict()

        best_value = -math.inf
        best_chip_node = None
        best_row = -1

        # Check for doubles that are not in the sequence
        for chip in chips_not_in_sequence:
            if chip.is_double():
                doubles[chip.get_side_a()] = ChipNode(chip, chip.get_side_a())
                for row in board.get_rows_random_start():
                    if row.get_index() != self.get_index() and row.has_train():
                        for position in row.get_open_positions():
                            if position in chip:
                                value = chip.get_value() - self.penalty_for_playing_lone_double
                                if value > best_value:
                                    best_value = value
                                    best_row = row.get_index()
                                    best_chip_node = ChipNode(chip, position)

        # Check for the rest of the chips that are not in the sequence
        for row in board.get_rows_random_start():
            if row.get_index() != self.get_index() and row.has_train():
                for position in row.get_open_positions():
                    for chip in chips_not_in_sequence:
                        if position in chip and not chip.is_double():
                            current_chip_node = ChipNode(chip, position)
                            current_value = chip.get_value()
                            if position in doubles:
                                current_chip_node = doubles.get(position)
                                current_chip_node.override_next_node(ChipNode(chip, position))
                                current_value = doubles.get(position).get_next_move_value() + self.heuristic_value_per_chip
                            if current_value > best_value:
                                best_value = current_value
                                best_row = row.get_index()
                                best_chip_node = current_chip_node

        # Check for the doubles in the sequence
        for chip in self.chip_node_list.get_chipset():
            if chip.is_double():
                doubles[chip.get_side_a()] = ChipNode(chip, chip.get_side_a())
                for row in board.get_rows_random_start():
                    if row.get_index() != self.get_index() and row.has_train():
                        for position in row.get_open_positions():
                            if position in chip:
                                value = chip.get_value() - self.penalty_for_playing_lone_double
                                if value > best_value:
                                    best_row = row.get_index()
                                    best_value = value
                                    best_chip_node = ChipNode(chip, position)

        # Check for the rest of the chips in the sequence
        for row in board.get_rows_random_start():
            if row.get_index() != self.get_index() and row.has_train():
                for position in row.get_open_positions():
                    for chip in self.chip_node_list.get_chipset():
                        if position in chip and not chip.is_double():
                            new_chips = self.chips.copy()
                            new_chips.remove(chip)
                            new_sequence = generate_sequence(my_open_positions, new_chips, self.heuristic_value_per_chip, self.front_loaded_index)
                            current_chip_node = ChipNode(chip, position)
                            current_value = chip.get_value() + new_sequence.get_chipset_value() - my_current_sequence_value
                            if position in doubles:
                                new_chips.remove(doubles.get(position).get_chip())
                                new_sequence = generate_sequence(my_open_positions, new_chips, self.heuristic_value_per_chip, self.front_loaded_index)
                                value_with_double = chip.get_value() + doubles.get(position).get_next_move_value() + self.heuristic_value_per_chip \
                                                    + new_sequence.get_chipset_value() - my_current_sequence_value
                                if value_with_double > current_value:
                                    current_value = value_with_double
                                    current_chip_node = doubles.get(position)
                                    current_chip_node.override_next_node(ChipNode(chip, position))

                            if current_value > best_value:
                                best_value = current_value
                                best_row = row.get_index()
                                best_chip_node = current_chip_node

        return [ChipNodeList([best_chip_node]), best_row]


def other_players_min_chip_count(players):
    min_chip_count = math.inf
    for player in players:
        if player.get_chip_count() < min_chip_count:
            min_chip_count = player.get_chip_count()
    return min_chip_count
