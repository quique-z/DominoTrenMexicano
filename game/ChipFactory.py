from typing import List

from game import Chip
from game.RevealedChip import RevealedChip


def create_chips(highest_double: int, double_to_skip: int = -1) -> List[Chip]:
    chips = []
    for i in range(highest_double + 1):
        for j in range(i, highest_double + 1):
            if not (i == double_to_skip and j == double_to_skip):
                chips.append(RevealedChip([i, j]))
    return chips


def create_chips_with_specific_numbers(numbers: List[int], highest_double: int) -> List[Chip]:
    chips = []
    for number in numbers:
        for i in range(highest_double + 1):
            chip = RevealedChip([i, number])
            if chip not in chips:
                chips.append(chip)
    return chips
