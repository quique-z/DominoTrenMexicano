import math
from typing import List, Set, Optional

from game.Chip import Chip
from game.ChipNode import ChipNode
from game.ChipNodeList import ChipNodeList

front_loaded_index = 0.9999


def generate_sequence(open_positions: List[int], chips: Set[Chip], heuristic_value_per_chip: int = 0, max_depth: int = math.inf) -> ChipNodeList:
    positions_to_consider = open_positions.copy()
    chip_node_list = ChipNodeList()
    new_chips = chips.copy()
    ready_to_exit = False

    while not ready_to_exit:
        best_open_position = None
        best_score = -math.inf
        ready_to_exit = True
        best_sequence = None

        for position in positions_to_consider:
            sequence = generate_sequence_recursive(position, new_chips, heuristic_value_per_chip, max_depth)
            if sequence and sequence.get_chain_weighted_value() > best_score:
                best_score = sequence.get_chain_weighted_value()
                best_open_position = position
                best_sequence = sequence
                ready_to_exit = False

        if best_sequence:
            new_chips -= best_sequence.get_chipset()
            positions_to_consider.remove(best_open_position)
            chip_node_list.add(best_sequence)
            max_depth -= best_sequence.get_depth()

    return chip_node_list


def generate_sequence_recursive(open_position: int, chips: Set[Chip], heuristic_value_per_chip: int = 0, max_depth: int = math.inf) -> Optional[ChipNode]:
    if not chips or max_depth <= 0:
        return None

    max_value = -math.inf
    best_chip_node = None

    for chip in chips:
        if open_position in chip:
            new_chips = chips.copy()
            new_chips.remove(chip)
            new_value = chip.get_value() + heuristic_value_per_chip
            sequence2 = None
            depth_step = 0 if chip.is_double() else 1

            sequence = generate_sequence_recursive(chip.get_other_side(open_position), new_chips, heuristic_value_per_chip, max_depth - depth_step)

            if sequence:
                new_value += sequence.get_chain_weighted_value() * front_loaded_index
                if chip.is_double():
                    new_chips -= sequence.get_chipset()
                    sequence2 = generate_sequence_recursive(chip.get_side_a(), new_chips, heuristic_value_per_chip, max_depth - sequence.get_depth())
                    if sequence2:
                        new_value += sequence2.get_chain_weighted_value() * front_loaded_index

            if new_value > max_value:
                max_value = new_value
                best_chip_node = ChipNode(chip, open_position, heuristic_value_per_chip)
                best_chip_node.add_next_node(sequence)
                best_chip_node.add_next_node(sequence2)

    return best_chip_node
