from __future__ import print_function
import sys

sys.path.append("..")

from Game import Game
import numpy as np

from ctypes import *

from .XiangqiLogic import (
    BOARD_SIZE,
    NUM_ROWS,
    NUM_COLS,
    get_init_board,
    move,
    valid_moves,
    get_winner,
    flip_board,
    encode_board_state,
    board_str,
    mirror_horizontal,
)


class XiangqiGame(Game):

    def __init__(self):
        pass

    def getInitBoard(self):
        # return initial board (numpy board)
        return get_init_board()

    def getBoardSize(self):
        return (1, BOARD_SIZE)

    def getActionSize(self):
        # return number of actions
        return BOARD_SIZE * BOARD_SIZE

    def getNextState(self, board, player, action):
        from_pos = action // 90
        to_pos = action % 90
        return (move(board, c_uint16((from_pos << 8) | to_pos)), -player)

    def getValidMoves(self, board, player):
        res = np.zeros(self.getActionSize(), dtype=np.int8)
        n, moves = valid_moves(board, player)
        if n == 0:
            return res
        for i in range(n):
            move = moves[i]
            from_pos = (move & 0xFF00) >> 8
            to_pos = move & 0xFF
            res[from_pos * 90 + to_pos] = 1
        return res

    def getGameEnded(self, board, player):
        winner = get_winner(board)
        if winner == -2:
            return 0
        return winner

    def getCanonicalForm(self, board, player):
        # return state if player==1, else return -state if player==-1
        if player == 1:
            return board
        return flip_board(board)

    def getSymmetries(self, board, pi):
        # assert len(pi) == self.getActionSize()
        # mirror_lr = mirror_horizontal(board)
        # pi_lr = pi.copy()
        # for i in range(BOARD_SIZE):
        #     for row in range(NUM_ROWS):
        #         row_start = i * BOARD_SIZE + row * NUM_COLS
        #         for col in range(NUM_COLS // 2):
        #             left = pi_lr[row_start + col]
        #             pi_lr[row_start + col] = pi_lr[row_start + NUM_COLS - 1 - col]
        #             pi_lr[row_start + NUM_COLS - 1 - col] = left
        # return [(mirror_lr, pi_lr)]
        return []

    def stringRepresentation(self, board):
        return encode_board_state(board)

    @staticmethod
    def display(board: np.ndarray):
        print(board_str(board))
