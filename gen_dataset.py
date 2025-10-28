import numpy as np
from game_logic import create_board, generate_next_move_random, get_winner
from PIL import Image, ImageDraw
from renderer import render, calc_coords_gomoku


def play_random_game(size: int = 15, n: int = 5) -> np.ndarray:
    """
    Play a random Gomoku game with 2 random actors.
    Returns a 3D array of shape (num_moves, size, size) representing the board after each move.
    """
    board = create_board(size)
    game_states = []
    current_player = 1

    while True:
        y, x = generate_next_move_random(board, current_player)
        print(f"Player {current_player} placed at (y={y}, x={x})")

        game_states.append(board.copy())

        winner = get_winner(board, n)
        if winner != 0:
            if winner == -1:
                print("Game ended in a draw.")
            else:
                print(f"Player {winner} wins!")
            break

        current_player = (current_player % 2) + 1

    return np.stack(game_states)


def create_gomoku_board(
    size: int = 15, cell_size: int = 40, margin: int = 20, line_width: int = 2
):
    board_px = size * cell_size + 2 * margin
    img = Image.new("RGB", (board_px, board_px), color=(238, 178, 73))
    draw = ImageDraw.Draw(img)

    for i in range(size + 1):
        offset = margin + i * cell_size
        draw.line(
            (margin, offset, board_px - margin, offset),
            width=line_width,
            fill=(0, 0, 0),
        )
        draw.line(
            (offset, margin, offset, board_px - margin),
            width=line_width,
            fill=(0, 0, 0),
        )

    if size == 15:
        star_positions = [(3, 3), (3, 11), (7, 7), (11, 3), (11, 11)]
        star_radius = max(2, cell_size // 8)
        for r, c in star_positions:
            cx = margin + c * cell_size
            cy = margin + r * cell_size
            draw.ellipse(
                (
                    cx - star_radius,
                    cy - star_radius,
                    cx + star_radius,
                    cy + star_radius,
                ),
                fill=(0, 0, 0),
            )

    return img


def create_gomoku_stone(color: str = "black", size: int = 40) -> Image.Image:
    scale = 4
    large_size = size * scale

    img = Image.new("RGBA", (large_size, large_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.ellipse((0, 0, large_size - 1, large_size - 1), fill=color, outline="black")

    highlight = Image.new("RGBA", (large_size, large_size), (0, 0, 0, 0))
    hdraw = ImageDraw.Draw(highlight)
    hdraw.ellipse(
        (large_size * 0.1, large_size * 0.1, large_size * 0.6, large_size * 0.6),
        fill=(255, 255, 255, 100),
    )
    img = Image.alpha_composite(img, highlight)

    img = img.resize((size, size), Image.LANCZOS)
    return img


def create_pieces(cell_size=40):
    black_piece = create_gomoku_stone("black", cell_size)
    white_piece = create_gomoku_stone("white", cell_size)

    return [black_piece, white_piece]


def render_game_steps(game_states: np.ndarray):
    prev_state = None
    board_img = create_gomoku_board()
    pieces = create_pieces()

    def calc_coords_gomoku_wrapper(i: int, j: int):
        return calc_coords_gomoku(i, j, 40, (20, 20))

    for i, state in enumerate(game_states):
        move_num = i + 1
        print(f"Rendering move {move_num}...")

        board_img = render(
            board_img,
            pieces,
            state,
            prev_state.astype(np.int8) if prev_state is not None else None,
            calc_coords=calc_coords_gomoku_wrapper,
        )

        board_img.save(f"move_{move_num:03d}.png")

        prev_state = state


if __name__ == "__main__":
    game_states = play_random_game()
    render_game_steps(game_states)
