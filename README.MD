# 🐍 Snake Eter

Terminal-first Snake written with Python + `curses`. The codebase stays compact,
yet the gameplay layers in just enough systems to feel modern—dynamic
obstacles, bonus fruit, adaptive speed, pause/resume, and persistent high
scores.

## 🎮 Feature Highlights

- **Three handcrafted difficulties** (Calm, Classic, Turbo) that control base
  speed + obstacle count.
- **Adaptive arena**: every 50 points the game injects a fresh obstacle and
  briefly bumps the tempo.
- **Bonus fruit**: `$` pieces appear randomly, rewarding +15 points and a
  subtle speed boost if eaten before they fade.
- **Pause-anytime loop**: hit `P` to freeze the board, resume or exit without
  losing progress.
- **Persistent highscores** saved at `~/.snake_eter_highscore`.

## 🚀 Installation

### Requirements

- Python 3.8+
- A Unix-like terminal (Linux, macOS, WSL). Windows terminal users should run
  it via WSL to get a working `curses` stack.

### Quick Start

```bash
git clone https://github.com/jjaspreetsingh/snake-eter.git
cd snake-eter
chmod +x snake_game.py
./snake_game.py          # or: python3 snake_game.py
```

### Optional: install globally

```bash
mkdir -p ~/.local/bin
ln -s "$(pwd)/snake_game.py" ~/.local/bin/snake-eter
export PATH="$HOME/.local/bin:$PATH"
snake-eter
```

## 🕹️ How to Play

- **Menus**: use ↑/↓ (or `j`/`k`) and press Enter.
- **In-game controls**
  - `↑ ↓ ← →` or `WASD` to steer
  - `P` pauses/resumes
  - `Q` leaves the current round/menu
- **Goals**
  1. Eat `*` food to grow + score 10 points.
  2. Snag `$` bonus fruit before it fades to gain 15 points and higher tempo.
  3. Avoid walls (`|`, `-`, `+`), your tail, and `#` obstacles.

## 🧠 Mechanics

| System        | Description                                                      |
|---------------|------------------------------------------------------------------|
| Difficulty    | Sets base tick speed plus starting obstacle count.               |
| Leveling      | Every 50 pts adds an obstacle + trims tick speed (to 30 ms min). |
| Bonus Fruit   | 25 % chance after eating normal food, lasts ~35 ticks.           |
| Persistence   | Highest score is written to `~/.snake_eter_highscore`.           |

## 🐛 Troubleshooting

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError: _curses` | Install via your package manager: `sudo apt install python3-curses`. |
| Terminal too small | Ensure at least 30×80 characters; resize and restart. |
| Unicode glitches | Switch to a UTF‑8 capable emulator (GNOME Terminal, iTerm2, Windows Terminal + WSL). |

## 🧩 Project Layout

```
snake-eter/
├── snake_game.py   # the entire game loop + menus
└── README.MD       # this guide
```

## 🤝 Contributing

Ideas welcome! Feel free to open PRs for new board themes, better input
handling, multiplayer experiments, etc.

---

Enjoy the grind and may your tail stay clear! 🎉

