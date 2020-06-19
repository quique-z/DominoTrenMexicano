import math
from ai.ChipNode import ChipNode
from ai.ChipNodeList import ChipNodeList


def generate_sequence(open_positions, chips, heuristic_value_per_chip):
    chip_node_list = ChipNodeList()
    new_chips = chips.copy()

    for open_position in open_positions:
        sequence = generate_sequence_recursive(open_position, new_chips, heuristic_value_per_chip)
        if sequence is not None:
            chip_node_list.add(sequence)
            new_chips = list(set(new_chips)-set(sequence.get_chipset()))
    return chip_node_list


def generate_sequence_recursive(open_position, chips, heuristic_value_per_chip):
    if chips is None or len(chips) == 0:
        return None

    max_value = -math.inf
    best_chip = None

    for chip in chips:
        if chip.__contains__(open_position):
            new_chips = chips.copy()
            new_chips.remove(chip)
            new_value = chip.get_value() + heuristic_value_per_chip

            sequence = generate_sequence_recursive(
                chip.get_other_side(open_position), new_chips, heuristic_value_per_chip)

            if sequence is not None:
                new_value += sequence.get_value()
            if new_value > max_value:
                max_value = new_value
                best_chip = ChipNode(chip, open_position, heuristic_value_per_chip)
                best_chip.add_next(sequence)

            if chip.is_double():
                if sequence is not None:
                    new_chips = list(set(new_chips)-set(sequence.get_chipset()))
                    sequence2 = generate_sequence_recursive(chip.get_side_a(), new_chips, heuristic_value_per_chip)
                    best_chip.add_next(sequence2)
                break

    return best_chip
