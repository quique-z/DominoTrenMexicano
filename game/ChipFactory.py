import random
from typing import List

from game.Chip import Chip
from game.HiddenChip import HiddenChip
from game.RevealedChip import RevealedChip


def create_chips(highest_double: int, double_to_skip: int = -1, human_game: bool = False) -> List[Chip]:
    return create_hidden_chips(highest_double, double_to_skip) if human_game else create_revealed_chips(highest_double, double_to_skip)

def create_hidden_chips(highest_double: int, double_to_skip: int = -1) -> List[HiddenChip]:
    # Nth +1 triangular number.
    skip = 0 if double_to_skip == -1 else 1
    return [HiddenChip() for _ in range((highest_double + 1) * (highest_double + 2) // 2 - skip)]

def create_revealed_chips(highest_double: int, double_to_skip: int = -1) -> List[RevealedChip]:
    chips = [RevealedChip([i, j]) for i in range(highest_double + 1) for j in range(i, highest_double + 1) if not (i == double_to_skip == j)]
    random.shuffle(chips)
    return chips

def create_chips_with_specific_numbers(numbers: List[int], highest_double: int) -> List[RevealedChip]:
    return [RevealedChip([i, number]) for number in numbers for i in range(highest_double + 1)]
