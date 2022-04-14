from game.Chip import Chip


def create_chips(highest_double, double_to_skip=-1):
    chips = []
    for i in range(highest_double + 1):
        for j in range(i, highest_double + 1):
            if not (i == double_to_skip and j == double_to_skip):
                chips.append(Chip(i, j))
    return chips


def create_chips_with_specific_number(number, highest_double):
    chips = []
    for i in range(highest_double + 1):
        chips.append(Chip(number, i))
    return chips
