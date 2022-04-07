class ChipNode:

    def __init__(self, chip, side_to_play, heuristic_value_per_chip=0):
        self.next = None
        self.next2 = None
        self.chip = chip
        self.chipset = [chip]
        self.side_to_play = side_to_play
        self.value = chip.get_value() + heuristic_value_per_chip
        self.double = chip.is_double()

    def add_next_node(self, chip_node):
        if chip_node is None:
            return
        self.value += chip_node.get_chip_value()
        self.chipset.extend(chip_node.get_chipset())

        if self.double and self.next is not None:
            self.next2 = chip_node
        else:
            self.next = chip_node

    def get_next_piece_value(self):
        next_value = 0
        if self.is_chip_double():
            if self.next is not None:
                next_value = self.next.get_next_piece_value()
            if self.next2 is not None and self.next2.get_next_piece_value() > next_value:
                next_value = self.next.get_next_piece_value()
        next_value += self.chip.get_value()
        return next_value

    def get_next_piece(self):
        next_chip = [self.chip]
        if self.is_chip_double():
            if self.next is not None:
                if self.next2 is not None and self.next2.get_next_piece_value() > self.next.get_next_piece_value():
                    next_chip.append(self.next2.get_chip())
                else:
                    next_chip.append(self.next.get_chip())
        return next_chip

    def get_tail(self):
        if self.next is None:
            return None

        if self.is_chip_double():
            if self.next2 is None:
                if self.next.next is None:
                    return None
                else:
                    return [self.next.next]
            elif self.next.get_next_piece_value() > self.next2.get_next_piece_value():
                if self.next.next is None:
                    return [self.next2]
                else:
                    return [self.next.next, self.next2]
            else:
                if self.next2.next is not None:
                    return [self.next2.next, self.next]

        return [self.next]

    def get_chain_value(self):
        return self.value

    def is_chip_double(self):
        return self.double

    def get_chip_side_to_play(self):
        return self.side_to_play

    def get_chipset(self):
        return self.chipset

    def get_chip(self):
        return self.chip

    def __contains__(self, value):
        if self.chip.__contains__(value):
            return True
        elif self.next is not None and self.next.__contains__(value):
            return True
        elif self.next2 is not None and self.next2.__contains__(value):
            return True
        return False

    def __str__(self):
        s = ["On position %s I play this chip: %s\n" % (self.side_to_play.__str__(), self.chip.__str__())]
        if self.next is not None:
            s.append(self.next.__str__())
        if self.next2 is not None:
            s.append(self.next2.__str__())
        return ''.join(s)
