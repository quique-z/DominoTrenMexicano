from players.BasicPlayer import Player
from players.SimpleAIPlayer import SimpleAIPlayer
from game.ChipFactory import *
from game.Board import Board
import random
import math
import time


class GameManager:

    def __init__(self, n_chips_per_player, highest_double, initial_double, basic_py, simple_py, player_names=[]):
        if len(player_names) == 0:
            for i in basic_py + simple_py:
                player_names.append(i.__str__())
        self.chips = []
        self.n_chips_per_player = n_chips_per_player
        self.highest_double = highest_double
        self.current_double = initial_double
        self.board = None
        self.turn = 0
        self.endgame = False
        self.global_winner = []
        self.n_players = basic_py + simple_py
        self.endgame_countdown = self.n_players
        self.player_names = player_names
        players = []
        for i in range(basic_py):
            players.append(Player(i, player_names[i]))
        for i in range(basic_py, self.n_players):
            players.append(SimpleAIPlayer(i, player_names[i]))
        self.players = players

    def init_round(self):
        self.chips = create_chips(self.highest_double, self.current_double)
        random.shuffle(self.chips)

        for player in self.players:
            chips = []
            for i in range(self.n_chips_per_player):
                chips.append(self.chips.pop())
            player.init_round(chips)

        self.board = Board(len(self.players), self.current_double, self.chips, self.player_names)
        self.current_double -= 1

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

        self.turn = round_winner.get_index()

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
                        player.declare_round_winner()

        return not self.players[self.previous_player_id()].is_round_winner()

    def next_turn(self):
        can_play = self.players[self.turn].can_play_any(self.board)

        if not can_play and self.board.can_draw():
            self.players[self.turn].add_chip(self.board.draw())
            can_play = self.players[self.turn].can_play_any(self.board)

        if can_play:
            self.players[self.turn].play(self.board)
            if self.endgame:
                self.endgame_countdown = len(self.players)
        else:
            self.board.set_train(self.turn)
            if self.endgame:
                self.endgame_countdown -= 1

        self.turn = self.next_player_id()

    def has_next_round(self):
        return self.current_double >= 0

    def previous_player_id(self):
        return (self.turn - 1) % len(self.players)

    def next_player_id(self):
        return (self.turn + 1) % len(self.players)

    def play_ai_game(self):
        millis = time.time() * 1000

        while self.has_next_round():
            self.init_round()
            while self.has_next_turn():
                print(self)
                self.next_turn()
            self.end_round()

        print(self)
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
