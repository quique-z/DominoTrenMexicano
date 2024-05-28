from typing import Self

from game.Chip import Chip


class HiddenChip(Chip):

    def __contains__(self, n: int) -> bool:
        return False

    def __eq__(self, other: Self) -> bool:
        if not isinstance(other, Chip):
            return NotImplemented
        return False

    def __str__(self) -> str:
        return "Hidden chip with unknown contents."
