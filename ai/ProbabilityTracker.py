from typing import Set

from ai.PossibleUniverse import PossibleUniverse
from game import ChipFactory
from game.RevealedChip import RevealedChip


class ProbabilityTracker:

    def __init__(self, highest_double: int, double_to_skip: int, n_players: int, owner_id: int) -> None:
        self.draw_pile_id = owner_id
        self.n_players = n_players

        self.unseen_chips = set(ChipFactory.create_chips(highest_double, double_to_skip))
        players_chips = [set() for _ in range(n_players)]
        players_chips[self.draw_pile_id] = self.unseen_chips

        self.possible_universes = {PossibleUniverse(owner_id, players_chips)}

    def player_draws(self, player_id: int, amount_of_chips: int = 1) -> None:
        if not amount_of_chips:
            return

        # self.possible_universes = {u for universe in self.possible_universes for u in universe.player_draws(player_id)}

        new_universes = set()

        for universe in self.possible_universes:
            new_universes.update(universe.player_draws(player_id))

        self.possible_universes = new_universes
        self.player_draws(player_id, amount_of_chips - 1)

    def player_reveals(self, player_id: int, chips: Set[RevealedChip]) -> None:
        #  self.possible_universes = {u for u in self.possible_universes if u.does_universe_persist(player_id, chips)}
        new_universes = set()

        for universe in self.possible_universes:
            if universe.does_n_player_have_x_chips(player_id, chips):
                new_universes.add(universe)

        self.possible_universes = new_universes

    def player_does_not_have_numbers(self, player_id: int, numbers: Set[int]) -> None:
        # self.possible_universes = {u for u in self.possible_universes if not u.does_n_player_have_x_numbers(player_id, numbers)}
        new_universes = set()

        for universe in self.possible_universes:
            if not universe.does_n_player_have_x_numbers(player_id, numbers):
                new_universes.add(universe)

        self.possible_universes = new_universes

    def get_probability_n_player_has_x_numbers(self, player_id: int, numbers: Set[int]) -> float:
        # return sum(u.does_n_player_have_x_numbers(player_id, numbers) for u in self.possible_universes) / len(self.possible_universes)
        total = 0
        for universe in self.possible_universes:
            if universe.does_n_player_have_x_numbers(player_id, numbers):
                total += 1
        return total / len(self.possible_universes)