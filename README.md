# Word Mosaic

A single-player word strategy game built with Python. Word Mosaic challenges players to build a connected network of words on a grid using a limited set of letters.

![Word Mosaic Game](https://github.com/caninecrew/word-mosaic)

## 🎮 Gameplay Overview

In Word Mosaic, you'll:
- Place letters on a 15x15 grid to form valid English words
- Start with 20 randomized letters based on standard frequency distributions
- Build an interconnected network of words, with each new word connecting to existing ones
- Earn points based on letter values, word length, and strategic placement
- Use power-ups and special abilities to maximize your score

## 🚀 Features

- **Strategic Word Building**: Create a mosaic of interconnected words
- **Balanced Scoring System**: Points for letters, word length, and connections
- **Special Tiles**: Discover multiplier tiles that boost your score
- **Power-Ups**: Use abilities like shuffle and hints to overcome challenges
- **End-Game Bonuses**: Earn additional points for coverage and complexity

## 📋 Game Rules

1. **Setup**: Start with 20 letters in your bank and an empty 15x15 grid
2. **First Word**: Your first word must cross the center tile
3. **Word Placement**: All words must read left-to-right or top-to-bottom
4. **Connections**: Every new word must connect to at least one existing word
5. **Valid Words**: All created words must be valid English words
6. **Letter Replenishment**: Gain new letters after successful placement
7. **Game End**: The game ends when no more valid placements are possible

## 🔧 Installation

```bash
# Clone the repository
git clone https://github.com/caninecrew/word-mosaic.git
cd word-mosaic

# Install dependencies
pip install -r requirements.txt

# Run the game
python main.py
```

## 🧠 Scoring System

- **Letter Values**: Each letter has a base point value (A=1, B=3, etc.)
- **Word Length Bonuses**: 
  - 5-letter words: 1.5× multiplier
  - 6-letter words: 2× multiplier
  - 7+ letter words: 3× multiplier
- **Connection Bonuses**: +2 points for each intersection with existing words
- **Special Tiles**: Double letter, triple letter, double word, and triple word multipliers
- **End-Game Bonuses**: Based on grid coverage and word complexity

## 💻 Technical Requirements

- Python 3.6+
- GUI framework (Tkinter/PyQt/Kivy)
- No internet connection required to play

## 🔜 Roadmap

- Dictionary integration for word validation
- Save/load functionality
- Achievements system
- Time-based challenge mode
- Custom theme options
- AI opponent for competitive play

## 📄 License

[MIT License](LICENSE)

## 👏 Acknowledgements

- Inspired by classic word games like Scrabble and Bananagrams
- Dictionary provided by [Open Source Dictionary Project]