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
        return best_chip_node.get_next_piece()

    def has_chip_to_play(self):
        return len(self.chip_nodes) > 0

    def remove_node(self, chip_node):
        self.chip_nodes.remove(chip_node)
        tail = chip_node.get_tail()
        if tail is not None:
            self.chip_nodes.extend(tail)

    def __len__(self):
        return len(self.chip_nodes)

    def __str__(self):
        s = []
        for i in self.chip_nodes:
            s.append(i.__str__())
        return ''.join(s)
