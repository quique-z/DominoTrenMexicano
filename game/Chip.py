from typing import Self, Set


class Chip:
    double_zero_value = 50
    highest_possible_chip = 15

    def get_side_a(self) -> int:
        return NotImplemented

    def get_side_b(self) -> int:
        return NotImplemented

    def get_sides(self) -> Set[int]:
        return NotImplemented

    def get_other_side(self, n: int) -> int:
        return NotImplemented

    def is_double(self) -> bool:
        return NotImplemented

    def get_value(self) -> int:
        return NotImplemented

    def __contains__(self, n: int) -> bool:
        return NotImplemented

    def __eq__(self, other: Self) -> bool:
        return NotImplemented

    def __str__(self) -> str:
        return NotImplemented

    def __hash__(self) -> int:
        return NotImplemented
