# Interface for a Human Player to play against the AI.
from typing import List, Set

from game.Board import Board
from game.Chip import Chip
from game.PlayableChipNode import PlayableChipNode
from players.Player import Player
from ui.Input import boolean_input, number_input, chip_node_input, row_input


class HumanPlayer(Player):

    def add_chip(self, chip: Chip) -> None:
        self.chips.add(chip)

    def remove_chips(self, chips: Set[Chip]) -> None:
        for _ in range(len(chips)):
            self.chips.pop()

    def can_play(self, board: Board) -> bool:
        if not super().can_play(board):
            return False

        return boolean_input(f"Can {self.name} play?")

    def get_current_points(self) -> int:
        return -1

    def add_up_points(self) -> None:
        self.total_points += number_input(f"total points for {self.name}")

    def will_say_one(self) -> bool:
        return boolean_input(f"Did {self.name} say one?")

    def will_remove_train(self) -> bool:
        return boolean_input(f"Did {self.name} remove their train?")

    def has_chips(self, chips: List[Chip]) -> bool:
        return True

    def get_chips(self) -> Set[Chip]:
        return set()

    def play(self, board: Board, players: List[Player]) -> PlayableChipNode:
        row = row_input([player.get_name() for player in players])
        open_position = number_input("Open position to play chips on.", board.get_row(row).get_open_positions())
        chip_node = chip_node_input(open_position, empty_allowed=False)
        return PlayableChipNode(chip_node, row)

    def __str__(self) -> str:
        return f"{self.name}: Round points: Unknown, Total points: {self.total_points}, Chips: {len(self.chips)} unknown chips."
