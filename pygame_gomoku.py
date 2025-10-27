import pygame
import sys
import numpy as np
from game_logic import create_board, make_move, get_winner, position_is_empty, generate_next_move_random

pygame.init()

BOARD_SIZE = 15
CELL_SIZE = 40
MARGIN = 50
WINDOW_SIZE = BOARD_SIZE * CELL_SIZE + 2 * MARGIN
INFO_HEIGHT = 60

BOARD_COLOR = (240, 217, 181)
LINE_COLOR = (0, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
HOVER_COLOR = (255, 0, 0, 100)
HIGHLIGHT_COLOR = (255, 215, 0)
INFO_COLOR = (70, 70, 70)

FONT = pygame.font.Font(None, 36)
FONT_SMALL = pygame.font.Font(None, 24)

class GomokuGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + INFO_HEIGHT))
        pygame.display.set_caption("Gomoku")
        self.clock = pygame.time.Clock()
        self.game = create_board(BOARD_SIZE).astype(np.int8)
        self.current_player = 1
        self.game_over = False
        self.winner = None
        self.last_move = None
        self.states = []  # saves state > export 

    def pixel_to_board_pos(self, pos):
        x, y = pos
        col = (x - MARGIN) // CELL_SIZE # j
        row = (y - MARGIN) // CELL_SIZE  # i > swapped col/ row
        if 0 <= col < BOARD_SIZE and 0 <= row < BOARD_SIZE:
            return row, col
        return None, None

    def get_pixelcoords(self, row, col): #renderer/game_logic helpers
        x = MARGIN + col * CELL_SIZE
        y = MARGIN + row * CELL_SIZE
        return x, y

    def draw_board(self):
        self.screen.fill(BOARD_COLOR)
        for i in range(BOARD_SIZE):
            x = MARGIN + i * CELL_SIZE
            pygame.draw.line(self.screen, LINE_COLOR, (x, MARGIN), (x, MARGIN + (BOARD_SIZE-1) * CELL_SIZE), 2)
            y = MARGIN + i * CELL_SIZE
            pygame.draw.line(self.screen, LINE_COLOR, (MARGIN, y), (MARGIN + (BOARD_SIZE-1) * CELL_SIZE, y), 2)
        star_points = [(3, 3), (3, 11), (11, 3), (11, 11), (7, 7)]
        for row, col in star_points:
            px, py = self.get_pixelcoords(row, col)
            pygame.draw.circle(self.screen, LINE_COLOR, (px, py), 4)

    def draw_stone(self, row, col, player, highlight=False):
        x, y = self.get_pixelcoords(row, col)
        radius = CELL_SIZE // 2 - 2
        color = BLACK if player == 1 else WHITE
        pygame.draw.circle(self.screen, color, (x, y), radius)
        if player == 2:
            pygame.draw.circle(self.screen, LINE_COLOR, (x, y), radius, 1)
        if highlight:
            pygame.draw.circle(self.screen, HIGHLIGHT_COLOR, (x, y), radius + 2, 3)

    def draw_hover(self, row, col):
        if row is None or col is None:
            return
        if position_is_empty(self.game, row, col):
            x, y = self.get_pixelcoords(row, col)
            radius = CELL_SIZE // 3
            s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, HOVER_COLOR, (radius, radius), radius)
            self.screen.blit(s, (x - radius, y - radius))

    def draw_stones(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.game[row, col] != 0:
                    highlight = (self.last_move == (row, col))
                    self.draw_stone(row, col, int(self.game[row, col]), highlight)

    def draw_info(self):
        info_rect = pygame.Rect(0, WINDOW_SIZE, WINDOW_SIZE, INFO_HEIGHT)
        pygame.draw.rect(self.screen, INFO_COLOR, info_rect)
        if self.game_over:
            if self.winner:
                text = f"Spieler {'Schwarz' if self.winner == 1 else 'Weiss'} gewinnt!"
                color = HIGHLIGHT_COLOR
            else:
                text = "Unentschieden!"
                color = WHITE
        else:
            text = f"Spieler {'Schwarz' if self.current_player == 1 else 'Weiss'} ist am Zug"
            color = WHITE
        text_surface = FONT.render(text, True, color)
        text_rect = text_surface.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE + INFO_HEIGHT//2))
        self.screen.blit(text_surface, text_rect)
        if self.game_over:
            restart_text = FONT_SMALL.render("R fuer Restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE + INFO_HEIGHT - 15))
            self.screen.blit(restart_text, restart_rect)

    def process_click(self, pos):
        if self.game_over:
            return
        row, col = self.pixel_to_board_pos(pos)
        if row is None or col is None:
            return
        if position_is_empty(self.game, row, col):
            make_move(self.game, row, col, self.current_player)
            self.last_move = (row, col)
            self.states.append(self.game.copy())  # save
            winner = get_winner(self.game, 5)
            if winner in (1, 2):
                self.game_over = True
                self.winner = winner
            elif winner == -1:
                self.game_over = True
                self.winner = None
            else:
                self.current_player = (self.current_player % 2) + 1
                # Bot move > when player 2s rurn
                if self.current_player == 2:
                    y, x = generate_next_move_random(self.game, 2)
                    self.last_move = (y, x)
                    self.states.append(self.game.copy())
                    winner = get_winner(self.game, 5)
                    if winner in (1, 2):
                        self.game_over = True
                        self.winner = winner
                    elif winner == -1:
                        self.game_over = True
                        self.winner = None
                    else:
                        self.current_player = 1

    def restart_game(self):
        self.game = create_board(BOARD_SIZE).astype(np.int8)
        self.current_player = 1
        self.game_over = False
        self.winner = None
        self.last_move = None
        self.states = []

    def export_game_states(self, filename="game_states.npy"):
        np.save(filename, np.array(self.states, dtype=np.int8))
        print(f"Game states saved to {filename}")

    def run(self):
        running = True
        while running:
            pos = pygame.mouse.get_pos()
            hover_row, hover_col = self.pixel_to_board_pos(pos)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.process_click(pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.restart_game()
                    elif event.key == pygame.K_e:
                        self.export_game_states()
                    elif event.key == pygame.K_ESCAPE:
                        running = False
            self.draw_board()
            self.draw_stones()
            if not self.game_over:
                self.draw_hover(hover_row, hover_col)
            self.draw_info()
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = GomokuGame()
    game.run()
