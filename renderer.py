import numpy as np
from PIL import Image
import numpy.typing as npt
from typing import Callable, Literal

Orientation = Literal["tl", "tc", "tr", "cl", "cc", "cr", "bl", "bc", "br"]
CalcCoordsFn = Callable[[int, int], tuple[int, int, int, int, Orientation]]


def calc_coords_gomoku(
    i: int, j: int, cell_size: int = 40, board_origin: tuple[int, int] = (0, 0)
):
    """
    Calculate the coordinates of a piece on the game board.
    """
    x0, y0 = board_origin
    w = h = cell_size

    x = x0 + j * cell_size
    y = y0 + i * cell_size
    return x, y, w, h, "tl"


def fix_xy(x: int, y: int, w: int, h: int, center: Orientation) -> tuple[int, int]:
    """
    Adjust the coordinates of a piece based on its center orientation.
    """
    hor_factor = {"l": 0, "c": 0.5, "r": 1}
    ver_factor = {"t": 0, "c": 0.5, "b": 1}

    f, s = center
    x = int(x - w * hor_factor[s])
    y = int(y - h * ver_factor[f])

    return x, y


def render_single(
    img: Image.Image, i: int, j: int, piece: Image.Image, calc_coords: CalcCoordsFn
) -> Image.Image:
    """
    Render a single piece on the game board.
    """
    x, y, w, h, center = calc_coords(i, j)
    x, y = fix_xy(x, y, w, h, center)
    piece = piece.resize((w, h), Image.LANCZOS) if img.size != (w, h) else piece
    img.paste(piece, (x, y), piece if piece.mode == "RGBA" else None)
    return img


def render(
    img: Image.Image,
    pieces: list[Image.Image],
    points: npt.NDArray[np.int8],
    old_points: npt.NDArray[np.int8] | None = None,
    calc_coords: CalcCoordsFn = calc_coords_gomoku,
) -> Image.Image:
    """
    Main render function
    """
    assert points.ndim == 2, f"Expected 2D array, got {points.ndim}D array"
    assert points.shape[0] == points.shape[1], (
        f"Expected square array, got {points.shape}"
    )
    assert points.dtype == np.int8, f"Expected int8 array, got {points.dtype}"
    if old_points is not None:
        assert old_points.shape == points.shape, f"{old_points.shape} != {points.shape}"
        assert points.dtype == old_points.dtype, f"{points.dtype} != {old_points.dtype}"
        indices = np.argwhere((points != old_points) & (points != 0))
    else:
        indices = np.nonzero(points)
    for i, j in zip(*indices):
        img = render_single(img, i, j, pieces[points[i, j] - 1], calc_coords)
    return img
