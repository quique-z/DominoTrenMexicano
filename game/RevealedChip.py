from typing import List

from game.Chip import Chip


class RevealedChip(Chip):

    def __init__(self, numbers: List[int]) -> None:
        super().__init__()
        if not numbers or len(numbers) != 2:
            raise Exception("A chip needs 2 numbers to be created.")

        for n in numbers:
            if not 0 <= n <= Chip.highest_possible_chip:
                raise Exception("Numbers in chip need to be between 0 and %s" % self.highest_possible_chip)

        self.numbers = numbers
        self.numbers.sort()

    def get_side_a(self) -> int:
        return self.numbers[0]

    def get_side_b(self) -> int:
        return self.numbers[1]

    def get_sides(self) -> List[int]:
        return [self.get_side_a()] if self.is_double() else self.numbers

    def get_other_side(self, n: int) -> int:
        if self.get_side_a() == n:
            return self.get_side_b()
        if self.get_side_b() == n:
            return self.get_side_a()
        raise Exception("This chip does not contain number %s" % n)

    def is_double(self) -> bool:
        return self.get_side_a() == self.get_side_b()

    def get_value(self) -> int:
        value = self.get_side_a() + self.get_side_b()
        return value if value > 0 else Chip.double_zero_value

    def __contains__(self, n: int) -> bool:
        return n in self.numbers

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Chip):
            return NotImplemented
        return self.get_side_a() == other.get_side_a() and self.get_side_b() == other.get_side_b()

    def __str__(self) -> str:
        return "[%s|%s]" % (self.get_side_a(), self.get_side_b())

    def __hash__(self) -> int:
        return hash(hash(self.get_side_a()) + hash(self.get_side_b()))
