import math
from ai.ChipNode import ChipNode


def generate_sequence(open_positions, chips):
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

            cs = generate_sequence(new_open_positions, new_chips)

            if cs is None:
                if chip.get_value() > max_value:
                    max_value = chip.get_value()
                    best_sequence = None
                    best_chip = chip
                    best_open_position = open_position
            elif cs.get_value() + chip.get_value() > max_value:
                max_value = cs.get_value() + chip.get_value()
                best_sequence = cs
                best_chip = chip
                best_open_position = open_position

    if best_chip is None:
        return None

    cn = ChipNode(best_chip, best_open_position)
    if best_sequence is not None:
        cn.add_next(best_sequence)

    return cn
