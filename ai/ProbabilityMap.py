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
        probability_loss = self.probability_map.pop(chip)
        self.adjust_probability_on_remaining_chips(probability_loss)

    def remove_number_from_probability_map(self, n):
        numbered_chips = ChipFactory.create_chips_with_specific_number(n, self.highest_double)

        probability_loss = Fraction(0)
        for chip in numbered_chips:
            if self.probability_map.__contains__(chip):
                probability_loss += self.probability_map.pop(chip)
                self.n_of_chips -= 1

        self.adjust_probability_on_remaining_chips(probability_loss)

    def adjust_probability_on_remaining_chips(self, probability_loss):
        for key in self.probability_map.keys():
            self.probability_map[key] /= 1 - probability_loss

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
