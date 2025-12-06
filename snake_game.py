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
from typing import Deque, Optional, Tuple, List


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
        # Input buffering: queue of desired directions
        self.move_queue: Deque[Direction] = deque()
        
        self.food: Tuple[int, int] = (0, 0)
        self.bonus_food: Optional[Tuple[int, int]] = None
        self.bonus_timer = 0
        self.obstacles: set[Tuple[int, int]] = set()
        self.pending_growth = 0
        self.speed_ms = DIFFICULTIES[self.difficulty_index].speed_ms

        # Color pairs identifiers
        self.COLOR_BORDER = 1
        self.COLOR_SNAKE = 2
        self.COLOR_FOOD = 3
        self.COLOR_BONUS = 4
        self.COLOR_OBSTACLE = 5
        self.COLOR_TEXT = 6

    # ------------------------------------------------------------------ menus
    def run(self) -> None:
        curses.curs_set(0)
        self.stdscr.keypad(True)
        self._init_colors()
        
        while True:
            choice = self._main_menu()
            if choice == "start":
                self._play_loop()
            elif choice == "difficulty":
                self._pick_difficulty()
            elif choice == "quit":
                break

    def _init_colors(self) -> None:
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            try:
                curses.init_pair(self.COLOR_BORDER, curses.COLOR_WHITE, -1)
                curses.init_pair(self.COLOR_SNAKE, curses.COLOR_GREEN, -1)
                curses.init_pair(self.COLOR_FOOD, curses.COLOR_RED, -1)
                curses.init_pair(self.COLOR_BONUS, curses.COLOR_CYAN, -1)
                curses.init_pair(self.COLOR_OBSTACLE, curses.COLOR_WHITE, -1) # or grey if available
                curses.init_pair(self.COLOR_TEXT, curses.COLOR_YELLOW, -1)
            except Exception:
                pass # Fallback to no colors if initiation fails

    def _main_menu(self) -> str:
        options = ["Start game", "Difficulty", "Quit"]
        selected = 0
        while True:
            self.stdscr.clear()
            title = "SNAKE ETER"
            subtitle = "simple moves, advanced rhythm"
            
            c_title = curses.color_pair(self.COLOR_SNAKE) | curses.A_BOLD
            self.stdscr.addstr(2, self.sw // 2 - len(title) // 2, title, c_title)
            self.stdscr.addstr(3, self.sw // 2 - len(subtitle) // 2, subtitle, curses.A_DIM)
            
            stats = f"High score: {self.high_score}  |  Current: {DIFFICULTIES[self.difficulty_index].name}"
            self.stdscr.addstr(5, self.sw // 2 - len(stats) // 2, stats, curses.color_pair(self.COLOR_TEXT))

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
        self.move_queue.clear()
        
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
        
        # colors
        c_border = curses.color_pair(self.COLOR_BORDER)
        c_snake = curses.color_pair(self.COLOR_SNAKE)
        c_food = curses.color_pair(self.COLOR_FOOD)
        c_bonus = curses.color_pair(self.COLOR_BONUS)
        c_obstacle = curses.color_pair(self.COLOR_OBSTACLE)

        # arena border
        for x in range(self.play_left, self.play_left + self.play_width):
            self.stdscr.addch(self.play_top, x, "-", c_border)
            self.stdscr.addch(self.play_top + self.play_height - 1, x, "-", c_border)
        for y in range(self.play_top, self.play_top + self.play_height):
            self.stdscr.addch(y, self.play_left, "|", c_border)
            self.stdscr.addch(y, self.play_left + self.play_width - 1, "|", c_border)
        self.stdscr.addch(self.play_top, self.play_left, "+", c_border)
        self.stdscr.addch(self.play_top, self.play_left + self.play_width - 1, "+", c_border)
        self.stdscr.addch(self.play_top + self.play_height - 1, self.play_left, "+", c_border)
        self.stdscr.addch(self.play_top + self.play_height - 1, self.play_left + self.play_width - 1, "+", c_border)

        # snake
        for idx, (y, x) in enumerate(self.snake):
            char = "@"
            attr = c_snake | curses.A_BOLD
            if idx != 0:
                char = "o"
                attr = c_snake # Body is just green
            self.stdscr.addch(y, x, char, attr)

        # food & bonus
        fy, fx = self.food
        self.stdscr.addch(fy, fx, "*", c_food | curses.A_BOLD)
        if self.bonus_food:
            by, bx = self.bonus_food
            self.stdscr.addch(by, bx, "$", c_bonus | curses.A_BLINK | curses.A_BOLD)

        # obstacles
        for y, x in self.obstacles:
            self.stdscr.addch(y, x, "#", c_obstacle)

        self._draw_hud()
        self.stdscr.noutrefresh()
        curses.doupdate()

    def _draw_hud(self) -> None:
        diff = DIFFICULTIES[self.difficulty_index]
        info = f"Score {self.score}   Level {self.level}   High {self.high_score}   Mode {diff.name}"
        self.stdscr.addstr(1, self.sw // 2 - len(info) // 2, info, curses.color_pair(self.COLOR_TEXT) | curses.A_BOLD)
        controls = "↑↓←→ move | P pause | Q quit"
        self.stdscr.addstr(self.sh - 2, self.sw // 2 - len(controls) // 2, controls, curses.A_DIM)
        if self.bonus_food:
            bonus_text = f"Bonus fruit fades in {self.bonus_timer} ticks"
            self.stdscr.addstr(2, self.sw // 2 - len(bonus_text) // 2, bonus_text, curses.color_pair(self.COLOR_BONUS))

    # --------------------------------------------------------------- gameplay
    def _play_loop(self) -> None:
        self._reset_round()
        self.stdscr.timeout(self.speed_ms)
        
        while True:
            self._draw_world()
            
            # Input handling with buffering
            # We drain the event queue to prevent lag but capture up to 2 buffered moves
            start_time = time.time()
            
            # Simple loop to consume keys
            key = self.stdscr.getch()
            if key != -1:
                self._handle_input(key)
                
            # Allow for multiple keys in one frame if the system is fast enough? 
            # Actually standard curses getch returns -1 if no input.
            # To be safe, we just process one key per tick or check if more are available?
            # A simple approach for snake is: read one key. If we want smooth buffering we might want to read all.
            # Let's read all pending keys
            while True:
                try:
                    # Non-blocking check for more keys?
                    # getch is already non-blocking due to nodelay/timeout
                    # We can set nodelay true temporarily
                    self.stdscr.nodelay(True)
                    next_key = self.stdscr.getch()
                    if next_key == -1:
                        break
                    self._handle_input(next_key)
                except Exception:
                    break
            
            # Restore timeout behavior
            self.stdscr.nodelay(False)
            self.stdscr.timeout(self.speed_ms)

            # Apply one move from queue
            if self.move_queue:
                next_dir = self.move_queue.popleft()
                # Double check validity against CURRENT direction (in case queue had multiples)
                # But actually, we want to check against the direction we *will* be facing 
                # after the previous queued move. 
                # Since we only execute one move per tick, 'self.direction' IS the direction 
                # from the previous tick. So checking against it is correct for the first item.
                # However, if we simply set self.direction, the _advance_snake uses it.
                if next_dir != OPPOSITES[self.direction] and next_dir != self.direction:
                     self.direction = next_dir
            
            # Game Over / Pause / Quit logic handled inside _handle_input via flags? 
            # No, 'P' and 'Q' should interrupt immediately or set a flag.
            # Let's adjust _handle_input to return a command or handle it.
            # Actually, the original code had distinct handling. 
            # Let's revert to a simpler flow: pause/quit are immediate, optional moves are queued.
            
            # We need to detect if we should exit loop
            if hasattr(self, '_should_quit') and self._should_quit:
                self._should_quit = False
                self._save_high_score()
                return

            if not self._advance_snake():
                self._crash_animation()
                wants_retry = self._game_over_screen()
                self._save_high_score()
                if wants_retry:
                    self._reset_round()
                    continue
                return

    def _handle_input(self, key: int) -> None:
        if key in (curses.KEY_UP, ord("w")):
            self._queue_move(UP)
        elif key in (curses.KEY_DOWN, ord("s")):
            self._queue_move(DOWN)
        elif key in (curses.KEY_LEFT, ord("a")):
            self._queue_move(LEFT)
        elif key in (curses.KEY_RIGHT, ord("d")):
            self._queue_move(RIGHT)
        elif key in (ord("p"), ord("P")):
            if not self._pause_screen():
                self._should_quit = True
        elif key in (ord("q"), ord("Q")):
            self._should_quit = True
            
    def _queue_move(self, new_dir: Direction) -> None:
        # Determine the reference direction for this new move.
        # If the queue is empty, we check against current direction.
        # If queue has items, we check against the LAST queued item.
        if self.move_queue:
            last_dir = self.move_queue[-1]
        else:
            last_dir = self.direction
            
        # Prevent 180 reverses and redundant moves
        if new_dir != OPPOSITES[last_dir] and new_dir != last_dir:
            # Limit queue size to prevent huge lag if user mashes keys
            if len(self.move_queue) < 3:
                self.move_queue.append(new_dir)

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
            
    def _crash_animation(self) -> None:
        # Simple flash effect
        curses.flash()
        head_y, head_x = self.snake[0]
        self.stdscr.addch(head_y, head_x, "X", curses.color_pair(self.COLOR_FOOD) | curses.A_BOLD | curses.A_BLINK)
        self.stdscr.refresh()
        time.sleep(0.5)

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
        
        y = self.sh // 2
        
        self.stdscr.attron(curses.color_pair(self.COLOR_FOOD) | curses.A_BOLD)
        self.stdscr.addstr(y - 1, self.sw // 2 - len(message) // 2, message)
        self.stdscr.attroff(curses.color_pair(self.COLOR_FOOD) | curses.A_BOLD)
        
        self.stdscr.addstr(y, self.sw // 2 - len(summary) // 2, summary)
        self.stdscr.addstr(y + 2, self.sw // 2 - len(prompt) // 2, prompt, curses.A_DIM)
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
