from fractions import Fraction
from game import ChipFactory


class ProbabilityMap:
    def __init__(self, name, highest_double, double_to_skip, is_initial_pool=False):
        self.numbers_in_existence = [highest_double + 1] * (highest_double + 1)
        self.max_numbers = [0] * (highest_double + 1)
        self.min_numbers = [0] * (highest_double + 1)
        self.highest_double = highest_double
        self.total_chip_weight = Fraction(0)
        self.probability_map = dict()
        self.n_of_chips = 0
        self.name = name

        if is_initial_pool:
            for chip in ChipFactory.create_chips(highest_double, double_to_skip):
                self.probability_map[chip] = Fraction(1)
            # Nth +1 triangular number minus one for the double to skip
            self.total_chip_weight = Fraction((highest_double + 2) * (highest_double + 1) / 2 - 1)
            self.n_of_chips = self.total_chip_weight
            self.max_numbers = [highest_double + 1] * (highest_double + 1)
            self.min_numbers = [highest_double + 1] * (highest_double + 1)
            self.numbers_in_existence[double_to_skip] -= 1
            self.max_numbers[double_to_skip] -= 1
            self.min_numbers[double_to_skip] -= 1

    def get_possible_chips(self):
        return self.probability_map.keys()

    def get_probability_for_chip(self, chip):
        return self.get_probability_fraction_for_chip(chip).__float__()

    def get_probability_for_number(self, n):
        return self.get_probability_fraction_for_number(n).__float__()

    def get_probability_fraction_for_chip(self, chip):
        if self.n_of_chips == 0 or not self.probability_map.__contains__(chip):
            return Fraction(0)
        return self.probability_map[chip] * self.n_of_chips / self.total_chip_weight

    def get_probability_fraction_for_number(self, n):
        if self.min_numbers[n] > 0:
            return Fraction(1)
        elif self.max_numbers[n] == 0:
            return Fraction(0)

        numbered_chips = ChipFactory.create_chips_with_specific_numbers([n], self.highest_double)
        inverse_probability = Fraction(1)

        for chip in numbered_chips:
            if self.probability_map.__contains__(chip):
                inverse_probability *= 1 - self.get_probability_fraction_for_chip(chip)

        return 1 - inverse_probability

    def withdraw_chip_from_probability_map(self, chip):
        self.n_of_chips -= 1
        chip_weight = self.probability_map.pop(chip)
        self.total_chip_weight -= chip_weight
        for side in chip.get_sides():
            self.max_numbers[side] -= 1
            self.numbers_in_existence[side] -= 1
            self.min_numbers[side] = min(self.max_numbers[side], self.min_numbers[side])
            # TODO: max might lower, if no other numbers have min > 0

        return chip_weight

    def remove_chip_from_probability_map(self, chip):
        if not self.probability_map.__contains__(chip):
            return
        chip_weight = self.probability_map.pop(chip)
        self.total_chip_weight -= chip_weight
        for side in chip.get_sides():
            self.numbers_in_existence[side] = max(self.numbers_in_existence[side] - 1, 0)
            self.max_numbers[side] = min(self.max_numbers[side], self.numbers_in_existence[side])

    def remove_numbers_from_probability_map(self, numbers):
        for number in numbers:
            self.max_numbers[number] == 0
            self.min_numbers[number] == 0  # Should be 0 anyway

        numbered_chips = ChipFactory.create_chips_with_specific_numbers(numbers, self.highest_double)
        total_weight_loss = Fraction(0)
        chips_weight_loss_map = dict()

        for chip in numbered_chips:
            if self.probability_map.__contains__(chip):
                chips_weight_loss_map[chip] = self.probability_map.pop(chip)
                total_weight_loss += chips_weight_loss_map[chip]

        self.total_chip_weight -= total_weight_loss
        return chips_weight_loss_map

    def decrease_probability_from_number(self, numbers, ratio):
        numbered_chips = ChipFactory.create_chips_with_specific_numbers(numbers, self.highest_double)
        total_weight_loss = Fraction(0)
        chips_weight_loss_map = dict()

        for chip in numbered_chips:
            if self.probability_map.__contains__(chip):
                chips_weight_loss_map[chip] = self.probability_map[chip] * (1 - ratio)
                total_weight_loss += chips_weight_loss_map[chip]
                self.probability_map[chip] *= ratio

        self.total_chip_weight -= total_weight_loss
        return chips_weight_loss_map

    def adjust_probability_on_remaining_chips(self, chip_weight_loss_map):
        for key in chip_weight_loss_map:
            if self.probability_map.__contains__(key):
                self.probability_map[key] /= 1 - chip_weight_loss_map[key]

    def detach_sub_probability_map(self, n_chips):
        split_ratio = Fraction(n_chips, self.n_of_chips)
        new_probability_map = dict()

        for key in self.probability_map.keys():
            new_probability_map[key] = self.probability_map[key] * split_ratio
            self.total_chip_weight -= new_probability_map[key]
            self.probability_map[key] *= 1 - split_ratio

        detached_min_numbers = [0] * (self.highest_double + 1)
        detached_max_numbers = [0] * (self.highest_double + 1)

        for number in range(self.highest_double + 1):
            detached_min_numbers[number] = max(self.min_numbers[number] + n_chips - self.n_of_chips, 0)
            detached_max_numbers[number] = min(self.max_numbers[number], n_chips)
            self.min_numbers[number] = max(self.min_numbers[number] - n_chips, 0)
            self.max_numbers[number] = min(self.max_numbers[number], self.n_of_chips)

        self.n_of_chips -= n_chips
        return [new_probability_map, detached_min_numbers, detached_max_numbers]

    def incorporate_probability_map(self, n_chips, probability_map, min_numbers, max_numbers):
        self.n_of_chips += n_chips

        for number in range(self.highest_double + 1):
            max_chips_of_this_number = min(self.numbers_in_existence[number], self.n_of_chips)
            self.min_numbers[number] = min(self.min_numbers[number] + min_numbers[number], max_chips_of_this_number)
            self.max_numbers[number] = min(self.max_numbers[number] + max_numbers[number], max_chips_of_this_number)

        for key in probability_map.keys():
            old_weight = Fraction(0)
            if self.probability_map.__contains__(key):
                old_weight += self.probability_map[key]
                inverse_probability = 1 - self.probability_map[key]
                inverse_probability *= 1 - probability_map[key]
                self.probability_map[key] = 1 - inverse_probability
            else:
                self.probability_map[key] = probability_map[key]
            self.total_chip_weight += self.probability_map[key] - old_weight

    def __str__(self):
        s = ["Probability map for: %s\n" % self.name,
             "Number of chips: %s\n" % self.n_of_chips,
             "Total chip weight: %s\n" % self.total_chip_weight,
             "Probabilities for each chip are:\n"]
        for key in self.probability_map.keys():
            s.append("%s, %s\n" % (key, self.get_probability_for_chip(key)))
        s.append("Probabilities for each number are: \n")
        for number in range(self.highest_double + 1):
            s.append(("%s: %s\n" % (number, self.get_probability_for_number(number))))
        s.append("Max chips for each number are: %s\n" % self.max_numbers)
        s.append("Min chips for each number are: %s\n" % self.min_numbers)
        s.append("Numbers in existence are: %s\n" % self.numbers_in_existence)
        return ''.join(s)
