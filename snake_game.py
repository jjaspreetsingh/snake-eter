#!/usr/bin/env python3
import curses
import random

def main(stdscr):
    # Initial setup
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(100)

    sh, sw = stdscr.getmaxyx()
    box = [[3, 3], [sh - 3, sw - 3]]
    stdscr.border()

    # Create initial snake and food
    snake = [[sh // 2, sw // 2 + 1], [sh // 2, sw // 2], [sh // 2, sw // 2 - 1]]
    food = create_food(snake, box)
    
    for y, x in snake:
        stdscr.addch(y, x, '#')

    stdscr.addch(food[0], food[1], '*')

    # Game state
    score = 0
    direction = curses.KEY_RIGHT

    while True:
        key = stdscr.getch()

        if key in [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT]:
            direction = key

        head = snake[0]
        new_head = [head[0], head[1]]

        if direction == curses.KEY_UP:
            new_head[0] -= 1
        elif direction == curses.KEY_DOWN:
            new_head[0] += 1
        elif direction == curses.KEY_LEFT:
            new_head[1] -= 1
        elif direction == curses.KEY_RIGHT:
            new_head[1] += 1

        snake.insert(0, new_head)
        stdscr.addch(new_head[0], new_head[1], '#')

        # Check if snake eats food
        if new_head == food:
            score += 1
            food = create_food(snake, box)
            stdscr.addch(food[0], food[1], '*')
        else:
            tail = snake.pop()
            stdscr.addch(tail[0], tail[1], ' ')

        # Check for collisions
        if (new_head[0] <= box[0][0] or new_head[0] >= box[1][0] or
            new_head[1] <= box[0][1] or new_head[1] >= box[1][1] or
            new_head in snake[1:]):
            msg = f"Game Over! Score: {score}"
            stdscr.addstr(sh // 2, sw // 2 - len(msg) // 2, msg)
            stdscr.nodelay(0)
            stdscr.getch()
            break
            
        display_score(stdscr, score)
        stdscr.refresh()

def create_food(snake, box):
    food = None
    while food is None:
        food = [random.randint(box[0][0] + 1, box[1][0] - 1),
                random.randint(box[0][1] + 1, box[1][1] - 1)]
        if food in snake:
            food = None
    return food

def display_score(stdscr, score):
    sh, sw = stdscr.getmaxyx()
    score_text = f"Score: {score}"
    stdscr.addstr(1, sw // 2 - len(score_text) // 2, score_text)

if __name__ == "__main__":
    curses.wrapper(main)
