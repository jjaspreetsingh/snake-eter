#!/usr/bin/env python3
"""
Lightweight yet modern terminal Snake game built with curses.

The design keeps the classic mechanics while layering in:
  • difficulty presets
  • bonus fruit with temporary speed boost
  • adaptive obstacle growth as the score climbs
  • pause/resume and persistent high-score tracking
"""

from __future__ import annotations

import curses
import random
import time
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Deque, Optional, Tuple


SCORE_FILE = Path.home() / ".snake_eter_highscore"


@dataclass(frozen=True)
class Difficulty:
    name: str
    speed_ms: int       # Initial tick speed in ms
    base_obstacles: int # Obstacles spawned on reset


DIFFICULTIES = [
    Difficulty("Calm", 140, 1),
    Difficulty("Classic", 100, 3),
    Difficulty("Turbo", 70, 5),
]


Direction = Tuple[int, int]
UP: Direction = (-1, 0)
DOWN: Direction = (1, 0)
LEFT: Direction = (0, -1)
RIGHT: Direction = (0, 1)
OPPOSITES = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}


class SnakeGame:
    def __init__(self, stdscr: "curses._CursesWindow") -> None:
        self.stdscr = stdscr
        self.sh, self.sw = self.stdscr.getmaxyx()
        self.play_top = 3
        self.play_left = 2
        self.play_height = self.sh - 5
        self.play_width = self.sw - 4

        self.difficulty_index = 1
        self.high_score = self._load_high_score()
        self.score = 0
        self.level = 1

        self.snake: Deque[Tuple[int, int]] = deque()
        self.direction: Direction = RIGHT
        self.food: Tuple[int, int] = (0, 0)
        self.bonus_food: Optional[Tuple[int, int]] = None
        self.bonus_timer = 0
        self.obstacles: set[Tuple[int, int]] = set()
        self.pending_growth = 0
        self.speed_ms = DIFFICULTIES[self.difficulty_index].speed_ms

    # ------------------------------------------------------------------ menus
    def run(self) -> None:
        curses.curs_set(0)
        self.stdscr.keypad(True)
        while True:
            choice = self._main_menu()
            if choice == "start":
                self._play_loop()
            elif choice == "difficulty":
                self._pick_difficulty()
            elif choice == "quit":
                break

    def _main_menu(self) -> str:
        options = ["Start game", "Difficulty", "Quit"]
        selected = 0
        while True:
            self.stdscr.clear()
            title = "SNAKE ETER"
            subtitle = "simple moves, advanced rhythm"
            self.stdscr.addstr(2, self.sw // 2 - len(title) // 2, title, curses.A_BOLD)
            self.stdscr.addstr(3, self.sw // 2 - len(subtitle) // 2, subtitle, curses.A_DIM)
            stats = f"High score: {self.high_score}  |  Current: {DIFFICULTIES[self.difficulty_index].name}"
            self.stdscr.addstr(5, self.sw // 2 - len(stats) // 2, stats)

            for idx, label in enumerate(options):
                prefix = "➤ " if idx == selected else "  "
                attr = curses.A_REVERSE if idx == selected else curses.A_NORMAL
                text = prefix + (label if idx != 1 else f"{label}: {DIFFICULTIES[self.difficulty_index].name}")
                self.stdscr.addstr(8 + idx * 2, self.sw // 2 - len(text) // 2, text, attr)

            self.stdscr.refresh()
            key = self.stdscr.getch()
            if key in (curses.KEY_UP, ord("k")):
                selected = (selected - 1) % len(options)
            elif key in (curses.KEY_DOWN, ord("j")):
                selected = (selected + 1) % len(options)
            elif key in (curses.KEY_ENTER, 10, 13):
                return ["start", "difficulty", "quit"][selected]

    def _pick_difficulty(self) -> None:
        idx = self.difficulty_index
        while True:
            self.stdscr.clear()
            self.stdscr.addstr(4, self.sw // 2 - 7, "Select speed", curses.A_BOLD)
            for i, diff in enumerate(DIFFICULTIES):
                marker = "•" if i == idx else " "
                text = f"{marker} {diff.name:<8} | tick {diff.speed_ms}ms | base obstacles {diff.base_obstacles}"
                attr = curses.A_REVERSE if i == idx else curses.A_NORMAL
                self.stdscr.addstr(7 + i * 2, self.sw // 2 - len(text) // 2, text, attr)
            self.stdscr.addstr(self.sh - 3, self.sw // 2 - 18, "Enter to lock, Q to cancel", curses.A_DIM)
            self.stdscr.refresh()

            key = self.stdscr.getch()
            if key in (curses.KEY_UP, ord("k")):
                idx = (idx - 1) % len(DIFFICULTIES)
            elif key in (curses.KEY_DOWN, ord("j")):
                idx = (idx + 1) % len(DIFFICULTIES)
            elif key in (curses.KEY_ENTER, 10, 13):
                self.difficulty_index = idx
                return
            elif key in (ord("q"), ord("Q"), 27):
                return

    # ------------------------------------------------------------- game setup
    def _reset_round(self) -> None:
        self.score = 0
        self.level = 1
        self.pending_growth = 0
        self.direction = RIGHT
        diff = DIFFICULTIES[self.difficulty_index]
        self.speed_ms = diff.speed_ms

        center_y = self.play_top + self.play_height // 2
        center_x = self.play_left + self.play_width // 2
        self.snake = deque(
            [
                (center_y, center_x + 1),
                (center_y, center_x),
                (center_y, center_x - 1),
            ]
        )

        self.obstacles = set()
        self.food = (-1, -1)
        for _ in range(diff.base_obstacles):
            self.obstacles.add(self._random_free_cell())

        self.food = self._random_free_cell()
        self.bonus_food = None
        self.bonus_timer = 0

    def _random_free_cell(self) -> Tuple[int, int]:
        while True:
            y = random.randint(self.play_top + 1, self.play_top + self.play_height - 2)
            x = random.randint(self.play_left + 1, self.play_left + self.play_width - 2)
            cell = (y, x)
            if cell in self.snake or cell in self.obstacles or cell == self.food or cell == self.bonus_food:
                continue
            return cell

    # ----------------------------------------------------------------- render
    def _draw_world(self) -> None:
        self.stdscr.erase()
        # arena border
        for x in range(self.play_left, self.play_left + self.play_width):
            self.stdscr.addch(self.play_top, x, "-")
            self.stdscr.addch(self.play_top + self.play_height - 1, x, "-")
        for y in range(self.play_top, self.play_top + self.play_height):
            self.stdscr.addch(y, self.play_left, "|")
            self.stdscr.addch(y, self.play_left + self.play_width - 1, "|")
        self.stdscr.addch(self.play_top, self.play_left, "+")
        self.stdscr.addch(self.play_top, self.play_left + self.play_width - 1, "+")
        self.stdscr.addch(self.play_top + self.play_height - 1, self.play_left, "+")
        self.stdscr.addch(self.play_top + self.play_height - 1, self.play_left + self.play_width - 1, "+")

        # snake
        for idx, (y, x) in enumerate(self.snake):
            char = "@"
            attr = curses.A_BOLD
            if idx != 0:
                char = "o"
                attr = curses.A_DIM
            self.stdscr.addch(y, x, char, attr)

        # food & bonus
        fy, fx = self.food
        self.stdscr.addch(fy, fx, "*", curses.A_BOLD)
        if self.bonus_food:
            by, bx = self.bonus_food
            self.stdscr.addch(by, bx, "$", curses.A_BLINK)

        # obstacles
        for y, x in self.obstacles:
            self.stdscr.addch(y, x, "#")

        self._draw_hud()
        self.stdscr.noutrefresh()
        curses.doupdate()

    def _draw_hud(self) -> None:
        diff = DIFFICULTIES[self.difficulty_index]
        info = f"Score {self.score}   Level {self.level}   High {self.high_score}   Mode {diff.name}"
        self.stdscr.addstr(1, self.sw // 2 - len(info) // 2, info)
        controls = "↑↓←→ move | P pause | Q quit"
        self.stdscr.addstr(self.sh - 2, self.sw // 2 - len(controls) // 2, controls, curses.A_DIM)
        if self.bonus_food:
            bonus_text = f"Bonus fruit fades in {self.bonus_timer} ticks"
            self.stdscr.addstr(2, self.sw // 2 - len(bonus_text) // 2, bonus_text, curses.A_DIM)

    # --------------------------------------------------------------- gameplay
    def _play_loop(self) -> None:
        self._reset_round()
        self.stdscr.nodelay(True)
        while True:
            self._draw_world()
            self.stdscr.timeout(self.speed_ms)
            key = self.stdscr.getch()
            if key in (curses.KEY_UP, ord("w")):
                self._maybe_turn(UP)
            elif key in (curses.KEY_DOWN, ord("s")):
                self._maybe_turn(DOWN)
            elif key in (curses.KEY_LEFT, ord("a")):
                self._maybe_turn(LEFT)
            elif key in (curses.KEY_RIGHT, ord("d")):
                self._maybe_turn(RIGHT)
            elif key in (ord("p"), ord("P")):
                if not self._pause_screen():
                    self._save_high_score()
                    return
            elif key in (ord("q"), ord("Q")):
                self._save_high_score()
                return

            if not self._advance_snake():
                wants_retry = self._game_over_screen()
                self._save_high_score()
                if wants_retry:
                    self._reset_round()
                    continue
                return

    def _maybe_turn(self, new_dir: Direction) -> None:
        if new_dir != OPPOSITES[self.direction]:
            self.direction = new_dir

    def _advance_snake(self) -> bool:
        head_y, head_x = self.snake[0]
        delta_y, delta_x = self.direction
        new_head = (head_y + delta_y, head_x + delta_x)

        if self._hits_wall(new_head) or new_head in self.snake or new_head in self.obstacles:
            return False

        self.snake.appendleft(new_head)
        if self.pending_growth > 0:
            self.pending_growth -= 1
        else:
            self.snake.pop()

        ate_bonus = self.bonus_food and new_head == self.bonus_food
        if new_head == self.food or ate_bonus:
            gained = 15 if ate_bonus else 10
            self.score += gained
            self.pending_growth += 1
            self.food = self._random_free_cell()
            if ate_bonus:
                self.bonus_food = None
                self.speed_ms = max(40, self.speed_ms - 5)
            else:
                self._maybe_spawn_bonus()
            self._maybe_level_up()

        if self.bonus_food:
            self.bonus_timer -= 1
            if self.bonus_timer <= 0:
                self.bonus_food = None

        if self.score > self.high_score:
            self.high_score = self.score
        return True

    def _hits_wall(self, position: Tuple[int, int]) -> bool:
        y, x = position
        return (
            y <= self.play_top
            or y >= self.play_top + self.play_height - 1
            or x <= self.play_left
            or x >= self.play_left + self.play_width - 1
        )

    def _maybe_spawn_bonus(self) -> None:
        if self.bonus_food is None and random.random() < 0.25:
            self.bonus_food = self._random_free_cell()
            self.bonus_timer = 35

    def _maybe_level_up(self) -> None:
        target = 50 * self.level
        if self.score >= target:
            self.level += 1
            self.speed_ms = max(30, self.speed_ms - 7)
            self.obstacles.add(self._random_free_cell())

    def _pause_screen(self) -> bool:
        self.stdscr.nodelay(False)
        self.stdscr.addstr(self.sh // 2, self.sw // 2 - 8, "Paused – press P", curses.A_BOLD)
        self.stdscr.refresh()
        while True:
            key = self.stdscr.getch()
            if key in (ord("p"), ord("P")):
                self.stdscr.nodelay(True)
                return True
            if key in (ord("q"), ord("Q")):
                self.stdscr.nodelay(True)
                return False

    # ------------------------------------------------------------ end screens
    def _game_over_screen(self) -> bool:
        self.stdscr.nodelay(False)
        message = "GAME OVER"
        summary = f"Score {self.score} | Level {self.level}"
        prompt = "Enter to retry  •  Q to menu"
        self.stdscr.addstr(self.sh // 2 - 1, self.sw // 2 - len(message) // 2, message, curses.A_BOLD)
        self.stdscr.addstr(self.sh // 2, self.sw // 2 - len(summary) // 2, summary)
        self.stdscr.addstr(self.sh // 2 + 2, self.sw // 2 - len(prompt) // 2, prompt, curses.A_DIM)
        self.stdscr.refresh()
        while True:
            key = self.stdscr.getch()
            if key in (curses.KEY_ENTER, 10, 13):
                self.stdscr.nodelay(True)
                return True
            if key in (ord("q"), ord("Q")):
                self.stdscr.nodelay(True)
                return False

    # --------------------------------------------------------------- storage
    def _load_high_score(self) -> int:
        try:
            return int(SCORE_FILE.read_text().strip())
        except Exception:
            return 0

    def _save_high_score(self) -> None:
        SCORE_FILE.write_text(str(max(self.high_score, 0)))


def main(stdscr: "curses._CursesWindow") -> None:
    game = SnakeGame(stdscr)
    game.run()


if __name__ == "__main__":
    curses.wrapper(main)
