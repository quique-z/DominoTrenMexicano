from fractions import Fraction
from game import ChipFactory


class ProbabilityMap:
    def __init__(self, highest_double, double_to_skip, is_initial_pool=False):
        self.highest_double = highest_double
        self.probability_map = dict()
        # Nth +1 triangular number minus one for the double to skip
        self.n_of_chips = (highest_double + 2) * (highest_double + 1) / 2 - 1

        if is_initial_pool:
            for chip in ChipFactory.create_chips(highest_double, double_to_skip):
                self.probability_map[chip] = Fraction(1)  # [self.n_of_chips, self.n_of_chips]

    def get_possible_chips(self):
        return self.probability_map.keys()

    def get_probability_for_chip(self, chip):
        if self.probability_map.__contains__(chip):
            return self.probability_map[chip].__float__()
        return 0

    def get_probability_fraction_for_chip(self, chip):
        if self.probability_map.__contains__(chip):
            return self.probability_map[chip]
        return 0

    def get_probability_for_number(self, n):
        numbered_chips = ChipFactory.create_chips_with_specific_number(n, self.highest_double)
        inverse_probability = Fraction(1)

        for chip in numbered_chips:
            if self.probability_map.__contains__(chip):
                chip_probability = self.get_probability_fraction_for_chip(chip)
                inverse_probability *= 1 - chip_probability

        return [1 - inverse_probability.__float__()]

    def remove_chip_from_probability_map(self, chip):
        self.n_of_chips -= 1
        self.probability_map.pop(chip)
        self.decrease_denominator_on_all_chips()

    def remove_number_from_probability_map(self, n):
        numbered_chips = ChipFactory.create_chips_with_specific_number(n, self.highest_double)

        counter = 0
        for chip in numbered_chips:
            if self.probability_map.__contains__(chip):
                self.probability_map.pop(chip)
                counter += 1

        self.n_of_chips -= counter
        self.decrease_denominator_on_all_chips(counter)

    # TODO: This is wrong, figure it out.
    def decrease_denominator_on_all_chips(self, n=1):
        for key in self.probability_map.keys():
            fraction = self.probability_map.get(key)
            if fraction != 0:
                numerator = fraction.numerator * self.n_of_chips
                denominator = fraction.denominator * self.n_of_chips
                fraction = Fraction(numerator, denominator - n)
                self.probability_map[key] = fraction

        self.sanity_check()

    def detach_sub_probability_map(self, n_chips=1):
        split_ratio = Fraction(n_chips, self.n_of_chips)
        new_probability_map = dict()
        self.n_of_chips -= n_chips

        for key in self.probability_map.keys():
            new_probability_map[key] = self.probability_map[key] * split_ratio
            self.probability_map[key] *= 1 - split_ratio

        return new_probability_map

    def incorporate_probability_map(self, probability_map, n_chips=1):
        self.n_of_chips += n_chips

        for key in probability_map.keys():
            if self.probability_map.__contains__(key):
                inverse_probability = 1 - self.probability_map[key]
                inverse_probability *= 1 - probability_map[key]
                self.probability_map[key] = 1 - inverse_probability
            else:
                self.probability_map[key] = probability_map[key]

    def sanity_check(self):
        total_chip_value = Fraction(0)
        for fraction in self.probability_map.items():
            total_chip_value += fraction

        if total_chip_value / self.n_of_chips < 0.99 or total_chip_value / self.n_of_chips > 1.01:
            raise Exception("Did some funky math")
