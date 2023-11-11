import pygame as pg
from collections import defaultdict
from enum import Enum
from utils import color_inverse, index_2d, index_all_2d
import sys
import pickle

sys.setrecursionlimit(9000)

# from copy import deepcopy
def deepcopy(x):
    return pickle.loads(pickle.dumps(x, -1))

DEPTH_LIMIT = 20

initial_grid = [
    ['*', '*', '*', '*', '*', '*', '*', '*', '*', '*'],
    ['*', ' ', ' ', ' ', '*', '*', '*', '*', '*', '*'],
    ['*', ' ', ' ', ' ', '*', '*', '*', '*', '*', '*'],
    ['*', ' ', ' ', ' ', ' ', '*', '*', '*', '*', '*'],
    ['*', 'x', ' ', ' ', ' ', ' ', '*', '*', '*', '*'],
    ['*', ' ', ' ', ' ', ' ', '*', '*', '*', '*', '*'],
    ['*', ' ', ' ', ' ', ' ', ' ', ' ', 'e', '*', '*'],
    ['*', 'x', ' ', ' ', ' ', ' ', '*', '*', '*', '*'],
    ['*', ' ', 'o', ' ', ' ', 'x', '*', '*', '*', '*'],
    ['*', '*', '*', '*', '*', '*', '*', '*', '*', '*'],
]


initial_grid = [
    [' ','*','*','*','x'],
    [' ',' ','x',' ',' '],
    ['*','*',' ',' ',' '],
    ['*','o',' ',' ',' '],
    ['*','*','*','*','e']
]

DEBUG = False

BLOCK_SIZE=75
FONT_SIZE = 15

# COLORS
WHITE = (255,255,255)
BLACK = (0,0,0)
YELLOW = (255,255,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
PURPLE = (128,0,128)
IDK = (0,128,0)
RED = (255,0,0)

PLAYER = "o"
ENEMY = "e"
OBSTACLE = "*"
TREASURE = "x"
EMPTY = " "

class Strategy(Enum):
    DFS = 0
    BFS = 1
    ASTAR = 2

color_dict = {
    OBSTACLE: WHITE,
    EMPTY: BLACK,
    PLAYER: YELLOW,
    TREASURE: GREEN,
    ENEMY: RED,
}


grid_size = len(initial_grid)
rects = [[0]*grid_size for i in range(grid_size)]

explored_p = defaultdict(bool)
explored_e = defaultdict(bool)
p_path = []
e_path = []

dir_names = {
        (-1,0):"Up",
        (1,0): "Down",
        (0,-1): "Left",
        (0,1): "Right"
    }

dirs = dir_names.keys()

def reset_search():
    explored_e.clear()
    explored_p.clear()

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
            color = color_dict[initial_grid[i][j]]
            if initial_grid[i][j] == EMPTY:
                if (i,j) in p_path:
                    color= PURPLE
                elif (i,j) in e_path:
                    color= IDK
                if (i,j) in p_path and (i,j) in e_path:
                    color=RED
                # elif (i,j) in explored:
                #     color = BLUE
            pg.draw.rect(screen,color, rects[i][j])
            pg.draw.rect(screen,BLACK, rects[i][j], width=1)
            if DEBUG:
                txt = ""
                if (i,j) in cost:
                    txt+=f"c={cost[(i,j)]}"
                # txt+=f"h={heuristic((i,j))}"
                text_surface = font.render(txt, True, color_inverse(color))
                text_rect = text_surface.get_rect(center=rects[i][j].center)
                screen.blit(text_surface, text_rect)
    pg.display.update()


class State():
    def __init__(self,grid) -> None:
        self.grid = deepcopy(grid)
        self.player_pos = index_2d(self.grid,PLAYER)
        self.enemy_pos = index_2d(self.grid,ENEMY)
        self.player_score = 0
        self.player_num_moves = 0
        self.enemy_num_moves = 0
        self.enemy_score = 0
        self.treasures = index_all_2d(self.grid,TREASURE)
        self.t_count = len(self.treasures)
        self.p_visited = set()
        self.e_visited = set()
    
    def evaluate(self):
        # Terminal state
        e_dist = self.heuristic(self.enemy_pos)
        p_dist = self.heuristic(self.player_pos)
        return self.player_score - self.enemy_score
        # return self.player_score / (self.player_num_moves + 1) - (self.enemy_score / (self.enemy_num_moves + 1) )


    def heuristic(self,pos:(int,int)):
        x,y = pos
        dist = 9999
        if len(self.treasures) == 0:
            return 0
        for tx,ty in self.treasures:
            if self.grid[tx][ty] == TREASURE: # Not collected
                dist = min(dist,abs(x-tx) + abs(y-ty))
        return dist
    
    def __str__(self) -> str:
        s = ""
        for row in self.grid:
            s+= "".join(row)
        s+=str(self.player_pos)
        s+=str(self.enemy_pos)
        s+=str(self.player_score)
        s+=str(self.enemy_score)
        s+=str(self.t_count)
        return s
    
    def print(self):
        return
        print("----")
        for row in self.grid:
            print(*row)
        print(self.player_score,self.enemy_score,self.t_count)


def min_max(state:State,is_player_turn:bool,p_path,e_path,depth):

    if len(index_all_2d(state.grid,TREASURE)) == 0:
        return (state.evaluate(),p_path,e_path)


    new_state = deepcopy(state)
    x,y = state.player_pos if is_player_turn else state.enemy_pos
    if is_player_turn:
        new_state.p_visited.add((x,y))
    else:
        new_state.e_visited.add((x,y))

    initial = -99999999 if is_player_turn else 999999999
    res = (initial,p_path,e_path)

    if depth >= DEPTH_LIMIT:
        return (state.evaluate(),p_path,e_path)

    new_state.grid[x][y] = PLAYER if is_player_turn else ENEMY

    if state.grid[x][y] == TREASURE:
        if is_player_turn:
            new_state.player_score+=1
        else:
            new_state.enemy_score+=1
        new_state.t_count -=1
        new_state.treasures.remove((x,y))
        new_state.p_visited.clear()
        new_state.e_visited.clear()


    if len(new_state.treasures) == 0 or new_state.t_count <=0:

        return (new_state.evaluate(),p_path,e_path)

    new_state.print()

    for dir_x,dir_y in dirs:
        newx, newy = x+dir_x, y+dir_y
        if 0 <= newx < grid_size and 0 <= newy < grid_size:
            if new_state.grid[newx][newy] != OBSTACLE:
                new_state.grid[x][y] = EMPTY
                if is_player_turn:
                    if (newx,newy) not in new_state.p_visited:
                        new_state.player_pos = (newx,newy)
                        new_state.player_num_moves += 1
                        new_val = min_max(new_state,not is_player_turn,p_path+[(newx,newy)],e_path,depth+1)
                        if new_val[0] > res[0]:
                            res = new_val
                else:
                    if (newx,newy) not in new_state.e_visited:
                        new_state.enemy_pos = (newx,newy)
                        new_state.enemy_num_moves +=1
                        new_val = min_max(new_state,not is_player_turn,p_path,e_path +[(newx,newy)],depth+1)
                        if new_val[0] < res[0]:
                            res = new_val
    return  res

while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
            break
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_m:
                reset_search()
                s = State(initial_grid)
                print("STARTING")
                cost, p_path,e_path = min_max(s,True,[s.player_pos],[s.enemy_pos],0)
                print(cost,"DONE")
                print(p_path,e_path)
            elif event.key == pg.K_r:
                reset_search()
            elif event.key == pg.K_q:
                running = False
            else:
                break

    draw_grid()
    pg.display.flip()

    clock.tick(60)  # limits FPS to 60

pg.quit()
