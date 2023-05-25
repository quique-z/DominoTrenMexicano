import math

from game.Chip import Chip
from game.ChipNode import ChipNode


class SequenceGeneration2:
    double_zero_value = 50
    highest_possible_chip = 15

    def __init__(self, chips):
        self.vertices = dict()
        for chip in chips:
            for number in chip.get_sides():
                self.vertices[number] = Vertex(number)

        for v in self.vertices.values():
            for chip in chips:
                if v.get_number() in chip:
                    v.add_neighbor(chip)


    def find_longest_chain(self):
        progress_made = True
        while progress_made:
            progress_made = False
            for origin_vertex in self.vertices:
                for neighbor_id in origin_vertex.get_neighbors():
                    neighbor_vertex = self.vertices[neighbor_id]
                    if neighbor_vertex.update_paths(origin_vertex.get_number(), origin_vertex.get_paths()):
                        progress_made = True





class Vertex:

    def __init__(self, number):
        self.neighbors = dict()
        self.double_chip = None
        self.is_double = False
        self.number = number
        self.paths = set()

    def add_neighbor(self, chip):
        if chip.is_double():
            self.is_double = True
            self.double_chip = chip
            return

        self.neighbors[chip.get_other_side(self.number)] = chip

    def get_neighbors(self):
        return self.neighbors.keys()

    def get_number(self):
        return self.number

    def update_paths(self, origin_id, paths):
        progress_made = False

        for individual_path in paths:
            cn = ChipNode(Chip([self.number, origin_id]), self.number)
            cn.add_next_node(individual_path.__copy__())
            if cn not in self.paths:
                self.paths.add(cn)
                progress_made = True

        return progress_made

    def get_paths(self):
        return self.paths

    def __eq__(self, other):
        return self.number == other.number

    def __hash__(self):
        return hash(self.number)

    def __str__(self):
        return "Vertex number %s" % self.number
