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
        return cn.get_next_piece()

    def remove_node(self, chip_node):
        self.chip_nodes.remove(chip_node)
        self.chip_nodes.extend(chip_node.get_tail())

    def __len__(self):
        return len(self.chip_nodes)

    def __str__(self):
        s = []
        for i in self.chip_nodes:
            s.append(i.__str__())
        return ''.join(s)
