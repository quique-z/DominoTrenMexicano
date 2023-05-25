import logging
import math


class ChipNodeList:

    def __init__(self, chip_nodes=None):
        self.chip_nodes = chip_nodes
        if chip_nodes is None:
            self.chip_nodes = []

        self.sanity_check()

    def add(self, chip_node):
        if chip_node is None:
            return
        self.chip_nodes.append(chip_node)
        self.sanity_check()

    def get_best_chip_to_play(self):
        max_value = -math.inf
        best_chip_node = None
        for cn in self.chip_nodes:
            if cn.get_next_move_value() > max_value:
                max_value = cn.get_next_move_value()
                best_chip_node = cn
        self.remove_node(best_chip_node)
        self.sanity_check()
        return best_chip_node.get_next_move_as_node()

    def has_number_to_play_immediately(self, numbers):
        for cn in self.chip_nodes:
            for number in numbers:
                if cn.get_chip_side_to_play() == number:
                    return True
        return False

    def get_best_numbered_chip_to_play(self, numbers):
        max_value = -math.inf
        best_chip_node = None
        for cn in self.chip_nodes:
            for number in numbers:
                if cn.get_chip_side_to_play() == number and cn.get_next_move_value() > max_value:
                    max_value = cn.get_next_move_value()
                    best_chip_node = cn
        self.remove_node(best_chip_node)
        self.sanity_check()
        return best_chip_node.get_next_move_as_node()

    def has_double_to_play_immediately(self):
        for cn in self.chip_nodes:
            if cn.is_chip_double():
                return True
        return False

    def ends_in_double(self):
        return len(self.get_ending_doubles()) > 0

    def get_ending_doubles(self):
        doubles = []
        for cn in self.chip_nodes:
            doubles += cn.get_ending_doubles()
        return doubles

    def has_chip_to_play(self):
        return len(self.chip_nodes) > 0

    def remove_node(self, chip_node):
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
        if tail is not None:
            self.chip_nodes += tail
        self.sanity_check()

    def get_chipset(self):
        chipset = []
        for cn in self.chip_nodes:
            chipset += cn.get_chipset()
        return chipset

    def get_chipset_value(self):
        value = 0
        for cn in self.chip_nodes:
            for chip in cn.get_chipset():
                value += chip.get_value()
        return value

    def get_chipset_weighted_value(self):
        value = 0
        for cn in self.chip_nodes:
            value += cn.get_chain_value()
        return value

    def sanity_check(self):
        for cn in self.chip_nodes:
            cn.get_chip()

    def __copy__(self):
        cnl = ChipNodeList()
        for cn in self.chip_nodes:
            cnl.add(cn.__copy__())
        return cnl

    def __len__(self):
        length = 0
        for cn in self.chip_nodes:
            length += len(cn)
        return length

    def __str__(self):
        s = []
        for cn in self.chip_nodes:
            s.append(cn.__str__())
        return ''.join(s)
