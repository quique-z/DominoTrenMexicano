class ChipSequence:

    def __init__(self, chip):
        self.parent = None
        self.next = None
        self.last = self
        self.chip = chip
        self.value = chip.get_value()
        self.is_double = chip.is_double()

    def add_next(self, chip_sequence):
        self.value += chip_sequence.get_value()
        chip_sequence.set_parent(self)

        if self.last == self:
            self.last = chip_sequence.get_last()
        else:
            self.last.append(chip_sequence.get_last())

        if self.is_double:
            if self.next is None:
                self.next = chip_sequence
                return
            else:
                self.next.append(chip_sequence)
                return

        self.next = chip_sequence

    def get_value(self):
        return self.value

    def set_parent(self, parent):
        self.parent = parent

    def get_last(self):
        return self.last

