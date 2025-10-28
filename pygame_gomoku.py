import pygame
import sys
import numpy as np
from game_logic import (
    create_board,
    make_move,
    has_player_won,
    position_is_empty,
    generate_next_move_random,
    get_winner,
    is_board_full
)
from config import *

pygame.init()

FONT = pygame.font.Font(None, FONT_SIZE_LARGE)
FONT_SMALL = pygame.font.Font(None, FONT_SIZE_SMALL)


class GomokuGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + INFO_HEIGHT))
        pygame.display.set_caption("Gomoku")
        self.clock = pygame.time.Clock()
        self.game = create_board(BOARD_SIZE)
        self.current_player = PLAYER_BLACK
        self.game_over = False
        self.winner = None
        self.last_move = None
        self.states = []
        
    def pixel_to_board_pos(self, pos):
        """pixel coordinates to board"""
        x, y = pos
        col = round((x - MARGIN) / CELL_SIZE) # j
        row = round((y - MARGIN) / CELL_SIZE) # i > swapped col/row
        
        if 0 <= col < BOARD_SIZE and 0 <= row < BOARD_SIZE:
            return row, col
        return None, None
    
    def get_pixelcoords(self, row, col): # reenderer/game_logic helpers
        """board coordinates to pixel"""
        x = MARGIN + col * CELL_SIZE
        y = MARGIN + row * CELL_SIZE
        return x, y
    
    def draw_board(self):

        self.screen.fill(BOARD_COLOR)
        
        # grid 
        for i in range(BOARD_SIZE):
            # vertical 
            x = MARGIN + i * CELL_SIZE
            pygame.draw.line(self.screen, LINE_COLOR, 
                           (x, MARGIN), 
                           (x, MARGIN + (BOARD_SIZE - 1) * CELL_SIZE), 2)
            
            # horizontal
            y = MARGIN + i * CELL_SIZE
            pygame.draw.line(self.screen, LINE_COLOR, 
                           (MARGIN, y), 
                           (MARGIN + (BOARD_SIZE - 1) * CELL_SIZE, y), 2)
        
        # starpoints (15x15 board)
        if BOARD_SIZE == 15:
            star_points = [(3, 3), (3, 11), (11, 3), (11, 11), (7, 7)]
            for row, col in star_points:
                px, py = self.get_pixelcoords(row, col)
                pygame.draw.circle(self.screen, LINE_COLOR, (px, py), 4)
    
    def draw_stone(self, row, col, player, highlight=False):
        """stone at the given board position"""
        x, y = self.get_pixelcoords(row, col)
        radius = CELL_SIZE // 2 - 2
        
        color = BLACK if player == PLAYER_BLACK else WHITE
        pygame.draw.circle(self.screen, color, (x, y), radius)
        
        # outline for white stones
        if player == PLAYER_WHITE:
            pygame.draw.circle(self.screen, LINE_COLOR, (x, y), radius, 1)
        
        # highlight > last move
        if highlight:
            pygame.draw.circle(self.screen, HIGHLIGHT_COLOR, (x, y), radius + 2, 3)
    
    def draw_hover(self, row, col):
        """hover indicator at valid positions"""
        if row is None or col is None:
            return
            
        if self.is_valid(row, col):
            x, y = self.get_pixelcoords(row, col)
            radius = CELL_SIZE // 3
            
            s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, HOVER_COLOR, (radius, radius), radius)
            self.screen.blit(s, (x - radius, y - radius))

    def is_valid(self, row, col):
        """if a move is valid > in bounds and empty"""
        return (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE) and \
               position_is_empty(self.game, row, col)
    
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
                text = f"Spieler {'Schwarz' if self.winner == PLAYER_BLACK else 'Weiß'} gewinnt!"
                color = HIGHLIGHT_COLOR
            else:
                text = "Unentschieden!"
                color = WHITE
        else:
            text = f"Spieler {'Schwarz' if self.current_player == PLAYER_BLACK else 'Weiß'} ist am Zug"
            color = WHITE
        
        text_surface = FONT.render(text, True, color)
        text_rect = text_surface.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE + INFO_HEIGHT // 2))
        self.screen.blit(text_surface, text_rect)
        
        # restart
        if self.game_over:
            restart_text = FONT_SMALL.render("R für Restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE + INFO_HEIGHT - 15))
            self.screen.blit(restart_text, restart_rect)
    
    def process_click(self, pos):
        """mouse click for human player move"""
        if self.game_over:
            return
            
        row, col = self.pixel_to_board_pos(pos)
        
        if row is None or col is None:
            return
            
        if self.is_valid(row, col):
            make_move(self.game, row, col, self.current_player)
            self.last_move = (row, col)
            self.states.append(self.game.copy())
            
            # won? 
            winner = get_winner(self.game, WIN_CONDITION)
            if winner in (PLAYER_BLACK, PLAYER_WHITE):
                self.game_over = True
                self.winner = winner
            elif winner == -1:  # draw
                self.game_over = True
                self.winner = None
            else:
                # swtich player: 1 -> 2, 2 -> 1
                self.current_player = (self.current_player % 2) + 1
    
    def restart_game(self):
        """reset > initial state"""
        self.game = create_board(BOARD_SIZE) 
        self.current_player = PLAYER_BLACK
        self.game_over = False
        self.winner = None
        self.last_move = None
        self.states = []
    
    def process_bot_move(self):
        """move for the bot player (Player 1 = Black)"""
        if self.game_over or self.current_player != PLAYER_BLACK:
            return

        row, col = generate_next_move_random(self.game, self.current_player)
        self.last_move = (row, col)
        self.states.append(self.game.copy())

        # win? > get_winner from game_logic
        winner = get_winner(self.game, WIN_CONDITION)
        if winner in (PLAYER_BLACK, PLAYER_WHITE):
            self.game_over = True
            self.winner = winner
        elif winner == -1:  # Draw
            self.game_over = True
            self.winner = None
        else:
            # switch player: 1 -> 2, 2 -> 1
            self.current_player = (self.current_player % 2) + 1
    
    def run(self):
        running = True
        
        while running:
            pos = pygame.mouse.get_pos()
            hover_row, hover_col = self.pixel_to_board_pos(pos)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.current_player == PLAYER_WHITE:  # human player
                        self.process_click(pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.restart_game()
                    elif event.key == pygame.K_ESCAPE:
                        running = False
            
            self.draw_board()
            self.draw_stones()
            
            if not self.game_over and self.current_player == PLAYER_BLACK:
                self.process_bot_move()
                
            if not self.game_over and self.current_player == PLAYER_WHITE:
                self.draw_hover(hover_row, hover_col)
            
            self.draw_info()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = GomokuGame()
    game.run()