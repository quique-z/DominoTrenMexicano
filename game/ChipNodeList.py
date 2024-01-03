import logging
import math
from typing import List, Set

from game import ChipNode, Chip


class ChipNodeList:

    def __init__(self, chip_nodes: List[ChipNode] = None) -> None:
        self.chip_nodes = chip_nodes
        if not chip_nodes:
            self.chip_nodes = []

    def add(self, chip_node: ChipNode) -> None:
        if not chip_node:
            return
        self.chip_nodes.append(chip_node)

    def get_best_chip_to_play(self) -> ChipNode:
        max_value = -math.inf
        best_chip_node = None
        for cn in self.chip_nodes:
            if cn.get_next_move_value() > max_value:
                max_value = cn.get_next_move_value()
                best_chip_node = cn
        self.remove_node_keep_tail(best_chip_node)
        return best_chip_node.get_next_move_as_node()

    def has_number_to_play_immediately(self, numbers: Set[int]) -> bool:
        for cn in self.chip_nodes:
            if cn.get_chip_side_to_play() in numbers:
                return True
        return False

    def get_best_numbered_chip_to_play(self, numbers: Set[int]) -> ChipNode:
        max_value = -math.inf
        best_chip_node = None
        for cn in self.chip_nodes:
            if cn.get_chip_side_to_play() in numbers and cn.get_next_move_value() > max_value:
                max_value = cn.get_next_move_value()
                best_chip_node = cn
        self.remove_node_keep_tail(best_chip_node)
        return best_chip_node.get_next_move_as_node()

    def get_all_chips(self) -> ChipNode:
        if len(self.chip_nodes) != 1:
            raise Exception("Can only play all chips if root is a single element.")
        chip_node = self.chip_nodes[0]
        self.chip_nodes = []
        return chip_node

    def get_all_chips_minus_last(self) -> ChipNode:
        chip_node = self.get_all_chips()
        last = chip_node.get_last()
        self.chip_nodes = [last]
        chip_node.remove_chip_from_tail(last.get_chip())
        return chip_node

    def has_chip_to_play(self) -> bool:
        return len(self.chip_nodes) > 0

    def remove_node_keep_tail(self, chip_node: ChipNode) -> None:
        removed = False

        for cn in self.chip_nodes:
            if cn.get_chip() == chip_node.get_chip():
                self.chip_nodes.remove(cn)
                removed = True
                break

        if not removed:
            logging.info("Trying to remove %s from %s." % (chip_node.__str__(), self.__str__()))
            raise Exception("Can't remove non-present node.")

        tail = chip_node.get_tail()
        if tail:
            self.chip_nodes.extend(tail)

    def get_chipset(self) -> Set[Chip]:
        chipset = set()
        for cn in self.chip_nodes:
            chipset.update(cn.get_chipset())
        return chipset

    def get_chipset_value(self) -> int:
        value = 0
        for chip in self.get_chipset():
            value += chip.get_value()
        return value

    def get_chipset_weighted_value(self) -> int:
        value = 0
        for cn in self.chip_nodes:
            value += cn.get_chain_weighted_value()
        return value

    def __len__(self) -> int:
        return len(self.get_chipset())

    def __str__(self) -> str:
        s = []
        for cn in self.chip_nodes:
            s.append(cn.__str__())
        return ''.join(s)
