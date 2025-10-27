# Gomoku VLM Training Project

Vision Language Model für Gomoku

## ToDo  
1. Create a strategy game with a grid-based layout and round-based actions
2. Create a bot (algorithmic, not AI) that can play the game reasonably well  
3. Let a VLM (and/or humans) play the game against the bot to generate game log data
4. Generate training/eval/test data for a vision language model from the game log data
5. Evaluate a VLM regarding its performance on the test data
6. Finetune a VLM on the training data
7. Analyze the differences in evaluation pre-/post training
8. Write down your personal learning experience from lecture and practical training

## Projektstruktur

```
projekt/
├── game_logic.py          # Spiellogik - BRAUCHT is_valid()! ?!
├── renderer.py            # Bildgenerierung 
├── pygame_gomoku.py       # GUI
├── bot.py                 # Bot
├── game_runner.py         # Spiel-Ausführung und Logging
├── data.py                # VLM Dataset 
└── evaluate.py            # VLM Evaluation 
```

für game_logic.py? sonst kann mein "test" bot.py und pygame_gomoku.py nicht laufen ?! 

def is_valid(board: npt.NDArray, row: int, col: int) -> bool:
    if not (0 <= row < board.shape[0] and 0 <= col < board.shape[1]):
        return False
    return position_is_empty(board, row, col)


## Installation

```bash
pip install numpy pillow pygame
```

## Nutzung

### 1. Spiel (Aufgabe 1-3)

python pygame_gomoku.py

Steuerung:
- Maus: Stein setzen
- R: Neues Spiel
- ESC: Beenden

bot > hab mich dran versucht 
python game_runner.py ? 

### 3. VLM Dataset generieren (Aufgabe 4)
python data.py

### 4. VLM evaluieren (Aufgabe 5)
Pre-Training Evaluation:
TODO: VLM Predictions generieren

### 5. VLM Finetuning (Aufgabe 6)
TODO: Mit VLM Framework

### 6. Post-Training Evaluation (Aufgabe 7)
+ VLM Dataset Format

