class Row:

    def __init__(self, index, center_double):
        self.index = index
        self.open_positions = [center_double]
        self.train = False
        self.has_chip_been_played = True

    def set_train(self):
        self.train = True

    def remove_train(self):
        self.train = False

    def has_train(self):
        return self.train

    def get_open_positions(self):
        return self.open_positions

    def add_open_positions(self, open_positions):
        self.open_positions.append(open_positions)
        self.has_chip_been_played = False

    def remove_open_positions(self, open_positions):
        self.open_positions.remove(open_positions)

    def swap_open_positions(self, remove, open_positions):
        self.open_positions.remove(remove)
        self.open_positions.append(open_positions)
        self.has_chip_been_played = False

    def get_index(self):
        return self.index

    def is_free(self):
        return self.has_chip_been_played

    def __str__(self):
        s = []
        for i in self.open_positions:
            s.append("%s " % i)
        return ''.join(s)
