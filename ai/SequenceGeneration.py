import math


def generate_sequence(open_position, chips, heuristic_value_per_chip):
    max_value = -math.inf
    for chip in chips:
        new_list = chips.copy()
        new_list.remove(chip)
        other_side = chip.get_other_side(open_position)
        sequence_value = generate_sequence(other_side, new_list, heuristic_value_per_chip)
        if sequence_value > max_value:
            max_value = sequence_value
    return max_value
