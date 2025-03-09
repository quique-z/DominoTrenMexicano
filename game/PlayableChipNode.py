from typing import Set

from game import ChipNode
from game.RevealedChip import RevealedChip


class PlayableChipNode:

    def __init__(self, chip_node: ChipNode, row: int) -> None:
        self.chip_node = chip_node
        self.row = row

    def get_chip_node(self) -> ChipNode:
        return self.chip_node

    def get_row(self) -> int:
        return self.row

    def ends_in_double(self) -> bool:
        return len(self.chip_node.get_ending_doubles()) > 0

    def get_ending_doubles(self) -> Set[int]:
        return self.chip_node.get_ending_doubles()

    def get_chipset(self) -> Set[RevealedChip]:
        return self.chip_node.get_chipset()

    def __str__(self) -> str:
        return f"On row {self.row} I play {self.chip_node}"
