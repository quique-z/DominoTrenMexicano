import logging

from ai.ProbabilityChipList import ProbabilityChipList
from players.HeuristicAIPlayer import HeuristicAIPlayer
from players.SmartCPUPlayer import SimpleCPUPlayer
from players.HumanPlayer import HumanPlayer
from players.CPUPlayer import Player
from game.Board import Board
from game import ChipFactory
import random
import math
import time


class GameManager:

    def __init__(self, n_chips_per_player, highest_double, initial_double, basic_py, simple_py, heuristic_py, human_py, player_names=None, starting_turn=-1):
        self.n_players = basic_py + simple_py + heuristic_py + human_py
        self.n_chips_per_player = n_chips_per_player
        self.endgame_countdown = self.n_players
        self.highest_double = highest_double
        self.current_double = initial_double
        self.probability_chip_lists = None
        self.global_winner = []
        self.endgame = False
        self.players = []
        self.board = None
        self.chips = []

        self.player_names = player_names
        if player_names is None:
            self.player_names = []
            for i in basic_py + simple_py + heuristic_py + human_py:
                self.player_names.append(i.__str__())

        if starting_turn < 0:
            self.turn = random.randrange(self.n_players)
        else:
            self.turn = starting_turn

        for i in range(basic_py):
            self.players.append(Player(i, player_names[i]))
        for i in range(len(self.players), len(self.players) + simple_py):
            self.players.append(SimpleCPUPlayer(i, player_names[i]))
        for i in range(len(self.players), len(self.players) + heuristic_py):
            self.players.append(HeuristicAIPlayer(i, player_names[i], highest_double, n_chips_per_player))
        for i in range(len(self.players), len(self.players) + human_py):
            self.players.append(HumanPlayer(i, player_names[i]))

    def init_round(self):
        self.chips = ChipFactory.create_chips(self.highest_double, self.current_double)
        self.probability_chip_lists = []
        random.shuffle(self.chips)
        self.endgame = False
        self.endgame_countdown = self.n_players

        for player in self.players:
            chips = []
            for i in range(self.n_chips_per_player):
                chips.append(self.chips.pop())
            player.init_round(chips, self.current_double)
            self.probability_chip_lists.append(ProbabilityChipList(self.chips, self.n_chips_per_player, self.highest_double))

        self.probability_chip_lists.append(ProbabilityChipList(self.chips, len(self.chips), self.highest_double))
        self.board = Board(self.n_players, self.current_double, self.chips, self.player_names)

    def end_round(self):
        global_best_score = math.inf
        round_winner = None

        for player in self.players:
            player.add_up_points()
            if player.is_round_winner():
                round_winner = player
            if player.get_total_points() < global_best_score:
                global_best_score = player.get_total_points()
                self.global_winner = [player]
            elif player.get_total_points() == global_best_score:
                self.global_winner.append(player)

        if round_winner is None:
            min_score = math.inf
            for player in self.players:
                if player.get_current_points() < min_score:
                    round_winner = player
                    min_score = player.get_current_points()
                elif player.get_current_points() == min_score:
                    if player.get_total_points() < round_winner.get_total_points():
                        round_winner = player

        self.current_double -= 1
        self.turn = round_winner.get_index()

    def has_next_round(self):
        return self.current_double >= 0

    def has_next_turn(self):
        # Breaks stalemates where there are no more moves to make.
        if not self.board.can_draw():
            self.endgame = True
            if self.endgame_countdown <= 0:
                return False
            # Rare condition where a player is eligible to win but hasn't because the board used to be forced due to their fault.
            # Can only happen when there are no chips to draw and the board is no longer forced.
            if not self.board.is_forced():
                for player in self.players:
                    if player.is_eligible_to_win():
                        player.declare_as_round_winner()
                        return False

        return not self.players[self.previous_player_id()].is_round_winner()

    def next_turn(self):
        self.players[self.turn].init_turn(self.board)
        can_play = self.players[self.turn].can_play(self.board)

        if not can_play:
            # self.probability_chip_lists[self.turn].remove_numbers(self.players[self.turn].get_numbers_player_does_not_have())
            if self.board.can_draw():
                self.draw_chip()
                can_play = self.players[self.turn].can_play(self.board)

        if can_play:
            self.play()
            if self.endgame:
                self.endgame_countdown = self.n_players
        else:
            # self.probability_chip_lists[self.turn].remove_numbers(self.players[self.turn].get_numbers_player_does_not_have())  # board.getNumbersPlayerXHasAccessTo
            self.board.set_train(self.turn)
            if self.endgame:
                self.endgame_countdown -= 1

        if self.players[self.turn].get_chip_count() == 1 and self.board.can_draw() and not self.players[self.turn].will_say_one():
            logging.info("%s did not say one." % self.players[self.turn].get_name())
            self.draw_chip()

        self.players[self.turn].end_turn(self.board)
        self.turn = self.next_player_id()

    def play(self):
        logging.info("%s plays: " % self.players[self.turn].get_name())
        [cnl, row] = self.players[self.turn].play(self.board, self.players)
        self.validate_play(cnl, row)
        self.make_move(cnl, row)
        if cnl.ends_in_double():
            self.handle_unresolved_doubles(cnl, row)

    def handle_unresolved_doubles(self, cnl, row):
        logging.info("%s ends in double." % self.players[self.turn].get_name())
        self.board.set_forced(row, cnl.get_ending_doubles(), self.turn)
        if self.board.can_draw():
            self.draw_chip()
        if self.players[self.turn].can_play(self.board):
            logging.info("Drew necessary number.")
            [cnl, row] = self.players[self.turn].play(self.board, self.players)
            self.validate_play(cnl, row)
            self.make_move(cnl, row)
        else:
            logging.info("Did not draw necessary number.")

    def make_move(self, cnl, row):
        logging.info("%s plays: %s" % (self.players[self.turn].get_name(), cnl.__str__()))

        # Remove forced
        if self.board.is_forced():
            self.board.remove_forced(cnl.get_best_chip_to_play().get_chip_side_to_play())

        # Remove train
        if self.board.get_row(self.turn).has_train() and self.turn == row and not cnl.ends_in_double() and not self.board.is_forced() and self.players[self.turn].will_remove_train():
            self.board.remove_train(self.turn)

        # Actually make move
        self.remove_chips(cnl)
        self.board.play_chip_node_list(cnl, row)

    def validate_play(self, cnl, row):
        if cnl is None or not cnl.has_chip_to_play():
            raise Exception("Empty move.")
        if not self.players[self.turn].has_chips(cnl.get_chipset()):
            logging.info(cnl.__str__())
            raise Exception("Player tried to play a chip they do not have.")

        if self.board.is_forced():
            if row != self.board.get_forced_row_index():
                logging.info(cnl.__str__())
                raise Exception("Board is forced but player is trying to play somewhere else.")
            if not cnl.has_number_to_play_immediately(self.board.get_forced_numbers()):
                logging.info(cnl.__str__())
                raise Exception("Chip does not contain forced number.")
            if len(cnl) > 1:
                logging.info(cnl.__str__())
                raise Exception("Trying to play too many chips.")
            return

        if not cnl.has_number_to_play_immediately(self.board.get_row(row).get_open_positions()):
            logging.info(cnl.__str__())
            raise Exception("Player tried to play a chip that does not match the numbers in the row.")
        if row != self.turn and self.board.get_row(self.turn).has_train():
            logging.info(cnl.__str__())
            raise Exception("Player tried to play elsewhere, but has train, and is not forced.")
        if row != self.turn and not self.board.get_row(row).has_train():
            logging.info(cnl.__str__())
            raise Exception("Player tried to play in a row without train.")
        if len(cnl) > 1:
            if len(cnl) == 2 and cnl.has_double_to_play_immediately():
                pass
            elif row == self.turn and self.board.get_row(self.turn).can_play_many():
                pass
            else:
                logging.info(cnl.__str__())
                raise Exception("Trying to play too many chips.")

    def previous_player_id(self):
        return (self.turn - 1) % self.n_players

    def next_player_id(self):
        return (self.turn + 1) % self.n_players

    def draw_chip(self):
        logging.info("%s draws chip." % self.players[self.turn].get_name())
        self.players[self.turn].add_chip(self.board.draw())
        # self.probability_chip_lists[player_id].add(self.probability_chip_lists[-1].pop())

    def remove_chips(self, cnl):
        for chip in cnl.get_chipset():
            self.players[self.turn].remove_chip(chip)

    def play_ai_game(self):
        millis = time.time() * 1000

        while self.has_next_round():
            self.init_round()
            while self.has_next_turn():
                self.next_turn()
                logging.info(self)
            self.end_round()

        logging.info(self)
        print("{:.0f}".format(time.time() * 1000 - millis) + " ms")

        winners = []
        for player in self.global_winner:
            winners.append(player.get_index())
        return winners

    def __str__(self):
        s = ["The board looks like this:\n%s\nPlayers:" % self.board.__str__()]
        for player in self.players:
            s.append("\n%s" % player.__str__())
        s.append("\nPlayer's turn: %s" % self.players[self.turn].get_name())
        s.append("\nPlayer(s) in the lead: ")
        for player in self.global_winner:
            s.append("\n%s" % player.get_name())
        s.append("\n\n\n")
        return ''.join(s)
