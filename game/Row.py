class Row:

    def __init__(self, index, center_double, name):
        self.index = index
        self.open_positions = [center_double]
        self.train = False
        self.is_empty = True
        self.name = name

    def set_train(self):
        self.train = True

    def remove_train(self):
        self.train = False

    def has_train(self):
        return self.train

    def get_open_positions(self):
        return self.open_positions

    def add_open_positions(self, n):
        self.open_positions.append(n)
        self.is_empty = False

    def remove_open_positions(self, n):
        self.open_positions.remove(n)

    def swap_open_positions(self, remove, add):
        self.open_positions.remove(remove)
        self.open_positions.append(add)
        self.is_empty = False

    def get_index(self):
        return self.index

    def get_name(self):
        return self.name

    def can_play_many(self):
        return self.is_empty

    def __str__(self):
        s = ["Row %s, contents: " % self.name]
        for i in self.open_positions:
            s.append("%s " % i)
        return ''.join(s)
