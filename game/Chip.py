class Chip:

    def __init__(self, a, b):
        self.numbers = [a, b]

    def get_side_a(self):
        return self.numbers[0]

    def get_side_b(self):
        return self.numbers[1]

    def get_other_side(self, n):
        if self.numbers[0] == n:
            return self.numbers[1]
        if self.numbers[1] == n:
            return self.numbers[0]
        raise Exception("This chip does not contain number %s" % n)

    def is_double(self):
        return self.get_side_a() == self.get_side_b()

    def get_value(self):
        if self.numbers[0] == 0 and self.numbers[1] == 0:
            return 50
        else:
            return self.numbers[0] + self.numbers[1]

    def __contains__(self, n):
        return self.numbers.__contains__(n)

    def __eq__(self, other):
        return self.get_side_a() == other.get_side_a() and self.get_side_b() == other.get_side_b()

    def __str__(self):
        return "[%s|%s]" % (self.numbers[0], self.numbers[1])

    def __hash__(self):
        return hash(hash(self.numbers[0]) + hash(self.numbers[1]))
