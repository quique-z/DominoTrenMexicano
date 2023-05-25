import math

from ai.ProbabilityChip import ProbabilityChip


class ProbabilityChipList:

    def __init__(self, chips, n_chips_to_draw, highest_double):
        self.probability_chips = [ProbabilityChip(chips, highest_double)] * n_chips_to_draw
        self.highest_double = highest_double

    def add(self, probability_chip):
        self.probability_chips.append(probability_chip)

    def remove(self, chip):
        smallest_pc = None
        smallest_count = math.inf

        for pc in self.probability_chips:
            if pc.contains_chip(chip) and pc.get_chip_count() < smallest_count:
                smallest_pc = pc
                smallest_count = pc.get_chip_count()

        self.probability_chips.remove(smallest_pc)

    def remove_numbers(self, numbers):
        for pc in self.probability_chips:
            pc.remove_numbers(numbers)

    def get_possible_numbers(self):
        numbers = set()
        for pc in self.probability_chips:
            for i in range(self.highest_double):
                if pc.contains_number(i):
                    numbers.add(i)
        return numbers

    def get_non_available_numbers(self):
        return set(range(self.highest_double)) - self.get_possible_numbers()

    def get_stakes_in_chip(self, chip):
        count = 0
        for pc in self.probability_chips:
            if pc.contains_chip(chip):
                count += 1
        return count

    def pop(self):
        return self.probability_chips.pop()
