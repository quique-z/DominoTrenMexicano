from DominoCubano.game.Chip import *


def create_chips(highest_double):
    chips = []
    for i in range(highest_double + 1):
        for j in range(i, highest_double + 1):
            f = Chip(i, j)
            chips.append(f)
    return chips


def create_chips_without_double(highest_double, double_to_skip):
    chips = []
    for i in range(highest_double + 1):
        for j in range(i, highest_double + 1):
            if not (i == double_to_skip and j == double_to_skip):
                f = Chip(i, j)
                chips.append(f)
    return chips
