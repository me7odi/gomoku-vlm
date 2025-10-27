# Gomoku VLM Training Project

## Installation

```bash
pip install -r requirements.txt
```

**requirements.txt:**
```
numpy
pygame
Pillow
```

## Running the Game

```bash
python pygame_gomoku.py
```

## Controls

- **Mouse click**: Place a stone
- **R**: Restart game
- **E**: Export game states as .npy file
- **ESC**: Quit game

## Features

- Two-player game (Player 1 is human, Player 2 can be a random bot)
- Saves every game state after each move
- Export all game states for analysis or dataset generation
