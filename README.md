# Gomoku VLM Training Project

## Installation
```bash
pip install -r requirements.txt
```

## Running the Game
```bash
# Standard (15x15, bot vs. human)
python pygame_gomoku.py

# custom board size
python pygame_gomoku.py --size 9

# 2-Player mode
python pygame_gomoku.py --bot none
```

## PyGame Controls

- **Mouse click**: Place a stone (as white player)
- **Any key**: Restart game (after game ends)
- **ESC**: Quit game

**Note**: Game states > automatically exported as .npy files to `game_data/` folder > when the game ends.