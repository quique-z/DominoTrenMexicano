# Interface for a Human Player to play against the AI.
from game.ChipNode import chip_node_from_string
from game.ChipNodeList import ChipNodeList
from players.CPUPlayer import Player


class HumanPlayer(Player):

    def can_play(self, board):
        while True:
            try:
                num = bool(input("Can %s play?" % self.name))
                break
            except ValueError:
                print('Expecting True or False')

        print('Good job. The entered number is: ', num)

    def has_chips(self, chips):
        return True

    def play(self, board, players):
        while True:
            try:
                row = int(input("Row to play"))
                break
            except ValueError:
                print("Not a number")

        cnl = ChipNodeList()
        print("Enter chips, one arm per line.")
        while True:
            try:
                number = int(input("Number to play next arm of chips on"))
                cn = chip_node_from_string(input("Next series of Ch").split(), number)
                if cn:
                    cnl.add(cn)
                else:
                    break
            except Exception:
                print("Invalid Chip Node")

        return [cnl, row]

    def add_up_points(self):
        while True:
            try:
                number = int(input("Total points for %s" % self.name))
                break
            except ValueError:
                print("Invalid input.")

        return number


