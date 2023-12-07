from typing import List


class Chip:
    double_zero_value = 50
    highest_possible_chip = 15

    def get_side_a(self) -> int:
        pass

    def get_side_b(self) -> int:
        pass

    def get_sides(self) -> List[int]:
        pass

    def get_other_side(self, n: int) -> int:
        pass

    def is_double(self) -> bool:
        pass

    def get_value(self) -> int:
        pass

    def __contains__(self, n: int) -> bool:
        return NotImplemented

    def __eq__(self, other: object) -> bool:
        return NotImplemented

    def __str__(self) -> str:
        return NotImplemented

    def __hash__(self) -> int:
        return NotImplemented
