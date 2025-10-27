import random

import numpy as np
import numpy.typing as npt
import threading


_thread_local = threading.local()

def get_random() -> random.Random:
    global _thread_local
    if not hasattr(_thread_local, "rng"):
        _thread_local.rng = random.Random()  
    return _thread_local.rng
    
def create_board(size: int = 15):
    return np.zeros((size, size), dtype=np.int8)


def position_is_empty(board: npt.NDArray, y: int, x: int) -> bool:
    return board[y, x] == 0


def is_board_full(board: npt.NDArray) -> bool:
    return not np.any(board == 0)


def make_move(board: npt.NDArray, y: int, x: int, player: int):
    if not (0 <= y < board.shape[0]):
        raise ValueError("y value out of board range")
    if not (0 <= x < board.shape[1]):
        raise ValueError("x value out of board range")
    if player not in [1, 2]:
        raise ValueError("player must be either 1 or 2")
    if not (position_is_empty(board, y, x)):
        raise RuntimeError("position already occupied")
    board[y, x] = player


def _get_random_empty_position(board: npt.NDArray, rng: random.Random) -> tuple[int, int]:
    """
    Return a random (y, x) that is currently empty.
    """

    empties = np.argwhere(board == 0)  # shape: (k, 2) rows of empty [y, x] points
    if len(empties) == 0:
        raise RuntimeError("board is full")

    y, x = rng.choice(empties)
    return y, x


def generate_next_move_random(board: npt.NDArray, player: int) -> tuple[int, int]:
    """
    Perform a random, but valid move for the given player.
    Returns the (y, x) position where the move was performed.
    """
    
    if not (player in [1, 2]):
        raise RuntimeError("player must be either 1 or 2")

    y, x = _get_random_empty_position(board, get_random())
    make_move(board, y, x, player)
    return y, x

def _has_player_won_helper(board: npt.NDArray, n: int, player: int):
    mask = (board == player).astype(int)
    kernel = np.ones(n, dtype=int)  # dim of win condition

    conv = np.convolve(mask, kernel, mode="valid")
    return np.any(conv == n)


def has_player_won(board: npt.NDArray, n: int, player: int) -> bool:
    """
    returns true if the win condition is satisfied by the given player (n in a row), otherwise false
    """

    # Check horizontals
    size = board.shape[0]
    for i in range(0, size):
        col = board[:, i]
        if _has_player_won_helper(col, n, player):
            return True
        row = board[i, :]
        if _has_player_won_helper(row, n, player):
            return True

    # Check diagonals
    for offset in range(-size + n, size - n + 1):
        diag1 = np.diag(board, k=offset)
        if _has_player_won_helper(diag1, n, player):
            return True
        diag2 = np.diag(np.fliplr(board), k=offset)
        if _has_player_won_helper(diag2, n, player):
            return True
    return False

def get_winner(board: npt.NDArray, n: int) -> int:
    """
    returns the winner of the given board.
    1 = player1 won
    2 = player2 won
    -1 = no winner, board is full
    0 = no winner, game still in progress
    """

    for player in (1, 2):
        if has_player_won(board, n, player):
            return player
    return -1 if is_board_full(board) else 0
