from typing import List, Self, Set

from game.RevealedChip import RevealedChip


class PossibleUniverse:

    def __init__(self, owner_id: int, chips: List[Set[RevealedChip]]) -> None:
        self.draw_pile_id = owner_id
        self.n_players = len(chips)
        self.chips = chips

        self.players_chips = [set() for _ in range(self.n_players)]

    def player_draws(self, player_id: int) -> Set[Self]:
        new_universes = set()

        for chip in self.players_chips[self.draw_pile_id]:
            tmp_universe = self.players_chips.copy()
            tmp_universe[self.draw_pile_id].remove(chip)
            tmp_universe[player_id].add(chip)
            new_universes.add(PossibleUniverse(self.draw_pile_id, tmp_universe))

        return new_universes

    def does_n_player_have_x_chips(self, player_id: int, chips: Set[RevealedChip]) -> bool:
        return bool(self.players_chips[player_id] & chips)

    def does_n_player_have_x_numbers(self, player_id: int, numbers: Set[int]) -> bool:
        return any(numbers & chip.get_sides() for chip in self.players_chips[player_id])

    def __eq__(self, other):
        if not isinstance(other, PossibleUniverse):
            return False
        return self.players_chips == other.players_chips

    def __hash__(self):
        return hash(tuple(frozenset(player_chips) for player_chips in self.players_chips))