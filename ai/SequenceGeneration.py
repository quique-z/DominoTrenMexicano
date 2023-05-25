from game.ChipNodeList import ChipNodeList
from game.ChipNode import ChipNode
import math


def generate_sequence(open_positions, chips, heuristic_value_per_chip=0, front_loaded_index=1, max_depth=math.inf):
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
            sequence = generate_sequence_recursive(position, new_chips, heuristic_value_per_chip, front_loaded_index, max_depth)
            if sequence is not None and sequence.get_chain_value() > best_score:
                best_score = sequence.get_chain_value()
                best_open_position = position
                best_sequence = sequence
                ready_to_exit = False

        if best_sequence is not None:
            new_chips = list(set(new_chips) - set(best_sequence.get_chipset()))
            positions_to_consider.remove(best_open_position)
            chip_node_list.add(best_sequence)
            max_depth -= len(best_sequence)

    return chip_node_list


def generate_sequence_recursive(open_position, chips, heuristic_value_per_chip=0, front_loaded_index=1, max_depth=math.inf):
    if len(chips) == 0 or max_depth <= 0:
        return None

    max_value = -math.inf
    best_chip_node = None

    for chip in chips:
        if open_position in chip:
            new_chips = chips.copy()
            new_chips.remove(chip)
            new_value = chip.get_value() + heuristic_value_per_chip
            sequence2 = None
            depth_step = 1
            if chip.is_double():
                depth_step = 0

            sequence = generate_sequence_recursive(
                chip.get_other_side(open_position), new_chips, heuristic_value_per_chip, front_loaded_index, max_depth - depth_step)

            if sequence is not None:
                new_value += sequence.get_chain_value() * front_loaded_index
                if chip.is_double():
                    new_chips = list(set(new_chips) - set(sequence.get_chipset()))
                    sequence2 = generate_sequence_recursive(
                        chip.get_side_a(), new_chips, heuristic_value_per_chip, front_loaded_index, max_depth - len(sequence) - 1)
                    if sequence2 is not None:
                        new_value += sequence2.get_chain_value() * front_loaded_index

            if new_value > max_value:
                max_value = new_value
                best_chip_node = ChipNode(chip, open_position, heuristic_value_per_chip)
                best_chip_node.add_next_node(sequence)
                best_chip_node.add_next_node(sequence2)

    return best_chip_node


def generate_sequence_recursive2(open_positions, chips, heuristic_value_per_chip=0, front_loaded_index=1, max_depth=math.inf):
    if len(chips) == 0 or max_depth <= 0:
        return None

    for open_position in open_positions:
        for chip in chips:
            if chip.is_double() and open_position in chip:
                pass

    max_value = -math.inf
    best_chip_node = None

    for chip in chips:
        for open_position in open_positions:
            if open_position in chip:
                new_chips = chips.copy()
                new_chips.remove(chip)
                new_value = chip.get_value() + heuristic_value_per_chip
                sequence2 = None
                depth_step = 1
                if chip.is_double():
                    depth_step = 0

                sequence = generate_sequence_recursive2(
                    chip.get_other_side(open_position), new_chips, heuristic_value_per_chip, front_loaded_index, max_depth - depth_step)

                if sequence is not None:
                    new_value += sequence.get_chain_value() * front_loaded_index
                    if chip.is_double():
                        new_chips = list(set(new_chips) - set(sequence.get_chipset()))
                        sequence2 = generate_sequence_recursive2(
                            chip.get_side_a(), new_chips, heuristic_value_per_chip, front_loaded_index, max_depth - len(sequence) - 1)
                        if sequence2 is not None:
                            new_value += sequence2.get_chain_value() * front_loaded_index

                if new_value > max_value:
                    max_value = new_value
                    best_chip_node = ChipNode(chip, open_position, heuristic_value_per_chip)
                    best_chip_node.add_next_node(sequence)
                    best_chip_node.add_next_node(sequence2)

    return best_chip_node
