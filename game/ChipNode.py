from game.Chip import Chip


class ChipNode:

    def __init__(self, chip, side_to_play, heuristic_value_per_chip=0):
        self.next = None
        self.next2 = None
        self.chip = chip
        self.side_to_play = side_to_play
        self.value = chip.get_value() + heuristic_value_per_chip

    def add_next_node(self, chip_node):
        if chip_node is None:
            return

        if not (self.next is None or (self.is_chip_double() and self.next2 is None)):
            raise Exception("Can't add a node, next is already occupied.")

        if chip_node.get_chip_side_to_play() != self.chip.get_other_side(self.side_to_play):
            raise Exception("Can't add a node, next chip's number does not match this chip's other side.")

        if self.is_chip_double() and self.next is not None:
            self.next2 = chip_node
        else:
            self.next = chip_node

    def override_next_node(self, chip_node):
        self.next = None
        self.next2 = None
        self.add_next_node(chip_node)

    def get_next_move_value(self):
        next_value = self.chip.get_value()
        if self.is_chip_double() and self.next is not None:
            if self.next2 is not None and self.next2.get_next_move_value() > self.next.get_next_move_value():
                next_value += self.next2.get_next_move_value()
            else:
                next_value += self.next.get_next_move_value()
        return next_value

    def get_next_move_as_chip_list(self):
        next_chip = [self.chip]
        if self.is_chip_double() and self.next is not None:
            if self.next2 is not None and self.next2.get_next_move_value() > self.next.get_next_move_value():
                next_chip.append(self.next2.get_chip())
            else:
                next_chip.append(self.next.get_chip())
        return next_chip

    def get_next_move_as_node(self):
        next_node = ChipNode(self.chip, self.side_to_play)
        if self.is_chip_double() and self.next is not None:
            if self.next2 is not None and self.next2.get_next_move_value() > self.next.get_next_move_value():
                next_node.add_next_node(ChipNode(self.next2.get_chip(), self.side_to_play))
            else:
                next_node.add_next_node(ChipNode(self.next.get_chip(), self.side_to_play))
        return next_node

    def get_tail(self):
        if self.next is None:
            return None

        if self.is_chip_double():
            if self.next2 is None:
                if self.next.next is None:
                    return None
                else:
                    return [self.next.next]
            elif self.next.get_next_move_value() > self.next2.get_next_move_value():
                if self.next.next is None:
                    return [self.next2]
                else:
                    return [self.next.next, self.next2]
            else:
                if self.next2.next is not None:
                    return [self.next2.next, self.next]

        return [self.next]

    def is_chip_double(self):
        return self.chip.is_double()

    def get_chip_side_to_play(self):
        return self.side_to_play

    def get_chip(self):
        return self.chip

    def get_chipset(self):
        chipset = [self.chip]
        if self.next is not None:
            chipset += self.next.get_chipset()
        if self.next2 is not None:
            chipset += self.next2.get_chipset()
        return chipset

    def get_chain_value(self):
        value = self.value
        if self.next is not None:
            value += self.next.get_chain_value()
        if self.next2 is not None:
            value += self.next2.get_chain_value()
        return value

    def get_ending_doubles(self):
        doubles = []
        if self.is_chip_double() and self.next is None and self.next2 is None:
            doubles.append(self.get_chip_side_to_play())
        if self.next is not None:
            doubles += self.next.get_ending_doubles()
        if self.next2 is not None:
            doubles += self.next2.get_ending_doubles()
        return doubles

    def __contains__(self, value):
        if value in self.chip:
            return True
        if self.next is not None and value in self.next:
            return True
        if self.next2 is not None and value in self.next2:
            return True
        return False

    def __copy__(self):
        cn = ChipNode(self.chip, self.side_to_play)
        if self.next is not None:
            cn.add_next_node(self.next.__copy__())
        if self.next2 is not None:
            cn.add_next_node(self.next2.__copy__())
        return cn

    def __len__(self):
        length = 1
        if self.next is not None:
            length += len(self.next)
        if self.next2 is not None:
            length += len(self.next2)
        return length

    def __str__(self):
        s = ["On position %s I play this chip: %s\n" % (self.side_to_play.__str__(), self.chip.__str__())]
        if self.next is not None:
            s.append(self.next.__str__())
        if self.next2 is not None:
            s.append(self.next2.__str__())
        return ''.join(s)


def chip_node_from_string(string, number):
    if not string:
        return None

    cn = ChipNode(Chip(string[0].split(",")), number)
    cn.next = chip_node_from_string(string[1:], number)

    return cn
