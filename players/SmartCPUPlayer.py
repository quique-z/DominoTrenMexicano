# Representation of what an average human player may play like. An average human is likely a bit better,
# but this should be close enough for testing and training purposes.
import logging
import math
from typing import List, Set

from ai.SequenceGeneration import generate_sequence
from game import Chip, Board
from game.ChipNode import ChipNode
from game.PlayableChipNode import PlayableChipNode
from players import Player
from players.CPUPlayer import CPUPlayer


class SmartCPUPlayer(CPUPlayer):
    empty_row_percentage_to_keep_one_piece = 0.8
    play_chip_elsewhere_multiplier = 1.3
    penalty_for_playing_lone_double = 7
    heuristic_value_per_chip = 7
    danger_threshold = 2

    def __init__(self, index, name=None):
        super().__init__(index, name)
        self.needs_to_update_sequence = True
        self.chip_node_list = None

    def init_round(self, chips: Set[Chip] = None, double_to_skip: int = None) -> None:
        super().init_round(chips)
        self.needs_to_update_sequence = True

    def add_chip(self, chip: Chip) -> None:
        super().add_chip(chip)
        self.needs_to_update_sequence = True

    def update_sequence(self, board: Board, max_depth: int = math.inf) -> None:
        self.needs_to_update_sequence = False
        self.chip_node_list = generate_sequence(board.get_row(self.index).get_open_positions(), self.chips, self.heuristic_value_per_chip, max_depth)

    def play(self, board: Board, players: List[Player]) -> PlayableChipNode:
        if self.needs_to_update_sequence or board.has_train(self.index):
            logging.info(f"{self.name} is updating sequence")
            self.update_sequence(board)
        if board.is_forced():
            logging.info(f"{self.name} is forced")
            return self.play_forced(board)
        if self.can_play_all_my_chips_if_i_play_many(board):
            logging.info(f"{self.name} is playing all their chips")
            return self.play_first(play_all=True)
        if self.danger_of_other_players_winning(players):
            logging.info(f"{self.name} is playing many points quickly")
            return self.play_many_points_quickly(board, other_players_min_chip_count(players))
        if self.can_play_cheaply_elsewhere(board):
            logging.info(f"{self.name} is playing elsewhere")
            return self.play_cheaply_elsewhere(board)
        if self.can_play_many(board):
            logging.info(f"{self.name} is playing many")
            return self.play_first(self.should_play_all(board))
        if self.chip_node_list.has_chip_to_play():
            logging.info(f"{self.name} is playing on their row, only one chip")
            return self.play_self()
        if self.can_play_self(board):
            raise Exception("What's going on?")
        logging.info(f"{self.name} is playing elsewhere.")
        return self.play_cheaply_elsewhere(board)

    def play_forced(self, board: Board) -> PlayableChipNode:
        if board.get_forced_row_index() == self.index:
            logging.info(f"{self.name} playing forced self")
            return self.play_forced_self(board)
        else:
            logging.info(f"{self.name} playing forced elsewhere")
            return self.play_forced_elsewhere(board)

    # TODO: Test with sequence.get_chipset_weighted_value()
    def play_forced_self(self, board: Board) -> PlayableChipNode:
        if self.chip_node_list.has_number_to_play_immediately(board.get_forced_numbers()):
            chip_node = self.chip_node_list.get_best_numbered_chip_to_play(board.get_forced_numbers())
            return PlayableChipNode(chip_node, self.index)

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

                    new_sequence = generate_sequence(new_open_positions, new_chips, self.heuristic_value_per_chip)

                    if new_sequence:
                        new_sequence_plus_chip_value += new_sequence.get_chipset_value()

                    if new_sequence_plus_chip_value > best_sequence_plus_chip_value:
                        self.chip_node_list = new_sequence
                        best_sequence_plus_chip_value = new_sequence_plus_chip_value
                        best_number = number
                        best_chip = chip

        return PlayableChipNode(ChipNode(best_chip, best_number), self.index)

    # TODO: Test using sequence.get_chipset_weighted_value() instead of regular sequence.get_chipset_value()
    def play_forced_elsewhere(self, board: Board) -> PlayableChipNode:
        chips_not_in_sequence = self.chips.difference(self.chip_node_list.get_chipset())
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

        if best_chip:
            min_points_lost = -best_chip.get_value()

        for chip in self.chip_node_list.get_chipset():
            for number in board.get_forced_numbers():
                if number in chip:
                    new_chips = self.chips.copy()
                    new_chips.remove(chip)
                    new_sequence = generate_sequence(board.get_row(self.index).get_open_positions(), new_chips, self.heuristic_value_per_chip)

                    if new_sequence:
                        points_lost = my_current_sequence_value - new_sequence.get_chipset_value() - chip.get_value()
                    else:
                        points_lost = my_current_sequence_value - chip.get_value()

                    if points_lost < min_points_lost or (points_lost == min_points_lost and chip.get_value() > best_chip.get_value()):
                        self.chip_node_list = new_sequence
                        min_points_lost = points_lost
                        best_number = number
                        best_chip = chip

        return PlayableChipNode(ChipNode(best_chip, best_number), board.get_forced_row_index())

    def can_play_many(self, board: Board) -> bool:
        return board.get_row(self.index).can_play_many() and self.chip_node_list.has_chip_to_play()

    def should_play_all(self, board: Board) -> bool:
        if len(self.chip_node_list) < 2:
            return True

        empty_row_count = 0
        for row in board.get_rows():
            if row.can_play_many():
                empty_row_count += 1
        return empty_row_count / board.get_number_of_players() >= self.empty_row_percentage_to_keep_one_piece

    def can_play_all_my_chips_if_i_play_many(self, board: Board) -> bool:
        return board.get_row(self.index).can_play_many() and len(self.chip_node_list) == len(self.chips)

    def play_first(self, play_all: bool = True) -> PlayableChipNode:
        if play_all:
            return PlayableChipNode(self.chip_node_list.get_all_chips(), self.index)
        else:
            return PlayableChipNode(self.chip_node_list.get_all_chips_minus_last(), self.index)

    def can_play_self(self, board):
        for position in board.get_row(self.index).get_open_positions():
            for chip in self.chips:
                if position in chip:
                    return True
        return False

    def play_self(self) -> PlayableChipNode:
        chip_node = self.chip_node_list.get_best_chip_to_play()
        return PlayableChipNode(chip_node, self.index)

    def danger_of_other_players_winning(self, players: List[Player]) -> bool:
        for player in players:
            if player.get_chip_count() <= self.danger_threshold:
                return True
        return False

    def play_many_points_quickly(self, board: Board, min_chip_count: int) -> PlayableChipNode:
        best_value = 0
        best_move = None

        if self.can_play_many(board):
            best_move = self.chip_node_list.get_all_chips()
            best_value = best_move.get_chain_value()

        turns_remaining = max(min_chip_count, 1)
        tmp_chip_node_list = generate_sequence(board.get_row(self.index).get_open_positions(), self.chips, self.heuristic_value_per_chip, turns_remaining)

        if not best_move and tmp_chip_node_list.has_chip_to_play():
            best_move = tmp_chip_node_list.get_best_chip_to_play()
            best_value = best_move.get_chain_value()
            self.needs_to_update_sequence = True

        if self.can_play_cheaply_elsewhere(board, best_value, True):
            return self.play_cheaply_elsewhere(board, True)

        if best_move:
            return PlayableChipNode(best_move, self.index)

        return self.play_cheaply_elsewhere(board)

    def can_play_cheaply_elsewhere(self, board: Board, min_acceptable_value: int = 0, play_lone_double_acceptable: bool = False) -> bool:
        if board.has_train(self.index):
            return False

        penalty_for_playing_lone_double = 0 if play_lone_double_acceptable else self.penalty_for_playing_lone_double

        chips_not_in_sequence = self.chips - self.chip_node_list.get_chipset()
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

        # Check for the rest of the chips in the sequence
        for row in board.get_rows():
            if row.get_index() != self.get_index() and row.has_train():
                for position in row.get_open_positions():
                    for chip in self.chip_node_list.get_chipset():
                        if position in chip:
                            new_chips = self.chips.copy()
                            new_chips.remove(chip)
                            new_sequence = generate_sequence(my_open_positions, new_chips, self.heuristic_value_per_chip)
                            current_value = chip.get_value() * self.play_chip_elsewhere_multiplier + new_sequence.get_chipset_value() - my_current_sequence_value

                            if not chip.is_double() and position in doubles:
                                new_chips.remove(doubles.get(position))
                                new_sequence = generate_sequence(my_open_positions, new_chips, self.heuristic_value_per_chip)
                                value_with_double = ((chip.get_value() + doubles.get(position).get_value()) * self.play_chip_elsewhere_multiplier +
                                                     self.heuristic_value_per_chip + new_sequence.get_chipset_value() - my_current_sequence_value)

                                if value_with_double > current_value:
                                    current_value = value_with_double

                            if current_value > min_acceptable_value:
                                return True
        return False

    def play_cheaply_elsewhere(self, board: Board, play_lone_double_acceptable: bool = False) -> PlayableChipNode:
        self.needs_to_update_sequence = True
        chips_not_in_sequence = self.chips - self.chip_node_list.get_chipset()
        my_open_positions = board.get_row(self.index).get_open_positions()
        my_current_sequence_value = self.chip_node_list.get_chipset_value()
        doubles = dict()
        penalty_for_playing_lone_double = 0 if play_lone_double_acceptable else self.penalty_for_playing_lone_double

        best_value = -math.inf
        best_chip_node = None
        best_row = -1

        # Check for doubles that are not in the sequence
        for chip in chips_not_in_sequence:
            if chip.is_double():
                doubles[chip.get_side_a()] = chip

                can_play_double_alone = True
                for chip2 in self.chips:
                    if chip != chip2 and chip.get_side_a() in chip2:
                        can_play_double_alone = False
                        break

                if can_play_double_alone:
                    for row in board.get_rows():
                        if row.get_index() != self.get_index() and row.has_train():
                            for position in row.get_open_positions():
                                if position in chip:
                                    value = chip.get_value() * self.play_chip_elsewhere_multiplier - penalty_for_playing_lone_double
                                    if value > best_value:
                                        best_value = value
                                        best_row = row.get_index()
                                        best_chip_node = ChipNode(chip, position)

        # Check for the rest of the chips that are not in the sequence
        for row in board.get_rows():
            if row.get_index() != self.get_index() and row.has_train():
                for position in row.get_open_positions():
                    for chip in chips_not_in_sequence:
                        if position in chip and not chip.is_double():
                            current_chip_node = ChipNode(chip, position)
                            current_value = chip.get_value()
                            if position in doubles:
                                current_chip_node = ChipNode(doubles.get(position), position)
                                current_chip_node.override_next_node(ChipNode(chip, position))
                                current_value += doubles.get(position).get_value() + self.heuristic_value_per_chip
                            if current_value > best_value:
                                best_value = current_value
                                best_row = row.get_index()
                                best_chip_node = current_chip_node

        # Check for the doubles in the sequence
        for chip in self.chip_node_list.get_chipset():
            if chip.is_double():
                doubles[chip.get_side_a()] = chip

                can_play_double_alone = len(self.chip_node_list) == 1

                if can_play_double_alone:
                    for row in board.get_rows():
                        if row.get_index() != self.get_index() and row.has_train():
                            for position in row.get_open_positions():
                                if position in chip:
                                    value = chip.get_value() * self.play_chip_elsewhere_multiplier - penalty_for_playing_lone_double
                                    if value > best_value:
                                        best_value = value
                                        best_row = row.get_index()
                                        best_chip_node = ChipNode(chip, position)

        # Check for the rest of the chips in the sequence
        for row in board.get_rows():
            if row.get_index() != self.get_index() and row.has_train():
                for position in row.get_open_positions():
                    for chip in self.chip_node_list.get_chipset():
                        if position in chip and not chip.is_double():
                            new_chips = self.chips.copy()
                            new_chips.remove(chip)
                            new_sequence = generate_sequence(my_open_positions, new_chips, self.heuristic_value_per_chip)
                            current_chip_node = ChipNode(chip, position)
                            current_value = chip.get_value() + new_sequence.get_chipset_value() - my_current_sequence_value

                            if position in doubles:
                                new_chips.remove(doubles.get(position))
                                new_sequence = generate_sequence(my_open_positions, new_chips, self.heuristic_value_per_chip)
                                value_with_double = (chip.get_value() + doubles.get(position).get_value() + self.heuristic_value_per_chip +
                                                     new_sequence.get_chipset_value() - my_current_sequence_value)
                                if value_with_double > current_value:
                                    current_value = value_with_double
                                    current_chip_node = ChipNode(doubles.get(position), position)
                                    current_chip_node.override_next_node(ChipNode(chip, position))

                            if current_value > best_value:
                                best_value = current_value
                                best_row = row.get_index()
                                best_chip_node = current_chip_node
        if not best_chip_node:
            raise Exception(f"Player {self.name} did not find a chip to play despite having one.")
        return PlayableChipNode(best_chip_node, best_row)


def other_players_min_chip_count(players: List[Player]) -> int:
    min_chip_count = math.inf
    for player in players:
        if player.get_chip_count() < min_chip_count:
            min_chip_count = player.get_chip_count()
    return min_chip_count
