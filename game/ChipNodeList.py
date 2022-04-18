import math


class ChipNodeList:

    def __init__(self):
        self.chip_nodes = []

    def add(self, chip_node):
        if chip_node is None:
            return
        self.chip_nodes.append(chip_node)

    def get_best_chip_to_play(self):
        max_value = -math.inf
        best_chip_node = None
        for cn in self.chip_nodes:
            if cn.get_next_piece_value() > max_value:
                max_value = cn.get_next_piece_value()
                best_chip_node = cn
        self.remove_node(best_chip_node)
        return best_chip_node

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
                if cn.get_chip_side_to_play() == number and cn.get_next_piece_value() > max_value:
                    max_value = cn.get_next_piece_value()
                    best_chip_node = cn
        self.remove_node(best_chip_node)
        return best_chip_node

    def has_chip_to_play(self):
        return len(self.chip_nodes) > 0

    def remove_node(self, chip_node):
        self.chip_nodes.remove(chip_node)
        tail = chip_node.get_tail()
        if tail is not None:
            self.chip_nodes.extend(tail)

    def get_chipset_length(self):
        return len(self.get_chipset())

    def get_chipset(self):
        chipset = []
        for cn in self.chip_nodes:
            chipset.extend(cn.get_chipset())
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

    def __len__(self):
        return len(self.chip_nodes)

    def __str__(self):
        s = []
        for cn in self.chip_nodes:
            s.append(cn.__str__())
        return ''.join(s)
