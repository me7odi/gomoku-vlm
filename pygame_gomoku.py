import pygame
import sys
import numpy as np
import argparse 
import pygame.gfxdraw
from pathlib import Path
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
    def __init__(self, board_size=15, bot_mode="random", two_player=False):
        self.board_size = board_size
        self.bot_mode = bot_mode
        self.two_player = two_player
        
        # recalculate window size
        self.cell_size = CELL_SIZE
        self.margin = MARGIN
        self.window_size = self.board_size * self.cell_size + 2 * self.margin
        
        self.screen = pygame.display.set_mode((self.window_size, self.window_size + INFO_HEIGHT))
        pygame.display.set_caption("Gomoku")
        self.clock = pygame.time.Clock()
        self.game = create_board(self.board_size)
        self.current_player = PLAYER_BLACK
        self.game_over = False
        self.winner = None
        self.last_move = None
        self.states = []
        
    def pixel_to_board_pos(self, pos):
        """pixel coordinates to board"""
        x, y = pos
        col = round((x - self.margin) / self.cell_size) # j
        row = round((y - self.margin) / self.cell_size) # i > swapped col/row
        
        if 0 <= col < self.board_size and 0 <= row < self.board_size:
            return row, col
        return None, None
    
    def get_pixelcoords(self, row, col): # renderer/game_logic helpers
        """board coordinates to pixel"""
        x = self.margin + col * self.cell_size
        y = self.margin + row * self.cell_size
        return x, y
    
    def draw_board(self):

        self.screen.fill(BOARD_COLOR)
        
        # grid 
        for i in range(self.board_size):
            # vertical 
            x = self.margin + i * self.cell_size
            pygame.draw.line(self.screen, LINE_COLOR, 
                           (x, self.margin), 
                           (x, self.margin + (self.board_size - 1) * self.cell_size), 2)
            
            # horizontal
            y = self.margin + i * self.cell_size
            pygame.draw.line(self.screen, LINE_COLOR, 
                           (self.margin, y), 
                           (self.margin + (self.board_size - 1) * self.cell_size, y), 2)
        
        # starpoints
        if self.board_size == 15:
            star_points = [(3, 3), (3, 11), (11, 3), (11, 11), (7, 7)]
            for row, col in star_points:
                px, py = self.get_pixelcoords(row, col)
                # anti-aliasing for star points
                pygame.gfxdraw.aacircle(self.screen, px, py, 4, LINE_COLOR)
                pygame.gfxdraw.filled_circle(self.screen, px, py, 4, LINE_COLOR)
    
    def draw_stone(self, row, col, player, highlight=False):
        """stone at the given board position"""
        x, y = self.get_pixelcoords(row, col)
        radius = self.cell_size // 2 - 2
        
        color = BLACK if player == PLAYER_BLACK else WHITE
        
        # anti-aliasing for smoother stones
        pygame.gfxdraw.aacircle(self.screen, x, y, radius, color)
        pygame.gfxdraw.filled_circle(self.screen, x, y, radius, color)
        
        # outline for white stones
        if player == PLAYER_WHITE:
            pygame.gfxdraw.aacircle(self.screen, x, y, radius, LINE_COLOR)
        
        # highlight > last move
        if highlight:
            pygame.gfxdraw.aacircle(self.screen, x, y, radius + 2, HIGHLIGHT_COLOR)
            pygame.gfxdraw.aacircle(self.screen, x, y, radius + 3, HIGHLIGHT_COLOR)
    
    def draw_hover(self, row, col):
        """hover indicator at valid positions"""
        if row is None or col is None:
            return
            
        if self.is_valid(row, col):
            x, y = self.get_pixelcoords(row, col)
            radius = self.cell_size // 3
            
            # anti-aliasing for hover circle
            s = pygame.Surface((radius * 2 + 2, radius * 2 + 2), pygame.SRCALPHA)
            center = radius + 1
            pygame.gfxdraw.aacircle(s, center, center, radius, (255, 0, 0, 150))
            pygame.gfxdraw.filled_circle(s, center, center, radius, HOVER_COLOR)
            self.screen.blit(s, (x - center, y - center))

    def is_valid(self, row, col):
        """if a move is valid > in bounds and empty"""
        return (0 <= row < self.board_size and 0 <= col < self.board_size) and \
               position_is_empty(self.game, row, col)
    
    def draw_stones(self):
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.game[row, col] != 0:
                    highlight = (self.last_move == (row, col))
                    self.draw_stone(row, col, int(self.game[row, col]), highlight)
    
    def draw_info(self):
        info_rect = pygame.Rect(0, self.window_size, self.window_size, INFO_HEIGHT)
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
        text_rect = text_surface.get_rect(center=(self.window_size // 2, self.window_size + INFO_HEIGHT // 2))
        self.screen.blit(text_surface, text_rect)
        
        # press any key on game end
        if self.game_over:
            restart_text = FONT_SMALL.render("Drücke eine beliebige Taste für Neustart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(self.window_size // 2, self.window_size + INFO_HEIGHT - 15))
            self.screen.blit(restart_text, restart_rect)
    
    def make_move_and_check(self, row, col):
        """make move and check win condition > removes redundancy"""
        make_move(self.game, row, col, self.current_player)
        self.last_move = (row, col)
        self.states.append(self.game.copy())
        
        # won? 
        winner = get_winner(self.game, WIN_CONDITION)
        if winner in (PLAYER_BLACK, PLAYER_WHITE):
            self.game_over = True
            self.winner = winner
            self.export_game_states()  # export on game end
        elif winner == -1:  # draw
            self.game_over = True
            self.winner = None
            self.export_game_states()  # export on game end
        else:
            # switch player: 1 -> 2, 2 -> 1
            self.current_player = (self.current_player % 2) + 1
    
    def process_click(self, pos):
        """mouse click for human player move"""
        if self.game_over:
            return
            
        row, col = self.pixel_to_board_pos(pos)
        
        if row is None or col is None:
            return
            
        if self.is_valid(row, col):
            self.make_move_and_check(row, col)
    
    def restart_game(self):
        """reset > initial state"""
        self.game = create_board(self.board_size) 
        self.current_player = PLAYER_BLACK
        self.game_over = False
        self.winner = None
        self.last_move = None
        self.states = []
    
    def process_bot_move(self):
        """move for the bot player (Player 1 = Black)"""
        if self.game_over or self.current_player != PLAYER_BLACK:
            return

        if self.bot_mode == "ai":
            # panic if ai mode is selected
            raise NotImplementedError("AI bot not implemented yet!")
        else:
            # generate_next_move_random > call make_move
            row, col = generate_next_move_random(self.game, self.current_player)
        
        # just update state / check win
        self.last_move = (row, col)
        self.states.append(self.game.copy())
        
        # won? 
        winner = get_winner(self.game, WIN_CONDITION)
        if winner in (PLAYER_BLACK, PLAYER_WHITE):
            self.game_over = True
            self.winner = winner
            self.export_game_states()  # export on game end
        elif winner == -1:  # draw
            self.game_over = True
            self.winner = None
            self.export_game_states()  # export on game end
        else:
            # switch player: 1 -> 2, 2 -> 1
            self.current_player = (self.current_player % 2) + 1
    
    def export_game_states(self):
        """export game states as numpy array > makes data generation easier"""
        if len(self.states) == 0:
            print("No moves to export.")
            return
        
        # create output directory
        output_dir = Path("game_data")
        output_dir.mkdir(exist_ok=True)
        
        # save as numpy array
        game_array = np.stack(self.states)
        filename = output_dir / f"game_{len(list(output_dir.glob('game_*.npy')))}.npy"
        np.save(filename, game_array)
        print(f"Game exported to {filename} with {len(self.states)} moves.")
    
    def run(self):
        running = True
        
        while running:
            pos = pygame.mouse.get_pos()
            hover_row, hover_col = self.pixel_to_board_pos(pos)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # human player move
                    if self.two_player:
                        # both players are human
                        self.process_click(pos)
                    elif self.current_player == PLAYER_WHITE:
                        # only white is human
                        self.process_click(pos)
                elif event.type == pygame.KEYDOWN:
                    if self.game_over:
                        # press any key on game end
                        self.restart_game()
                    elif event.key == pygame.K_ESCAPE:
                        running = False
            
            self.draw_board()
            self.draw_stones()
            
            # bot makes move if it's their turn
            if not self.game_over and not self.two_player and self.current_player == PLAYER_BLACK:
                self.process_bot_move()
                
            # show hover indicator for human player
            if not self.game_over:
                if self.two_player or self.current_player == PLAYER_WHITE:
                    self.draw_hover(hover_row, hover_col)
            
            self.draw_info()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()


def parse_args():
    """cli"""
    parser = argparse.ArgumentParser(description="configurable settings")
    parser.add_argument(
        "--size",
        type=int,
        default=15,
        help="Board size (default: 15)"
    )
    parser.add_argument(
        "--bot",
        type=str,
        choices=["random", "ai", "none"],
        default="random",
        help="Bot mode: random, ai > not implemented / or none for 2-player > default: random"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    
    # check if ai mode is selected
    if args.bot == "ai":
        print("ERROR!!! AI > not implemented")
        sys.exit(1)
    
    two_player_mode = (args.bot == "none")
    
    game = GomokuGame(
        board_size=args.size,
        bot_mode=args.bot,
        two_player=two_player_mode
    )
    game.run()