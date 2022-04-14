from game import ChipFactory
from game.Chip import Chip


class ProbabilityMap:
    def __init__(self, highest_double, double_to_skip):
        self.highest_double = highest_double
        self.probability_map = dict()
        # Nth +1 triangular number minus the double to skip
        self.n_of_chips = (highest_double + 2) * (highest_double + 1) / 2 - 1
        for chip in ChipFactory.create_chips(highest_double, double_to_skip):
            self.probability_map[chip] = [self.n_of_chips, self.n_of_chips]

    def __int__(self, other):
        self.highest_double = other.highest_double
        self.probability_map = other.probability_map.copy()
        self.n_of_chips = other.n_of_chips

    def get_probability_for_chip(self, a, b):
        fraction = self.probability_map[Chip(a, b)]
        return fraction[0]/fraction[1]

    def set_zero_probability_for_chip(self, chip):
        self.probability_map[chip] = [0, -1]

    def get_probability_numerator_for_chip(self, a, b):
        fraction = self.probability_map[Chip(a, b)]
        return fraction[0]

    def get_probability_denominator_for_chip(self, a, b):
        fraction = self.probability_map[Chip(a, b)]
        return fraction[1]

    def get_probability_for_number(self, n):
        chips = ChipFactory.create_chips_with_specific_number(n, self.highest_double)
        inverse_probability = 1
        total_probability = 0

        for chip in chips:
            probability = self.get_probability_for_chip(chip)
            inverse_probability *= 1 - probability
            total_probability += (1 - total_probability) * probability

        # Sanity check, they should be the same
        return [total_probability, 1 - inverse_probability]

    def remove_chip_from_probability_map(self, chip_to_update):
        self.probability_map.pop(chip_to_update)

        for key in self.probability_map.keys():
            fraction = self.probability_map.get(key)
            numerator = fraction[0]
            denominator = fraction[1]
            if numerator != 0 and denominator != 1:
                denominator -= 1
                self.probability_map[key] = [numerator, denominator]

        total_chip_value = 0
        for fraction in self.probability_map.items():
            numerator = fraction[0]
            denominator = fraction[1]
            if numerator != 0:
                total_chip_value += numerator/denominator

        if total_chip_value / self.n_of_chips < 0.99 or total_chip_value / self.n_of_chips > 1.01:
            raise Exception("Did some funky math")
