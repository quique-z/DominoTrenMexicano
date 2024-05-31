import math
from typing import List, Set

from game.Chip import Chip
from game.ChipNodeList import ChipNodeList
from game.RevealedChip import RevealedChip


def generate_sequence(open_positions: List[int], chips: Set[Chip], heuristic_value_per_chip: float = 0, max_depth: int = math.inf) -> ChipNodeList:
    sg2 = SequenceGeneration2(chips)
    boundary = [sg2.nodes[i] for i in open_positions]
    sg2.find_longest_chain(boundary)
    return ChipNodeList()


class Node:

    def __init__(self, number):
        self.neighbors = dict()
        self.is_double = False
        self.number = number

    def add_neighbor(self, chip):
        if chip.is_double():
            self.is_double = True

        self.neighbors[chip.get_other_side(self.number)] = chip

    def get_neighbors(self):
        return self.neighbors.keys()

    def get_number(self):
        return self.number

    def __eq__(self, other):
        return self.number == other.number

    def __hash__(self):
        return hash(self.number)

    def __str__(self):
        return f"Node number {self.number}, neighbors {self.neighbors.keys()}"


class SequenceGeneration2:

    def __init__(self, chips):
        self.nodes = dict()

        for chip in chips:
            for number in chip.get_sides():
                if number not in self.nodes:
                    self.nodes[number] = Node(number)

                self.nodes[number].add_neighbor(chip)

    def find_longest_chain(self, boundary: List[Node], used_chips: Set[Chip] = None) -> ChipNodeList:
        if not used_chips:
            used_chips = set()

        for node in boundary:
            for n, chip in node.neighbors.items():
                if chip in used_chips:
                    continue

                new_boundary = boundary.copy()
                new_boundary.remove(node)
                new_boundary.append(self.nodes[chip.get_other_side(n)])

                new_chips = used_chips.copy()
                new_chips.add(chip)

                self.find_longest_chain(new_boundary, new_chips)

        return ChipNodeList()


def test_sequence_generation():
    numbers = [[5, 5], [5, 0], [0, 1], [1, 5], [1, 2]]
    chips = {RevealedChip(pair) for pair in numbers}
    print(generate_sequence([5], chips))
