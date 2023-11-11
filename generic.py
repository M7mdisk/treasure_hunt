import pygame as pg
from collections import defaultdict
from enum import Enum
import random
from utils import color_inverse, index_2d, index_all_2d

grid = [
    [' ', ' ', ' ', 'x', ' ', ' ', '*', '*', '*', 'x'],
    [' ', ' ', 'x', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', '*', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', 'x', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', 'o', ' ', ' ', ' ', ' ', ' ', 'x', ' '],
    [' ', '*', '*', '*', ' ', ' ', ' ', ' ', ' ', ' '],
]

COLLECT_ALL = True

DEBUG = True


BLOCK_SIZE=75
FONT_SIZE = 25

# COLORS
WHITE = (255,255,255)
BLACK = (0,0,0)
YELLOW = (255,255,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
PURPLE = (128,0,128)

class Cell(str,Enum):
    PLAYER = "o"
    OBSTACLE = "*"
    TREASURE = "x"
    EMPTY = " "

class Strategy(Enum):
    DFS = 0
    BFS = 1
    ASTAR = 2

color_dict = {
        Cell.OBSTACLE: WHITE,
        Cell.EMPTY: BLACK,
        Cell.PLAYER: YELLOW,
        Cell.TREASURE: GREEN,
    }


grid_size = len(grid)

rects = [[0]*grid_size for _ in range(grid_size)]

explored = defaultdict(bool)
final_path = defaultdict(bool)

dir_names = {
        (-1,0):"Up",
        (1,0): "Down",
        (0,-1): "Left",
        (0,1): "Right"
    }

dirs = dir_names.keys()


player_pos = index_2d(grid,Cell.PLAYER)
treasures = index_all_2d(grid,Cell.TREASURE)

def heuristic(pos:(int,int)):
    x,y = pos
    dist = 9999
    if len(treasures) == 0:
        return 0
    for tx,ty in treasures:
        if grid[tx][ty] == Cell.TREASURE: # Not collected
            dist = min(dist,abs(x-tx) + abs(y-ty))
    return dist

cost = {}

def dequeue_fringe(fringe,strat):
    if strat ==Strategy.BFS:
        return fringe.pop(0)
    elif strat == Strategy.DFS:
        return fringe.pop()

    cur_idx = 0
    cur = fringe[cur_idx][-1]
    for idx,c in enumerate(fringe):
        cell = c[-1]
        if heuristic(cell) + cost[cell] < heuristic(cur) + cost[cur]:
            cur = cell
            cur_idx = idx
    return fringe.pop(cur_idx)


def search(start,strategy):
    cost.clear()
    cost[start] = 0
    fringe = [] 
    fringe.append([start])
    if len(treasures) == 0:
        return []
    while fringe:

        cur = dequeue_fringe(fringe,strategy)
        x,y = cur[-1]
        explored[(x,y)] = True

        pg.time.wait(100)
        draw_grid()
        if grid[x][y] == Cell.TREASURE and (x,y) in treasures:
            return cur

        for dir_x,dir_y in random.sample(dirs,len(dirs)):
            newx,newy = x+dir_x, y+dir_y
            if 0<= newx < grid_size and 0 <=newy < grid_size:
                if grid[newx][newy] != Cell.OBSTACLE and (newx,newy) not in explored:
                    cost[(newx,newy)] = cost[(x,y)] + 1
                    new_path = list(cur)
                    new_path.append((newx,newy))
                    fringe.append(new_path)
    return []

def reset_search():
    global treasures
    cost.clear()
    final_path.clear()
    explored.clear()
    treasures = index_all_2d(grid,Cell.TREASURE)

# pg setup
pg.init()

WIDTH = BLOCK_SIZE * grid_size
font = pg.font.Font(None, FONT_SIZE)
screen = pg.display.set_mode((BLOCK_SIZE * grid_size, WIDTH ))
clock = pg.time.Clock()
running = True

def draw_grid():
    for i in range(grid_size):
        for j in range(grid_size):
            rects[i][j] = pg.Rect(j*BLOCK_SIZE, i*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
            color = color_dict[grid[i][j]]
            if grid[i][j] == Cell.EMPTY:
                if (i,j) in final_path:
                    color= PURPLE
                elif (i,j) in explored:
                    color = BLUE
            pg.draw.rect(screen,color, rects[i][j])
            pg.draw.rect(screen,BLACK, rects[i][j], width=1)
            if DEBUG:
                txt = ""
                if (i,j) in cost:
                    txt+=f"c={cost[(i,j)]}"
                txt+=f"h={heuristic((i,j))}"
                text_surface = font.render(txt, True, color_inverse(color))
                text_rect = text_surface.get_rect(center=rects[i][j].center)
                screen.blit(text_surface, text_rect)
    pg.display.update()

while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
            break
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_b:
                reset_search()
                final_path = search(player_pos,Strategy.BFS)
            elif event.key == pg.K_d:
                reset_search()
                final_path = search(player_pos,Strategy.DFS)
            elif event.key == pg.K_a:
                reset_search()
                final_path = []
                cur_pos = player_pos
                if COLLECT_ALL:
                    while len(treasures):
                        final_path += search(cur_pos,Strategy.ASTAR)
                        explored.clear()
                        treasures.remove(final_path[-1])
                        cur_pos = final_path[-1]
            elif event.key == pg.K_r:
                reset_search()
            elif event.key == pg.K_q:
                running = False
            else:
                break
            print(final_path)

    draw_grid()
    pg.display.flip()

    clock.tick(60)  # limits FPS to 60

pg.quit()
