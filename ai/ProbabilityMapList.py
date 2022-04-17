from ai.ProbabilityMap import ProbabilityMap


class ProbabilityMapList:

    def __init__(self, names, highest_double, n_chips_per_player):
        self.n_chips_per_player = n_chips_per_player
        self.highest_double = highest_double
        self.probability_maps = None
        self.n_players = len(names)
        self.names = names

    def init_round(self, double_to_skip):
        self.probability_maps = []
        for i in range(self.n_players):
            pm = self.probability_maps.append(ProbabilityMap(self.names[i], self.highest_double, double_to_skip))

        # Initial Pool
        self.probability_maps.append(ProbabilityMap("Draw Pool", self.highest_double, double_to_skip, True))

        for i in range(self.n_players):
            self.player_draws_chips(i, self.n_chips_per_player)

    def get_possible_chips(self, index):
        return self.probability_maps[index].get_possible_chips()

    def get_probability_for_chip(self, index, chip):
        return self.probability_maps[index].get_probability_for_chip(chip)

    def get_probability_fraction_for_chip(self, index, chip):
        return self.probability_maps[index].get_probability_fraction_for_chip(chip)

    def get_probability_fraction_for_number(self, index, n):
        return self.probability_maps[index].get_probability_fraction_for_number(n)

    def get_probability_for_number(self, index, n):
        return self.probability_maps[index].get_probability_for_number(n)

    def chip_was_played_by_player(self, chip, index):
        for i in range(len(self.probability_maps)):
            if i == index:
                self.probability_maps[i].withdraw_chip_from_probability_map(chip)
            else:
                self.probability_maps[i].remove_chip_from_probability_map(chip)

    def remove_numbers_from_probability_map(self, index, numbers):
        chip_weight_loss_map = self.probability_maps[index].remove_numbers_from_probability_map(numbers)

        for i in range(len(self.probability_maps)):
            if i != index:
                self.probability_maps[i].adjust_probability_on_remaining_chips(chip_weight_loss_map)

    def decrease_probability_from_number(self, index, numbers, not_likely_to_have_chip_ratio):
        self.probability_maps[index].decrease_probability_from_number(numbers, not_likely_to_have_chip_ratio)

    def player_draws_chips(self, index, n_chips=1):
        [pm, min_n, max_n] = self.probability_maps[self.n_players].detach_sub_probability_map(n_chips)
        self.probability_maps[index].incorporate_probability_map(n_chips, pm, min_n, max_n)

    def __str__(self):
        s = []
        for i in range(len(self.probability_maps)):
            s.append(self.probability_maps[i].__str__())
            s.append("\n\n")
        return ''.join(s)

