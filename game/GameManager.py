import logging
import math
import random
import time
from typing import List

from game import ChipFactory, ChipNodeList
from game.Board import Board
from players.HeuristicCPUPlayer import HeuristicCPUPlayer
from players.HumanPlayer import HumanPlayer
from players.RandomCPUPlayer import RandomCPUPlayer
from players.SmartCPUPlayer import SmartCPUCPUPlayer


class GameManager:

    def __init__(self, chips_per_player: int, highest_double: int, initial_double: int, random_py: int, simple_py: int,
                 heuristic_py: int, human_py: int, player_names: List[str] = None, starting_turn: int = -1) -> None:
        self.n_players = random_py + simple_py + heuristic_py + human_py
        self.chips_per_player = chips_per_player
        self.endgame_countdown = self.n_players
        self.highest_double = highest_double
        self.current_double = initial_double
        self.global_winner = []
        self.endgame = False
        self.players = []
        self.board = None
        self.turn = random.randrange(self.n_players) if starting_turn < 0 else starting_turn
        self.player_names = player_names
        if not player_names:
            self.player_names = [i.__str__() for i in range(self.n_players)]

        for i in range(random_py):
            self.players.append(RandomCPUPlayer(i, player_names[i]))
        for i in range(len(self.players), len(self.players) + simple_py):
            self.players.append(SmartCPUCPUPlayer(i, player_names[i]))
        for i in range(len(self.players), len(self.players) + heuristic_py):
            self.players.append(HeuristicCPUPlayer(i, player_names[i], highest_double, chips_per_player))
        for i in range(len(self.players), len(self.players) + human_py):
            self.players.append(HumanPlayer(i, player_names[i]))

    def init_round(self) -> None:
        self.endgame = False
        self.endgame_countdown = self.n_players
        chips = ChipFactory.create_chips(self.highest_double, self.current_double)
        random.shuffle(chips)

        for player in self.players:
            starting_chips = [chips.pop() for _ in range(self.chips_per_player)]
            player.init_round(starting_chips, self.current_double)

        self.board = Board(self.n_players, self.current_double, chips, self.player_names)

    def end_round(self) -> None:
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

        if not round_winner:
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

    def has_next_round(self) -> bool:
        return self.current_double >= 0

    def has_next_turn(self) -> bool:
        # Breaks stalemates where there are no more moves to make.
        if not self.board.can_draw():
            self.endgame = True
            if self.endgame_countdown <= 0:
                return False
            # Rare condition where a player is eligible to win but hasn't because the board used to be forced
            # due to their fault. Can only happen when there are no chips to draw and the board is no longer forced.
            if not self.board.is_forced():
                for player in self.players:
                    if player.is_eligible_to_win():
                        player.declare_as_round_winner()
                        return False

        return not self.players[self.previous_player_id()].is_round_winner()

    def next_turn(self) -> None:
        active_player = self.players[self.turn]
        active_player.init_turn(self.board)

        can_play = active_player.can_play(self.board)
        if not can_play:
            # TODO: Notify other players of missing numbers
            if self.board.can_draw():
                self.draw_chip()
                can_play = active_player.can_play(self.board)

        if can_play:
            self.play()
            if self.endgame:
                self.endgame_countdown = self.n_players
        else:
            # TODO: Notify other players of missing numbers
            self.board.set_train(self.turn)
            if self.endgame:
                self.endgame_countdown -= 1

        if active_player.get_chip_count() == 1 and self.board.can_draw() and not active_player.will_say_one():
            logging.info("%s did not say one." % active_player.get_name())
            self.draw_chip()

        active_player.end_turn(self.board)
        self.turn = self.next_player_id()

    def play(self) -> None:
        active_player = self.players[self.turn]
        logging.info("%s plays: " % active_player.get_name())
        [chip_node_list, row] = active_player.play(self.board, self.players)  # TODO: Can reduce this to ChipNode instead of CNL?
        self.validate_play(chip_node_list, row)
        self.make_move(chip_node_list, row)
        if chip_node_list.ends_in_double():
            self.handle_unresolved_doubles(chip_node_list, row)

    def handle_unresolved_doubles(self, chip_node_list: ChipNodeList, row: int) -> None:
        active_player = self.players[self.turn]
        logging.info("%s ends in double." % active_player.get_name())
        self.board.set_forced(row, chip_node_list.get_ending_doubles(), self.turn)

        if self.board.can_draw():
            self.draw_chip()
        if active_player.can_play(self.board):
            logging.info("Drew necessary number.")
            [chip_node_list, row] = active_player.play(self.board, self.players)
            self.validate_play(chip_node_list, row)
            self.make_move(chip_node_list, row)
        else:
            logging.info("Did not draw necessary number.")

    def make_move(self, chip_node_list: ChipNodeList, row: int) -> None:
        active_player = self.players[self.turn]
        logging.info("%s plays: %s" % (active_player.get_name(), chip_node_list.__str__()))

        # Remove forced
        if self.board.is_forced():
            self.board.remove_forced(chip_node_list.get_best_chip_to_play().get_chip_side_to_play())

        # Remove train
        if (self.board.get_row(self.turn).has_train()
                and self.turn == row
                and not chip_node_list.ends_in_double()
                and not self.board.is_forced()
                and active_player.will_remove_train()):
            self.board.remove_train(self.turn)

        # Actually make move
        self.remove_chips(chip_node_list)
        self.board.play_chip_node_list(chip_node_list, row)

    def validate_play(self, chip_node_list: ChipNodeList, row: int) -> None:
        if not chip_node_list or not chip_node_list.has_chip_to_play():
            raise Exception("Empty move.")
        if not self.players[self.turn].has_chips(chip_node_list.get_chipset()):
            logging.info(chip_node_list.__str__())
            raise Exception("Player tried to play a chip they do not have.")

        if self.board.is_forced():
            if row != self.board.get_forced_row_index():
                logging.info(chip_node_list.__str__())
                raise Exception("Board is forced but player is trying to play somewhere else.")
            if not chip_node_list.has_number_to_play_immediately(self.board.get_forced_numbers()):
                logging.info(chip_node_list.__str__())
                raise Exception("Chip does not contain forced number.")
            if len(chip_node_list) > 1:
                logging.info(chip_node_list.__str__())
                raise Exception("Trying to play too many chips.")
            return

        if not chip_node_list.has_number_to_play_immediately(self.board.get_row(row).get_open_positions()):
            logging.info(chip_node_list.__str__())
            raise Exception("Player tried to play a chip that does not match the numbers in the row.")
        if row != self.turn and self.board.get_row(self.turn).has_train():
            logging.info(chip_node_list.__str__())
            raise Exception("Player tried to play elsewhere, but has train and is not forced.")
        if row != self.turn and not self.board.get_row(row).has_train():
            logging.info(chip_node_list.__str__())
            raise Exception("Player tried to play in a row without train.")
        if len(chip_node_list) > 1:
            if row == self.turn and self.board.get_row(self.turn).can_play_many():
                pass
            elif len(chip_node_list) == 2 and chip_node_list.has_double_to_play_immediately():
                pass
            else:
                logging.info(chip_node_list.__str__())
                raise Exception("Trying to play too many chips.")
        elif chip_node_list.has_double_to_play_immediately():
            double = chip_node_list.get_chipset()[0]
            for chip in self.players[self.turn].chips:
                if chip.__contains__(double.get_side_a()) and chip != double:
                    logging.info(chip_node_list.__str__())
                    raise Exception("Player played a double but withheld from resolving it.")

    def previous_player_id(self) -> int:
        return (self.turn - 1) % self.n_players

    def next_player_id(self) -> int:
        return (self.turn + 1) % self.n_players

    def draw_chip(self) -> None:
        logging.info("%s draws chip." % self.players[self.turn].get_name())
        self.players[self.turn].add_chip(self.board.draw())
        # TODO: Notify players

    def remove_chips(self, chip_node_list: ChipNodeList) -> None:
        for chip in chip_node_list.get_chipset():
            self.players[self.turn].remove_chip(chip)

    def play_ai_game(self) -> List[int]:
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

    def __str__(self) -> str:
        s = ["The board looks like this:\n%s\nPlayers:" % self.board.__str__()]
        for player in self.players:
            s.append("\n%s" % player.__str__())
        s.append("\nPlayer's turn: %s" % self.players[self.turn].get_name())
        s.append("\nPlayer(s) in the lead: ")
        for player in self.global_winner:
            s.append("\n%s" % player.get_name())
        s.append("\n\n\n")
        return ''.join(s)
