#!/usr/bin/env python3
import curses
import random

#!/usr/bin/env python3
import curses
import random
import time
import sys

class AdvancedSnakeGame:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.sh, self.sw = self.stdscr.getmaxyx()
        
        # Game settings
        self.difficulty_levels = {
            'easy': {'speed': 150, 'obstacles': 3, 'powerups': True},
            'medium': {'speed': 100, 'obstacles': 5, 'powerups': True},
            'hard': {'speed': 50, 'obstacles': 8, 'powerups': True}
        }
        
        self.current_difficulty = 'medium'
        self.score = 0
        self.high_score = 0
        self.level = 1
        self.game_state = 'menu'
        
        # Game objects
        self.snake = []
        self.food = []
        self.obstacles = []
        self.powerups = []
        self.powerup_active = None
        self.powerup_timer = 0
        
        # Colors
        self._init_colors()
        
    def _init_colors(self):
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Snake
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)    # Food
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Obstacles
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)   # Powerups
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK) # Score
        
    def _show_menu(self):
        self.stdscr.clear()
        
        title = "🐍 ADVANCED SNAKE GAME 🐍"
        options = [
            "1. Start Game",
            "2. Difficulty: {}".format(self.current_difficulty.capitalize()),
            "3. High Score: {}".format(self.high_score),
            "4. Quit"
        ]
        
        self.stdscr.addstr(2, self.sw//2 - len(title)//2, title, curses.A_BOLD)
        
        for i, option in enumerate(options):
            self.stdscr.addstr(5 + i, self.sw//2 - len(option)//2, option)
        
        self.stdscr.addstr(self.sh - 2, 2, "Use arrow keys to navigate, Enter to select", curses.A_DIM)
        self.stdscr.refresh()
        
    def _show_difficulty_menu(self):
        self.stdscr.clear()
        
        title = "Select Difficulty"
        difficulties = ["Easy", "Medium", "Hard"]
        
        self.stdscr.addstr(2, self.sw//2 - len(title)//2, title, curses.A_BOLD)
        
        for i, diff in enumerate(difficulties):
            marker = "▶" if diff.lower() == self.current_difficulty else " "
            option = "{} {}".format(marker, diff)
            self.stdscr.addstr(5 + i, self.sw//2 - len(option)//2, option)
        
        self.stdscr.refresh()
        
    def _init_game(self):
        self.score = 0
        self.level = 1
        
        # Create snake in the middle
        center_y, center_x = self.sh//2, self.sw//2
        self.snake = [[center_y, center_x + i] for i in range(3)]
        
        # Create initial food
        self.food = self._create_food()
        
        # Create obstacles based on difficulty
        self.obstacles = []
        num_obstacles = self.difficulty_levels[self.current_difficulty]['obstacles']
        for _ in range(num_obstacles):
            self.obstacles.append(self._create_obstacle())
        
        # Clear powerups
        self.powerups = []
        self.powerup_active = None
        self.powerup_timer = 0
        
        # Set game speed
        self.game_speed = self.difficulty_levels[self.current_difficulty]['speed']
        
    def _create_food(self):
        while True:
            y = random.randint(3, self.sh - 4)
            x = random.randint(3, self.sw - 4)
            food = [y, x]
            if (food not in self.snake and 
                food not in self.obstacles and 
                food not in [p[0] for p in self.powerups]):
                return food
                
    def _create_obstacle(self):
        while True:
            y = random.randint(3, self.sh - 4)
            x = random.randint(3, self.sw - 4)
            obstacle = [y, x]
            if (obstacle not in self.snake and 
                obstacle != self.food and 
                obstacle not in self.obstacles and
                obstacle not in [p[0] for p in self.powerups]):
                return obstacle
                
    def _create_powerup(self):
        if random.random() < 0.1:  # 10% chance to spawn powerup
            while True:
                y = random.randint(3, self.sh - 4)
                x = random.randint(3, self.sw - 4)
                powerup = [y, x]
                powerup_type = random.choice(['speed', 'invincible', 'double'])
                if (powerup not in self.snake and 
                    powerup != self.food and 
                    powerup not in self.obstacles and
                    powerup not in [p[0] for p in self.powerups]):
                    return [powerup, powerup_type]
        return None
        
    def _draw_game(self):
        self.stdscr.clear()
        
        # Draw border
        self.stdscr.border()
        
        # Draw snake
        for i, (y, x) in enumerate(self.snake):
            if i == 0:  # Head
                self.stdscr.addch(y, x, '●', curses.color_pair(1) | curses.A_BOLD)
            else:  # Body
                self.stdscr.addch(y, x, '○', curses.color_pair(1))
        
        # Draw food
        y, x = self.food
        self.stdscr.addch(y, x, '🍎', curses.color_pair(2))
        
        # Draw obstacles
        for y, x in self.obstacles:
            self.stdscr.addch(y, x, '■', curses.color_pair(3))
        
        # Draw powerups
        for (y, x), ptype in self.powerups:
            symbol = '⚡' if ptype == 'speed' else '🛡️' if ptype == 'invincible' else '2️⃣'
            self.stdscr.addch(y, x, symbol, curses.color_pair(4))
        
        # Draw UI
        self._draw_ui()
        
    def _draw_ui(self):
        # Score and level
        score_text = f"Score: {self.score}"
        level_text = f"Level: {self.level}"
        high_score_text = f"High Score: {self.high_score}"
        
        self.stdscr.addstr(1, 2, score_text, curses.color_pair(5))
        self.stdscr.addstr(1, self.sw - len(level_text) - 2, level_text, curses.color_pair(5))
        self.stdscr.addstr(2, 2, high_score_text, curses.color_pair(5))
        
        # Active powerup
        if self.powerup_active:
            ptype, time_left = self.powerup_active
            powerup_text = f"{ptype.upper()}: {time_left}s"
            symbol = '⚡' if ptype == 'speed' else '🛡️' if ptype == 'invincible' else '2️⃣'
            self.stdscr.addstr(2, self.sw - len(powerup_text) - 2, f"{symbol} {powerup_text}", curses.color_pair(4))
        
        # Controls help
        controls = "Controls: ↑↓←→ to move, P to pause, Q to quit"
        self.stdscr.addstr(self.sh - 2, self.sw//2 - len(controls)//2, controls, curses.A_DIM)
        
    def _check_collision(self, position):
        y, x = position
        
        # Wall collision
        if y <= 1 or y >= self.sh - 2 or x <= 1 or x >= self.sw - 2:
            return True
            
        # Self collision (unless invincible)
        if position in self.snake[1:] and self.powerup_active != ('invincible', self.powerup_timer):
            return True
            
        # Obstacle collision (unless invincible)
        if position in self.obstacles and self.powerup_active != ('invincible', self.powerup_timer):
            return True
            
        return False
        
    def _handle_powerup(self, position):
        for i, ((py, px), ptype) in enumerate(self.powerups):
            if [py, px] == position:
                self.powerups.pop(i)
                self.powerup_active = (ptype, 10)  # 10 seconds duration
                self.powerup_timer = 10
                
                if ptype == 'speed':
                    self.game_speed = max(20, self.game_speed - 30)
                elif ptype == 'double':
                    self.score += 5  # Bonus points
                
                return True
        return False
        
    def _update_powerup_timer(self):
        if self.powerup_active:
            self.powerup_timer -= 1
            if self.powerup_timer <= 0:
                ptype, _ = self.powerup_active
                if ptype == 'speed':
                    self.game_speed = self.difficulty_levels[self.current_difficulty]['speed']
                self.powerup_active = None
            else:
                self.powerup_active = (self.powerup_active[0], self.powerup_timer)
        
    def _level_up(self):
        if self.score >= self.level * 10:
            self.level += 1
            # Add more obstacles
            new_obstacle = self._create_obstacle()
            if new_obstacle:
                self.obstacles.append(new_obstacle)
            # Increase speed slightly
            self.game_speed = max(20, self.game_speed - 5)
            
    def _game_over(self):
        if self.score > self.high_score:
            self.high_score = self.score
            
        self.stdscr.clear()
        
        game_over_text = "GAME OVER!"
        score_text = f"Final Score: {self.score}"
        high_score_text = f"High Score: {self.high_score}"
        continue_text = "Press any key to continue..."
        
        self.stdscr.addstr(self.sh//2 - 2, self.sw//2 - len(game_over_text)//2, game_over_text, curses.A_BOLD)
        self.stdscr.addstr(self.sh//2, self.sw//2 - len(score_text)//2, score_text)
        self.stdscr.addstr(self.sh//2 + 1, self.sw//2 - len(high_score_text)//2, high_score_text)
        self.stdscr.addstr(self.sh//2 + 3, self.sw//2 - len(continue_text)//2, continue_text)
        
        self.stdscr.refresh()
        self.stdscr.getch()
        
    def run(self):
        curses.curs_set(0)
        self.stdscr.nodelay(1)
        
        direction = curses.KEY_RIGHT
        paused = False
        
        while True:
            if self.game_state == 'menu':
                self._show_menu()
                key = self.stdscr.getch()
                
                if key == ord('1'):
                    self.game_state = 'playing'
                    self._init_game()
                elif key == ord('2'):
                    self.game_state = 'difficulty'
                elif key == ord('4') or key == ord('q'):
                    break
                    
            elif self.game_state == 'difficulty':
                self._show_difficulty_menu()
                key = self.stdscr.getch()
                
                if key == curses.KEY_UP:
                    diffs = list(self.difficulty_levels.keys())
                    current_idx = diffs.index(self.current_difficulty)
                    self.current_difficulty = diffs[max(0, current_idx - 1)]
                elif key == curses.KEY_DOWN:
                    diffs = list(self.difficulty_levels.keys())
                    current_idx = diffs.index(self.current_difficulty)
                    self.current_difficulty = diffs[min(len(diffs) - 1, current_idx + 1)]
                elif key == ord('\n') or key == ord(' '):
                    self.game_state = 'menu'
                    
            elif self.game_state == 'playing':
                if not paused:
                    key = self.stdscr.getch()
                    
                    if key in [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT]:
                        # Prevent 180-degree turns
                        opposite_directions = {
                            curses.KEY_UP: curses.KEY_DOWN,
                            curses.KEY_DOWN: curses.KEY_UP,
                            curses.KEY_LEFT: curses.KEY_RIGHT,
                            curses.KEY_RIGHT: curses.KEY_LEFT
                        }
                        if key != opposite_directions.get(direction):
                            direction = key
                    elif key == ord('p') or key == ord('P'):
                        paused = True
                    elif key == ord('q') or key == ord('Q'):
                        self.game_state = 'menu'
                        continue
                    
                    # Move snake
                    head_y, head_x = self.snake[0]
                    
                    if direction == curses.KEY_UP:
                        head_y -= 1
                    elif direction == curses.KEY_DOWN:
                        head_y += 1
                    elif direction == curses.KEY_LEFT:
                        head_x -= 1
                    elif direction == curses.KEY_RIGHT:
                        head_x += 1
                    
                    new_head = [head_y, head_x]
                    
                    # Check collisions
                    if self._check_collision(new_head):
                        self._game_over()
                        self.game_state = 'menu'
                        continue
                    
                    self.snake.insert(0, new_head)
                    
                    # Check food
                    if new_head == self.food:
                        self.score += 2 if self.powerup_active and self.powerup_active[0] == 'double' else 1
                        self.food = self._create_food()
                        
                        # Chance to spawn powerup
                        powerup = self._create_powerup()
                        if powerup:
                            self.powerups.append(powerup)
                        
                        self._level_up()
                    else:
                        self.snake.pop()
                    
                    # Check powerups
                    self._handle_powerup(new_head)
                    
                    # Update powerup timer
                    self._update_powerup_timer()
                    
                    self._draw_game()
                    self.stdscr.refresh()
                    
                    time.sleep(self.game_speed / 1000.0)
                    
                else:  # Game is paused
                    pause_text = "PAUSED - Press P to resume"
                    self.stdscr.addstr(self.sh//2, self.sw//2 - len(pause_text)//2, pause_text, curses.A_BOLD)
                    self.stdscr.refresh()
                    
                    key = self.stdscr.getch()
                    if key == ord('p') or key == ord('P'):
                        paused = False
                    elif key == ord('q') or key == ord('Q'):
                        self.game_state = 'menu'
                        
def main(stdscr):
    game = AdvancedSnakeGame(stdscr)
    game.run()

if __name__ == "__main__":
    curses.wrapper(main)

if __name__ == "__main__":
    curses.wrapper(main)
