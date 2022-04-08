class Chip:

    def __init__(self, a, b):
        self.numbers = [a, b]

    def get_side_a(self):
        return self.numbers[0]

    def get_side_b(self):
        return self.numbers[1]

    def get_other_side(self, n):
        if self.get_side_a() == n:
            return self.get_side_b()
        if self.get_side_b() == n:
            return self.get_side_a()
        raise Exception("This chip does not contain number %s" % n)

    def is_double(self):
        return self.get_side_a() == self.get_side_b()

    def get_value(self):
        if self.get_side_a() == 0 and self.get_side_b() == 0:
            return 50
        else:
            return self.get_side_a() + self.get_side_b()

    def __contains__(self, n):
        return self.numbers.__contains__(n)

    def __eq__(self, other):
        return self.get_side_a() == other.get_side_a() and self.get_side_b() == other.get_side_b()

    def __str__(self):
        return "[%s|%s]" % (self.get_side_a(), self.get_side_b())

    def __hash__(self):
        return hash(hash(self.get_side_a()) + hash(self.get_side_b()))
