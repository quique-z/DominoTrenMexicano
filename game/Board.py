from typing import List, Set

from game import Chip, PlayableChipNode
from game.Row import Row


class Board:

    def __init__(self, n_players: int, center_chip_double: int, chips: List[Chip], player_names: List[str] = None) -> None:
        if not player_names:
            player_names = range(n_players)
        self.center_double = center_chip_double
        self.n_players = n_players
        self.draw_pile = chips
        self.forced = False
        self.forced_row = -1
        self.forced_numbers = set()
        self.forced_culprit = -1
        self.rows = []
        for i in range(n_players):
            self.rows.append(Row(i, center_chip_double, player_names[i]))

    def play_chip(self, chip_to_play: Chip, side_to_play: int, row_to_play: int) -> None:
        self.rows[row_to_play].play_chip(chip_to_play, side_to_play)

    def play_playable_chip_node(self, playable_chip_node: PlayableChipNode) -> None:
        self.rows[playable_chip_node.get_row()].play_chip_node(playable_chip_node.get_chip_node())

    def set_forced(self, row: int, numbers: List[int], culprit: int) -> None:
        self.forced = True
        self.forced_row = row
        self.set_train(culprit)
        self.forced_culprit = culprit
        self.forced_numbers.update(numbers)

    def remove_forced(self, number: int) -> None:
        self.forced_numbers.remove(number)
        if not self.forced_numbers:
            self.forced = False
            self.forced_row = -1
            self.forced_culprit = -1

    def is_forced(self) -> bool:
        return self.forced

    def get_forced_row_index(self) -> int:
        return self.forced_row

    def get_forced_numbers(self) -> Set[int]:
        return self.forced_numbers

    def get_forced_culprit_index(self) -> int:
        return self.forced_culprit

    def get_row(self, index: int) -> Row:
        return self.rows[index]

    def get_rows(self) -> List[Row]:
        return self.rows

    def can_draw(self) -> bool:
        return len(self.draw_pile) > 0

    def draw(self) -> Chip:
        return self.draw_pile.pop()

    def set_train(self, index: int) -> None:
        self.rows[index].set_train()

    def remove_train(self, index: int) -> None:
        self.rows[index].remove_train()

    def has_train(self, index: int) -> bool:
        return self.rows[index].has_train()

    def get_number_of_players(self) -> int:
        return self.n_players

    def __str__(self) -> str:
        s = ["Center double: %s" % self.center_double,
             "\nPlayers: %s" % len(self.rows),
             "\nChips in draw pile: %s" % len(self.draw_pile)]
        for row in self.rows:
            s.append("\n%s" % row.__str__())
        if self.forced:
            s.append("\nAnd board is forced to row " + self.forced_row.__str__())
            s.append("\nOn numbers " + self.forced_numbers.__str__())
        return ''.join(s)
