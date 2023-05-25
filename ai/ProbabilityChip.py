class ProbabilityChip:

    def __init__(self, chips, highest_double):
        self.chips = chips
        self.highest_double = highest_double

    def contains_chip(self, chip):
        return chip in self.chips

    def contains_number(self, number):
        for chip in self.chips:
            if number in chip:
                return True
        return False

    def get_chip_count(self):
        return len(self.chips)

    def remove_numbers(self, numbers):
        for chip in self.chips:
            for n in numbers:
                if chip.__contains__(n):
                    self.chips.remove(chip)
                    continue


