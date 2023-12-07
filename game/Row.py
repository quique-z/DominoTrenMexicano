from typing import List

from game import Chip, ChipNode
from game.ChipNodeList import ChipNodeList


class Row:

    def __init__(self, index: int, center_double: int, name: str = None) -> None:
        self.name = name
        if not name:
            self.name = index.__str__()
        self.open_positions = [center_double]
        self.is_empty = True
        self.train = False
        self.index = index

    def set_train(self) -> None:
        self.train = True

    def remove_train(self) -> None:
        self.train = False

    def has_train(self) -> bool:
        return self.train

    def get_open_positions(self) -> List[int]:
        return self.open_positions

    def play_chip(self, chip: Chip, side_to_play: int) -> None:
        if side_to_play not in self.open_positions:
            raise Exception("% is not in row's open positions" % side_to_play)

        if not chip.is_double():
            self.open_positions.remove(side_to_play)

        self.open_positions.append(chip.get_other_side(side_to_play))
        self.is_empty = False

    def play_chip_node(self, chip_node: ChipNode) -> None:
        chip_node_list = ChipNodeList([chip_node])
        while chip_node_list.has_chip_to_play():
            cn = chip_node_list.get_best_chip_to_play()
            for chip in cn.get_next_move_as_chip_list():
                self.play_chip(chip, cn.get_chip_side_to_play())

    def get_index(self) -> int:
        return self.index

    def get_name(self) -> str:
        return self.name

    def can_play_many(self) -> bool:
        return self.is_empty

    def __str__(self) -> str:
        s = ["%s row's contents: " % self.name]
        for i in self.open_positions:
            s.append("%s " % i)
        if self.train:
            s.append("and has train")
        return ''.join(s)
