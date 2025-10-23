import numpy as np


def create_game(size: int = 15):
    return np.zeros((size, size), dtype=np.int8)


def is_valid(game, x: int, y: int) -> bool:
    return game[y, x] == 0


def make_move(game, x: int, y: int, player: int):
    assert player in [1, 2], "Invalid player"
    game[y, x] = player


def _has_won_helper(arr, n: int, player: int):
    mask = (arr == player).astype(int)
    kernel = np.ones(n, dtype=int)  # dim of win condition

    conv = np.convolve(mask, kernel, mode="valid")
    return np.any(conv == n)


def has_won(board, n: int, player: int) -> bool:
    """
    n is the number of consecutive pieces required to win
    """
    size = board.shape[0]
    for i in range(0, size):
        col = board[:, i]
        if _has_won_helper(col, n, player):
            return True
        row = board[i, :]
        if _has_won_helper(row, n, player):
            return True

    # Check diagonals
    for offset in range(-size + n, size - n + 1):
        diag1 = np.diag(board, k=offset)
        if _has_won_helper(diag1, n, player):
            return True
        diag2 = np.diag(np.fliplr(board), k=offset)
        if _has_won_helper(diag2, n, player):
            return True
    return False
