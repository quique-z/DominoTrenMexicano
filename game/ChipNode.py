from typing import Self, List, Optional

from game.Chip import Chip


class ChipNode:

    def __init__(self, chip: Chip, side_to_play: int, heuristic_value_per_chip: int = 0) -> None:
        self.next = None
        self.next2 = None
        self.chip = chip
        self.side_to_play = side_to_play
        self.value = chip.get_value() + heuristic_value_per_chip

    def add_next_node(self, chip_node: Self) -> None:
        if chip_node is None:
            return

        if self.next and (self.next2 or not self.is_chip_double()):
            raise Exception("Can't add a node, next is already occupied.")

        if chip_node.get_chip_side_to_play() != self.chip.get_other_side(self.side_to_play):
            raise Exception("Can't add a node, next chip's number does not match this chip's other side.")

        if self.is_chip_double() and self.next:
            self.next2 = chip_node
        else:
            self.next = chip_node

    def override_next_node(self, chip_node: Self) -> None:
        self.next = None
        self.next2 = None
        self.add_next_node(chip_node)

    def get_next_move_value(self) -> int:
        next_value = self.chip.get_value()
        if self.is_chip_double() and self.next is not None:
            if self.next2 is not None and self.next2.get_next_move_value() > self.next.get_next_move_value():
                next_value += self.next2.get_next_move_value()
            else:
                next_value += self.next.get_next_move_value()
        return next_value

    def get_next_move_as_chip_list(self) -> List[Chip]:
        next_chip = [self.chip]
        if self.is_chip_double() and self.next is not None:
            if self.next2 is not None and self.next2.get_next_move_value() > self.next.get_next_move_value():
                next_chip.append(self.next2.get_chip())
            else:
                next_chip.append(self.next.get_chip())
        return next_chip

    def get_next_move_as_node(self) -> Self:
        next_node = ChipNode(self.chip, self.side_to_play)
        if self.is_chip_double() and self.next is not None:
            if self.next2 is not None and self.next2.get_next_move_value() > self.next.get_next_move_value():
                next_node.add_next_node(ChipNode(self.next2.get_chip(), self.side_to_play))
            else:
                next_node.add_next_node(ChipNode(self.next.get_chip(), self.side_to_play))
        return next_node

    def get_tail(self) -> Optional[List[Self]]:
        if not self.next:
            return None

        if self.is_chip_double():
            if not self.next2:
                return [self.next.next] if self.next.next else None
            elif self.next.get_next_piece_value() > self.next2.get_next_piece_value():
                return [self.next.next, self.next2] if self.next.next else [self.next2]
            elif self.next2.next:
                return [self.next2.next, self.next]

        return [self.next]

    def is_chip_double(self) -> bool:
        return self.chip.is_double()

    def get_chip_side_to_play(self) -> int:
        return self.side_to_play

    def get_chip(self) -> Chip:
        return self.chip

    def get_chipset(self) -> List[Chip]:
        chipset = [self.chip]
        if self.next:
            chipset.extend(self.next.get_chipset())
        if self.next2:
            chipset.extend(self.next2.get_chipset())
        return chipset

    def get_chain_value(self) -> int:
        value = self.value
        if self.next:
            value += self.next.get_chain_value()
        if self.next2:
            value += self.next2.get_chain_value()
        return value

    def get_ending_doubles(self) -> List[int]:
        doubles = []
        if self.is_chip_double() and not self.next and not self.next2:
            doubles.append(self.get_chip_side_to_play())
        if self.next:
            doubles += self.next.get_ending_doubles()
        if self.next2:
            doubles += self.next2.get_ending_doubles()
        return doubles

    def __contains__(self, value) -> bool:
        if self.chip.__contains__(value):
            return True
        elif self.next and self.next.__contains__(value):
            return True
        elif self.next2 and self.next2.__contains__(value):
            return True
        return False

    def __copy__(self) -> Self:
        cn = ChipNode(self.chip, self.side_to_play)
        if self.next:
            cn.add_next_node(self.next.__copy__())
        if self.next2:
            cn.add_next_node(self.next2.__copy__())
        return cn

    def __len__(self) -> int:
        return len(self.get_chipset())

    def __str__(self) -> str:
        s = ["On position %s I play this chip: %s\n" % (self.side_to_play.__str__(), self.chip.__str__())]
        if self.next:
            s.append(self.next.__str__())
        if self.next2:
            s.append(self.next2.__str__())
        return ''.join(s)


def chip_node_from_string(string, number) -> Optional[ChipNode]:
    if not string:
        return None

    cn = ChipNode(Chip(), number)
    cn.next = chip_node_from_string(string[1:], number)

    return cn
