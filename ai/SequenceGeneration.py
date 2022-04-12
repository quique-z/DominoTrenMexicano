import math
from ai.ChipNode import ChipNode
from ai.ChipNodeList import ChipNodeList


def generate_sequence(open_positions, chips, heuristic_value_per_chip=0, front_loaded_index=1):
    chip_node_list = ChipNodeList()
    new_chips = chips.copy()
    ready_to_exit = False
    positions_to_consider = open_positions.copy()

    while not ready_to_exit:
        ready_to_exit = True
        best_sequence = None
        best_open_position = None
        best_score = -math.inf

        for open_position in positions_to_consider:
            sequence = generate_sequence_recursive(open_position, new_chips, heuristic_value_per_chip, front_loaded_index)
            if sequence is not None and sequence.get_chain_value() > best_score:
                best_sequence = sequence
                best_open_position = open_position
                best_score = sequence.get_chain_value()
                ready_to_exit = False

        if best_sequence is not None:
            chip_node_list.add(best_sequence)
            new_chips = list(set(new_chips) - set(best_sequence.get_chipset()))
            positions_to_consider.remove(best_open_position)

    return chip_node_list


def generate_sequence_recursive(open_position, chips, heuristic_value_per_chip=0, front_loaded_index=1):
    if chips is None or len(chips) == 0:
        return None

    max_value = -math.inf
    best_chip = None

    for chip in chips:
        if chip.__contains__(open_position):
            new_chips = chips.copy()
            new_chips.remove(chip)
            new_value = chip.get_value() + heuristic_value_per_chip
            sequence2 = None

            sequence = generate_sequence_recursive(
                chip.get_other_side(open_position), new_chips, heuristic_value_per_chip, front_loaded_index)

            if sequence is not None:
                new_value += sequence.get_chain_value() * front_loaded_index
                if chip.is_double():
                    new_chips = list(set(new_chips) - set(sequence.get_chipset()))
                    sequence2 = generate_sequence_recursive(
                        chip.get_side_a(), new_chips, heuristic_value_per_chip, front_loaded_index)
                    if sequence2 is not None:
                        new_value += sequence2.get_chain_value() * front_loaded_index

            if new_value > max_value:
                max_value = new_value
                best_chip = ChipNode(chip, open_position, heuristic_value_per_chip)
                best_chip.add_next_node(sequence)
                best_chip.add_next_node(sequence2)

    return best_chip
