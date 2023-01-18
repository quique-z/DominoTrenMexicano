from fractions import Fraction
from game import ChipFactory


class ProbabilityMap:
    def __init__(self, index, name, highest_double, double_to_skip, is_initial_pool=False):
        self.numbers_in_existence = [highest_double + 1] * (highest_double + 1)
        self.max_numbers = [0] * (highest_double + 1)
        self.min_numbers = [0] * (highest_double + 1)
        self.highest_double = highest_double
        self.total_chip_weight = Fraction(0)
        self.probability_map = dict()
        self.n_of_chips = 0
        self.index = index
        self.name = name

        if is_initial_pool:
            for chip in ChipFactory.create_chips(highest_double, double_to_skip):
                self.probability_map[chip] = Fraction(1)
            # Nth +1 triangular number minus one for the double to skip
            self.n_of_chips = int((highest_double + 2) * (highest_double + 1) / 2 - 1)
            self.max_numbers = [highest_double + 1] * (highest_double + 1)
            self.min_numbers = [highest_double + 1] * (highest_double + 1)
            self.numbers_in_existence[double_to_skip] -= 1
            self.total_chip_weight = Fraction(self.n_of_chips)
            self.max_numbers[double_to_skip] -= 1
            self.min_numbers[double_to_skip] -= 1

    def get_index(self):
        return self.index

    def get_possible_chips(self):
        return self.probability_map.keys()

    def get_probability_for_chip(self, chip):
        return self.get_probability_fraction_for_chip(chip).__float__()

    def get_probability_for_number(self, n):
        return self.get_probability_fraction_for_number(n).__float__()

    def get_probability_fraction_for_chip(self, chip):
        if self.n_of_chips == 0 or chip not in self.probability_map:
            return Fraction(0)
        return self.probability_map[chip]

    def get_probability_fraction_for_number(self, n):
        if self.min_numbers[n] > 0:
            return Fraction(1)
        elif self.max_numbers[n] == 0:
            return Fraction(0)

        numbered_chips = ChipFactory.create_chips_with_specific_numbers([n], self.highest_double)
        inverse_probability = Fraction(1)

        for chip in numbered_chips:
            if chip in self.probability_map:
                inverse_probability *= 1 - self.get_probability_fraction_for_chip(chip)

        return 1 - inverse_probability

    def refactor_probabilities(self, chip_weight_gain_map, chips_lost):
        if self.n_of_chips == 0 or chip_weight_gain_map is None:
            self.probability_map = dict()
            self.total_chip_weight = 0
            return dict()

        rolling_weight_multiplier = None
        new_chip_weight_gain_map = dict().fromkeys(self.probability_map.keys(), 0)

        for chip in chip_weight_gain_map.keys():
            if rolling_weight_multiplier is None:
                rolling_weight_multiplier = chip_weight_gain_map[chip]
            else:
                rolling_weight_multiplier /= 1 + (chips_lost - rolling_weight_multiplier) / self.n_of_chips

            for key in self.probability_map.keys():
                if key not in chip_weight_gain_map:
                    old_chip_weight = self.probability_map[key]
                    self.probability_map[key] /= 1 + (chips_lost - rolling_weight_multiplier) / self.n_of_chips
                    new_chip_weight_gain_map[key] -= self.probability_map[key] - old_chip_weight
                    self.total_chip_weight += self.probability_map[key] - old_chip_weight

        self.sanity_check()
        return new_chip_weight_gain_map

    def refactor_probabilities_2(self, modified_chips, sum_of_modified_chips_old_values, sum_of_modified_chips_new_values, chips_lost):
        old_n_of_chips = self.n_of_chips + chips_lost

        for chip in self.probability_map.keys():
            if chip not in modified_chips:
                self.total_chip_weight -= self.probability_map[chip]
                self.probability_map[chip] *= (self.n_of_chips - sum_of_modified_chips_new_values) / (old_n_of_chips - sum_of_modified_chips_old_values)
                self.total_chip_weight += self.probability_map[chip]

    def remove_chips_from_probability_map(self, chips, chips_lost):
        self.sanity_check()
        chip_weight_loss_map = dict()
        for chip in chips:
            if chip in self.probability_map:
                for side in chip.get_sides():
                    self.numbers_in_existence[side] = max(self.numbers_in_existence[side] - chips_lost, 0)
                    self.max_numbers[side] = min(self.max_numbers[side] - chips_lost, self.numbers_in_existence[side] - chips_lost)
                    self.min_numbers[side] = min(self.max_numbers[side], self.min_numbers[side])

                self.n_of_chips -= chips_lost
                chip_weight_loss_map[chip] = self.probability_map.pop(chip)
                self.total_chip_weight -= chip_weight_loss_map[chip]
        tmp = self.refactor_probabilities(chip_weight_loss_map, chips_lost)
        self.sanity_check()
        return merge_maps([chip_weight_loss_map, tmp])

    def remove_numbers_from_probability_map(self, numbers):
        self.sanity_check()
        for number in numbers:
            self.max_numbers[number] == 0
            self.min_numbers[number] == 0  # Should be 0 anyway

        numbered_chips = ChipFactory.create_chips_with_specific_numbers(numbers, self.highest_double)
        tmp = self.remove_chips_from_probability_map(numbered_chips, False)
        self.sanity_check()
        return tmp

    def decrease_probability_from_number(self, numbers, ratio):
        numbered_chips = ChipFactory.create_chips_with_specific_numbers(numbers, self.highest_double)
        chips_weight_loss_map = dict()

        for chip in numbered_chips:
            if chip in self.probability_map:
                chips_weight_loss_map[chip] = self.probability_map[chip] * (1 - ratio)
                self.total_chip_weight -= chips_weight_loss_map[chip]
                self.probability_map[chip] *= ratio

        return chips_weight_loss_map

    def adjust_probability_on_remaining_chips(self, chip_weight_loss_map):
        new_positive_chip_weight_loss_map = dict()
        new_negative_chip_weight_loss_map = dict()
        my_chips_copy = self.probability_map.copy()
        for key in chip_weight_loss_map:
            if chip_weight_loss_map[key] > 0:
                new_positive_chip_weight_loss_map[key] = chip_weight_loss_map[key]
            else:
                new_negative_chip_weight_loss_map[key] = chip_weight_loss_map[key]

        list_of_modified_chips = []
        modified_chips_old_weight_sum = 0
        modified_chips_new_weight_sum = 0
        for key in new_negative_chip_weight_loss_map.keys():
            if key in new_negative_chip_weight_loss_map:
                list_of_modified_chips.append(key)
                modified_chips_old_weight_sum += self.probability_map[key]
                self.total_chip_weight -= self.probability_map[key]
                self.probability_map[key] /= (1 + new_negative_chip_weight_loss_map[key])
                self.total_chip_weight += self.probability_map[key]
                modified_chips_new_weight_sum += self.probability_map[key]

        self.refactor_probabilities_2(list_of_modified_chips, modified_chips_old_weight_sum, modified_chips_new_weight_sum, False)

        # list_of_modified_chips = []
        modified_chips_old_weight_sum = 0
        modified_chips_new_weight_sum = 0
        for key in new_positive_chip_weight_loss_map.keys():
            if key in new_positive_chip_weight_loss_map:
                my_chips_copy[key] /= (1 + new_positive_chip_weight_loss_map[key])
                if my_chips_copy[key] != self.probability_map[key]:
                    list_of_modified_chips.append(key)
                    modified_chips_old_weight_sum += self.probability_map[key]
                    self.total_chip_weight -= self.probability_map[key]
                    self.probability_map[key] = my_chips_copy[key]
                    self.total_chip_weight += self.probability_map[key]
                    modified_chips_new_weight_sum += self.probability_map[key]

        self.refactor_probabilities_2(list_of_modified_chips, modified_chips_old_weight_sum, modified_chips_new_weight_sum, False)

        self.sanity_check()

    def detach_sub_probability_map(self, n_chips):
        self.sanity_check()
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
        self.sanity_check()
        return [new_probability_map, detached_min_numbers, detached_max_numbers]

    def incorporate_sub_probability_map(self, n_chips, probability_map, min_numbers, max_numbers):
        self.sanity_check()
        self.n_of_chips += n_chips

        for number in range(self.highest_double + 1):
            max_chips_of_this_number = min(self.numbers_in_existence[number], self.n_of_chips)
            self.min_numbers[number] = min(self.min_numbers[number] + min_numbers[number], max_chips_of_this_number)
            self.max_numbers[number] = min(self.max_numbers[number] + max_numbers[number], max_chips_of_this_number)

        for key in probability_map.keys():
            self.total_chip_weight += probability_map[key]
            if key in self.probability_map:
                self.probability_map[key] += probability_map[key]
            else:
                self.probability_map[key] = probability_map[key]

        self.sanity_check()

    def refactor_chip(self, chip, weight):
        self.total_chip_weight -= self.probability_map[chip]
        self.probability_map[chip] /= weight
        self.total_chip_weight += self.probability_map[chip]

    def refactor_all(self):
        if self.n_of_chips == self.total_chip_weight:
            return False

        old_total_chip_weight = self.total_chip_weight
        for chip in self.probability_map.keys():
            self.total_chip_weight -= self.probability_map[chip]
            self.probability_map[chip] /= old_total_chip_weight
            self.total_chip_weight += self.probability_map[chip]

        return True

    def get_n_of_chips(self):
        return self.n_of_chips

    def sanity_check(self):
        if self.n_of_chips != self.total_chip_weight:
            raise Exception("Hi")
        total = 0
        for key in self.probability_map.keys():
            total += self.probability_map[key]
        if total != self.n_of_chips:
            raise Exception("Hi")

    def __str__(self):
        s = ["Probability map for: %s\n" % self.name,
             "Number of chips: %s\n" % self.n_of_chips,
             "Total chip weight: %s\n" % self.total_chip_weight.__float__(),
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


def merge_maps(probability_maps):
    merged_map = dict()
    for pm in probability_maps:
        for key in pm.keys():
            if key in merged_map:
                merged_map[key] -= pm[key]
            else:
                merged_map[key] = -pm[key]
    return merged_map
