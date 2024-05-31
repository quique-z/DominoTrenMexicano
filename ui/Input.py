from typing import Optional, List

from game.ChipNode import ChipNode
from game.RevealedChip import RevealedChip


def boolean_input(prompt: str) -> bool:
    while True:
        try:
            user_input = input(prompt)
            if user_input[0].upper() == "T":
                return True
            if user_input[0].upper() == "F":
                return False
            raise ValueError
        except ValueError:
            print("Expecting (T)rue or (F)alse")


def number_input(prompt: str, valid_options: List[int] = None) -> int:
    while True:
        try:
            number = int(input(prompt))
            if not valid_options or number in valid_options:
                return number
            raise ValueError
        except ValueError:
            if valid_options:
                print(f"Invalid input. Expecting a choice between these numbers: {valid_options}")
            else:
                print("Expecting a number.")


def row_input(player_names: List[str]) -> int:
    row_prompt = [f"Row to play\n"]
    row_prompt.extend(f"{i}: {name}" for i, name in enumerate(player_names))
    return number_input("".join(row_prompt), list(range(len(player_names))))


def chip_input(prompt: str, empty_allowed: bool = True) -> Optional[RevealedChip]:
    while True:
        try:
            chip_as_string = input(prompt)

            if not chip_as_string:
                if empty_allowed:
                    return None
                else:
                    raise ValueError("Move can't be empty.")

            numbers = [int(n) for n in chip_as_string.split()]
            return RevealedChip(numbers)
        except ValueError:
            print("Invalid input. Expecting 2 numbers in A B format. Ex: 5 12")


def chip_node_input(open_position: int, empty_allowed: bool = True) -> Optional[ChipNode]:
    chip_node = None
    while True:
        try:
            chip = chip_input(f"Enter chip to play on position {open_position}. Leave blank when done.", empty_allowed)

            if not chip:
                if chip_node or empty_allowed:
                    return chip_node
                raise ValueError

            chip_node = ChipNode(chip, open_position)

            next_node = chip_node_input(chip.get_other_side(open_position))
            chip_node.add_next_node(next_node)

            if chip.is_double() and next_node:
                next_node2 = chip_node_input(chip.get_other_side(open_position))
                chip_node.add_next_node(next_node2)

            return chip_node

        except ValueError:
            print("Invalid chain.")
