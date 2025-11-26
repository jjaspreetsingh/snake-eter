# 🐍 Advanced Snake Game

A feature-rich, terminal-based Snake game built with Python and curses library.

## 🎮 Features

### Core Gameplay
- **Classic Snake mechanics** with modern enhancements
- **Multiple difficulty levels** (Easy, Medium, Hard)
- **Level progression** - game gets harder as you advance
- **High score tracking** across sessions

### Advanced Features
- **Powerup system**: Speed boost, invincibility, double points
- **Obstacle avoidance** - randomly placed barriers
- **Colorful UI** with Unicode symbols and proper styling
- **Pause functionality** - press 'P' to pause/resume

### Visual Enhancements
- **Color-coded elements**: Snake, food, obstacles, powerups
- **Unicode symbols**: Snake head (●), body (○), food (🍎), obstacles (■)
- **Powerup icons**: ⚡ (speed), 🛡️ (invincible), 2️⃣ (double points)
- **Professional menu system** with navigation

## 🚀 Installation & Setup

### Prerequisites
- Python 3.6+
- Linux/macOS terminal (Windows requires additional setup)

### Quick Start
```bash
# Clone the repository
git clone https://github.com/jjaspreetsingh/snake-eter.git
cd snake-eter

# Make the game executable
chmod +x snake_game.py

# Run the game
./snake_game.py
```

### System-wide Installation
```bash
# Create a symbolic link in your PATH
mkdir -p ~/.local/bin
ln -s $(pwd)/snake_game.py ~/.local/bin/snake

# Add to PATH if not already (add to ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.local/bin:$PATH"

# Now run from anywhere:
snake
```

## 🎯 How to Play

### Controls
- **Arrow Keys** (↑↓←→): Move the snake
- **P**: Pause/Resume the game
- **Q**: Quit to main menu
- **Enter/Return**: Select menu options

### Game Rules
1. **Eat food** (🍎) to grow and earn points
2. **Avoid collisions** with walls, yourself, and obstacles (■)
3. **Collect powerups** for temporary advantages
4. **Level up** every 10 points - increases difficulty

### Powerups
- **⚡ Speed Boost**: Temporarily increases snake speed
- **🛡️ Invincibility**: Immune to collisions for 10 seconds
- **2️⃣ Double Points**: Doubles points from food + bonus points

## 🏆 Difficulty Levels

| Level | Speed | Obstacles | Description |
|-------|-------|-----------|-------------|
| Easy | 150ms | 3 | Slower pace, fewer obstacles |
| Medium | 100ms | 5 | Balanced challenge |
| Hard | 50ms | 8 | Fast-paced, many obstacles |

## 🛠️ Technical Details

### Dependencies
- **Python 3.6+**
- **curses library** (included in Python standard library)
- **Terminal with Unicode support**

### File Structure
```
snake-eter/
├── snake_game.py    # Main game executable
├── README.MD        # This documentation
└── (future assets)
```

### Compatibility
- ✅ **Linux**: Fully supported
- ✅ **macOS**: Fully supported
- ⚠️ **Windows**: Requires Windows Subsystem for Linux (WSL) or additional setup

## 🐛 Troubleshooting

### Common Issues

**Game doesn't start:**
```bash
# Ensure Python 3 is installed
python3 --version

# Make script executable
chmod +x snake_game.py

# Run with Python explicitly if needed
python3 snake_game.py
```

**Unicode characters not displaying:**
- Ensure your terminal supports UTF-8
- Try a modern terminal like GNOME Terminal, iTerm2, or Windows Terminal

**Colors not working:**
- Some terminals may not support curses colors
- Game will still work in monochrome mode

## 🤝 Contributing

Feel free to contribute to this project! Here are some areas for improvement:
- Additional powerups
- Sound effects
- Save game functionality
- Leaderboard system
- Custom themes

## 📄 License

This project is open source. Feel free to modify and distribute.

## 👨‍💻 Author

**Jaspreet Singh** - [GitHub](https://github.com/jjaspreetsingh)

---

**Enjoy the game! 🎉**

