import random
from typing import List

from game.Chip import Chip
from game.HiddenChip import HiddenChip
from game.RevealedChip import RevealedChip


def create_chips(highest_double: int, human_game: bool, double_to_skip: int = -1) -> List[Chip]:
    return create_hidden_chips(highest_double, double_to_skip) if human_game else create_revealed_chips(highest_double, double_to_skip)


def create_hidden_chips(highest_double: int, double_to_skip: int = -1) -> List[HiddenChip]:
    # Nth +1 triangular number.
    count = (highest_double + 1) * (highest_double + 2) // 2

    if double_to_skip != -1:
        count -= 1

    return [HiddenChip() for _ in range(count)]


def create_revealed_chips(highest_double: int, double_to_skip: int = -1) -> List[RevealedChip]:
    chips = []
    for i in range(highest_double + 1):
        for j in range(i, highest_double + 1):
            if i == double_to_skip and j == double_to_skip:
                continue
            chips.append(RevealedChip([i, j]))

    random.shuffle(chips)
    return chips


def create_chips_with_specific_numbers(numbers: List[int], highest_double: int) -> List[RevealedChip]:
    chips = []
    for number in numbers:
        for i in range(highest_double + 1):
            chip = RevealedChip([i, number])
            if chip not in chips:
                chips.append(chip)
    return chips
