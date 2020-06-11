class ChipNode:

    def __init__(self, chip, side_to_play):
        self.next = None
        self.next2 = None
        self.chip = chip
        self.side_to_play = side_to_play
        self.value = chip.get_value()
        self.double = chip.is_double()

    def add_next(self, chip_node):
        self.value += chip_node.get_value()

        if self.double and self.next is None:
            self.next2 = chip_node
        else:
            self.next = chip_node

    def get_value(self):
        return self.value

    def is_double(self):
        return self.double

    def get_side_to_play(self):
        return self.side_to_play

    def __str__(self):
        s = ["En la posición %s juego la ficha %s\n" % (self.side_to_play.__str__(), self.chip.__str__())]
        if self.next is not None:
            s.append(self.next.__str__())
        if self.next2 is not None:
            s.append(self.next2.__str__())
        return ''.join(s)
