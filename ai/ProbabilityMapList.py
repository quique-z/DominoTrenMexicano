from fractions import Fraction

from ai.ProbabilityMap import ProbabilityMap
from game import ChipFactory


class ProbabilityMapList:

    def __init__(self, names, highest_double, n_chips_per_player, index):
        self.n_chips_per_player = n_chips_per_player
        self.highest_double = highest_double
        self.probability_maps = None
        self.my_player_index = index
        self.n_players = len(names)
        self.names = names

    def init_round(self, chips, double_to_skip):
        self.probability_maps = []
        for i in range(self.n_players):
            self.probability_maps.append(ProbabilityMap(i, self.names[i], self.highest_double, double_to_skip))

        # Initial Pool
        self.probability_maps.append(ProbabilityMap(self.n_players, "Draw Pool", self.highest_double, double_to_skip, True))

        # Remove my chips from pool
        self.probability_maps[-1].remove_chips_from_probability_map(chips, True)

        # Give other players their initial hand
        for i in range(self.n_players):
            if i != self.my_player_index:
                self.player_draws_chips(i, self.n_chips_per_player)

        self.sanity_check()

    def get_possible_chips(self, index):
        return self.probability_maps[index].get_possible_chips()

    def get_probability_for_chip(self, index, chip):
        return self.probability_maps[index].get_probability_for_chip(chip)

    def get_probability_for_number(self, index, n):
        return self.probability_maps[index].get_probability_for_number(n)

    def chip_was_played_by_player(self, index, chip):
        for pm in self.probability_maps:
            pm.remove_chips_from_probability_map([chip], pm.get_index() == index)
        self.sanity_check()

    def remove_numbers_from_probability_map(self, index, numbers):
        chip_weight_loss_map = self.probability_maps[index].remove_numbers_from_probability_map(numbers)

        for i in range(len(self.probability_maps)):
            if i != index:
                self.probability_maps[i].adjust_probability_on_remaining_chips(chip_weight_loss_map)
        self.sanity_check()

    def decrease_probability_from_number(self, index, numbers, not_likely_to_have_chip_ratio):
        self.probability_maps[index].decrease_probability_from_number(numbers, not_likely_to_have_chip_ratio)
        self.sanity_check()

    def player_draws_chips(self, index, n_chips=1):
        [pm, min_n, max_n] = self.probability_maps[-1].detach_sub_probability_map(n_chips)
        self.probability_maps[index].incorporate_sub_probability_map(n_chips, pm, min_n, max_n)
        self.sanity_check()

    def chip_was_drawn_by_ai(self, chip):
        # Having the AI player whose PML this is draw and see a chip is equivalent (in probabilistic terms) to "the draw pile playing a chip".
        self.chip_was_played_by_player(self.n_players, chip)

    def sanity_check(self):
        chips = ChipFactory.create_chips(self.highest_double)
        for chip in chips:
            total = Fraction(0)
            total_float = 0
            for pm in self.probability_maps:
                total += pm.get_probability_fraction_for_chip(chip)
                total_float += pm.get_probability_for_chip(chip)
            if total < -0.01 or total > 1.01 or (0 < total < 0.99):
                raise Exception("Probability mismatch")

    def __str__(self):
        s = ["\n"]
        for i in range(len(self.probability_maps)):
            if i != self.my_player_index:
                s.append("%s" % self.probability_maps[i].__str__())
        return ''.join(s)

