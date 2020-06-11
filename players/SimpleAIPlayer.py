from players.BasicPlayer import Player


class SimpleAIPlayer(Player):

    def __init__(self, index):
        super().__init__(index)

    def play_any(self, board):
        print(self.name + " juega: ")
        if board.is_forced():
            self.play_forced(board)
            return

        for row in board.get_rows():
            if row.get_index() == self.index or (row.has_train() and (not board.has_train(self.index))):
                for open_number in row.get_open_positions():
                    for chip in self.chips:
                        if chip.__contains__(open_number):
                            chip_to_play = chip
                            self.chips.remove(chip)
                            board.play_chip(chip_to_play, open_number, row.get_index())
                            board.remove_train(self.index)
                            print(chip_to_play)
                            if chip_to_play.double():
                                board.set_forced(row.get_index(), chip_to_play.get_side_a())
                                can_play = self.can_play_number(chip_to_play.get_side_a())
                                if not can_play and board.can_draw():
                                    self.add_chip(board.draw())
                                    can_play = self.can_play_number(chip_to_play.get_side_a())
                                if can_play:
                                    self.play_forced(board)
                                else:
                                    board.set_train(self.index)
                            if len(self.chips) == 1:
                                print(self.name + ": ¡Uno!")
                            return

    def play_forced(self, board):
        for number in board.get_forced_numbers():
            for chip in self.chips:
                if chip.__contains__(number):
                    chip_to_play = chip
                    print(chip_to_play)
                    self.chips.remove(chip)
                    board.play_chip(chip_to_play, number, board.get_forced_row())
                    board.remove_forced(number)
                    if not board.is_forced and board.get_forced_row == self.index:
                        board.remove_train(self.index)
                    if len(self.chips) == 1:
                        print(self.name + ": ¡Uno!")
                    return
