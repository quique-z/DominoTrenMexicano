from typing import List

from game import ChipNode


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

    def get_ending_doubles(self) -> List[int]:
        return self.chip_node.get_ending_doubles()

    def __str__(self) -> str:
        return "On row %s I play %s" % (self.row, self.chip_node.__str__())
