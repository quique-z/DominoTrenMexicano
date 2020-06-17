import math
from ai.ChipNode import ChipNode


def generate_sequence3(open_positions, chips, heuristic_value_per_chip, steps):
    print("Sequence generation %s" % steps)
    if chips is None or len(chips) == 0 or open_positions is None or len(open_positions) == 0:
        return None
    max_value = -math.inf
    best_sequence = None
    best_chip = None
    best_open_position = None

    for open_position in open_positions:
        chips_to_play = []

        for chip in chips:
            if chip.__contains__(open_position):
                chips_to_play.append(chip)

        for chip in chips_to_play:
            new_chips = chips.copy()
            new_chips.remove(chip)
            new_open_positions = open_positions.copy()

            if chip.is_double():
                new_open_positions.append(open_position)
            else:
                new_open_positions.remove(open_position)
                new_open_positions.append(chip.get_other_side(open_position))

            chip_sequence = generate_sequence(new_open_positions, new_chips, heuristic_value_per_chip, steps + 1)

            if chip_sequence is None:
                if chip.get_value() > max_value:
                    max_value = chip.get_value()
                    best_sequence = None
                    best_chip = chip
                    best_open_position = open_position
            elif chip_sequence.get_value() + chip.get_value() > max_value:
                max_value = chip_sequence.get_value() + chip.get_value()
                best_sequence = chip_sequence
                best_chip = chip
                best_open_position = open_position

    if best_chip is None:
        return None

    chip_node = ChipNode(best_chip, best_open_position, heuristic_value_per_chip)
    if best_sequence is not None:
        chip_node.add_next(best_sequence)

    return chip_node


def generate_sequence(open_positions, chips, heuristic_value_per_chip):
    chip_node_list = []
    new_chips = chips.copy()

    for open_position in open_positions:
        sequence = generate_sequence_recursive(open_position, new_chips, heuristic_value_per_chip)
        if sequence is not None:
            chip_node_list.append(sequence)
            new_chips.remove(sequence.get_chipset())
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
                best_chip = ChipNode(chip)
                best_chip.add_next(sequence)

            if chip.is_double():
                if sequence is not None:
                    new_chips.remove(sequence.get_chipset())
                    sequence2 = generate_sequence_recursive(chip.get_side_a(), new_chips, heuristic_value_per_chip)
                    best_chip.add_next(sequence2)
                break

    return best_chip
