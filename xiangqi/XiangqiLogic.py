import os
import sys
import base64
import faulthandler

import numpy as np

from ctypes import *
from typing import Tuple

faulthandler.enable()

NUM_COLS = 9
NUM_ROWS = 10
BOARD_SIZE = 90
BOARD_STR_SIZE = 232
MAX_POSSIBLE_MOVES = 112

_LIBC_PATH = "xiangqi/lib/xiangqi_libc.so"

if not os.path.exists(_LIBC_PATH) and os.path.isfile(_LIBC_PATH):
    print("Cannot find lib/xiangqi_libc.so.", file=sys.stderr)
    sys.exit(1)

_libc = CDLL(_LIBC_PATH)
_libc.ResetBoard_C.argtypes = [POINTER(c_int8)]
_libc.CopyBoard_C.argtypes = [POINTER(c_int8), POINTER(c_int8)]
_libc.Move_C.argtypes = [POINTER(c_int8), c_uint16]
_libc.PossibleMoves_C.argtypes = [POINTER(c_int8), c_bool, c_bool, POINTER(c_uint16)]
_libc.GetWinner_C.argtypes = [POINTER(c_int8)]
_libc.FlipBoard_C.argtypes = [POINTER(c_int8), POINTER(c_int8)]
_libc.MirrorBoardHorizontal_C.argtypes = [POINTER(c_int8), POINTER(c_int8)]
_libc.MirrorBoardVertical_C.argtypes = [POINTER(c_int8), POINTER(c_int8)]
_libc.EncodeBoardState_C.argtypes = [POINTER(c_int8), POINTER(c_uint64)]
_libc.BoardToString_C.argtypes = [POINTER(c_int8), POINTER(c_char)]

_init_board_buff = create_string_buffer(BOARD_SIZE)
_init_board = cast(_init_board_buff, POINTER(c_int8))
_libc.ResetBoard_C(_init_board)
_np_init_board = np.ctypeslib.as_array(_init_board, shape=(BOARD_SIZE,)).copy()


def get_init_board() -> np.ndarray:
    return _np_init_board.copy()


def move(board: np.ndarray, action: c_uint16) -> np.ndarray:
    if (
        board.dtype != np.int8
        or not board.flags.writeable
        or not board.flags.c_contiguous
    ):
        board = np.ascontiguousarray(board, dtype=np.int8)
    board_buff = create_string_buffer(b"\000", BOARD_SIZE)
    board_c = cast(board_buff, POINTER(c_int8))
    _libc.CopyBoard_C(board_c, board.ctypes.data_as(POINTER(c_int8)))
    _libc.Move_C(board_c, action)
    return np.ctypeslib.as_array(board_c, shape=(BOARD_SIZE,)).copy()


def valid_moves(board: np.ndarray, player: int) -> Tuple[c_uint8, np.ndarray]:
    if board.dtype != np.int8 or not board.flags.c_contiguous:
        board = np.ascontiguousarray(board, dtype=np.int8)
    board_c = board.ctypes.data_as(POINTER(c_int8))
    str_buff = create_string_buffer(b"\000", MAX_POSSIBLE_MOVES * 2)
    buff = cast(str_buff, POINTER(c_uint16))
    player_c = True
    if player < 0:
        player_c = False
    num_moves = _libc.PossibleMoves_C(board_c, player_c, False, buff)
    return (num_moves, np.ctypeslib.as_array(buff, shape=(MAX_POSSIBLE_MOVES,)).copy())


def get_winner(board: np.ndarray) -> c_int8:
    if board.dtype != np.int8 or not board.flags.c_contiguous:
        board = np.ascontiguousarray(board, dtype=np.int8)
    board_c = board.ctypes.data_as(POINTER(c_int8))
    return _libc.GetWinner_C(board_c)


def flip_board(board: np.ndarray) -> np.ndarray:
    if board.dtype != np.int8 or not board.flags.c_contiguous:
        board = np.ascontiguousarray(board, dtype=np.int8)
    res_buff = create_string_buffer(b"\000", BOARD_SIZE)
    res = cast(res_buff, POINTER(c_int8))
    _libc.FlipBoard_C(res, board.ctypes.data_as(POINTER(c_int8)))
    return np.ctypeslib.as_array(res, shape=(BOARD_SIZE,)).copy()


def mirror_horizontal(board: np.ndarray) -> np.ndarray:
    if board.dtype != np.int8 or not board.flags.c_contiguous:
        board = np.ascontiguousarray(board, dtype=np.int8)
    res_buff = create_string_buffer(b"\000", BOARD_SIZE)
    res = cast(res_buff, POINTER(c_int8))
    _libc.MirrorBoardHorizontal_C(res, board)
    return np.ctypeslib.as_array(res, shape=(BOARD_SIZE,)).copy()


def mirror_vertical(board: np.ndarray) -> np.ndarray:
    if board.dtype != np.int8 or not board.flags.c_contiguous:
        board = np.ascontiguousarray(board, dtype=np.int8)
    res_buff = create_string_buffer(b"\000", BOARD_SIZE)
    res = cast(res_buff, POINTER(c_int8))
    _libc.MirrorBoardVertical_C(res, board)
    return np.ctypeslib.as_array(res, shape=(BOARD_SIZE,)).copy()


def encode_board_state(board: np.ndarray) -> str:
    if board.dtype != np.int8 or not board.flags.c_contiguous:
        board = np.ascontiguousarray(board, dtype=np.int8)
    res_buff = create_string_buffer(32)
    res = cast(res_buff, POINTER(c_uint64))
    board_c = board.ctypes.data_as(POINTER(c_int8))
    _libc.EncodeBoardState_C(board_c, res)
    return base64.b64encode(bytes(res_buff)).decode("utf-8")


def board_str(board: np.ndarray) -> str:
    if board.dtype != np.int8 or not board.flags.c_contiguous:
        board = np.ascontiguousarray(board, dtype=np.int8)
    board_c = board.ctypes.data_as(POINTER(c_int8))
    res = create_string_buffer(BOARD_STR_SIZE)
    _libc.BoardToString_C(board_c, res)
    return res.value.decode("utf-8")
