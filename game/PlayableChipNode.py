from game import ChipNode


class PlayableChipNode:

    def __init__(self, chip_node: ChipNode, row: int) -> None:
        self.chip_node = chip_node
        self.row = row

    def get_chip_node(self) -> ChipNode:
        return self.chip_node

    def get_row(self) -> int:
        return self.row
