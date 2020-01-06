# Author        : linjunyang
# Date          : 2020/1/5
# File Name     : ele_emulator.py


""" Initialization of Elevator Emulator """


import time
import pygame
from ele_component import Elevator, Button, Passenger

time.sleep(1)
pygame.init()

# COLORS
BLUE = (15, 15, 158)
RED = (255, 0, 0)
DARKGREY = (126, 126, 126)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Game display
screen_width = 800
screen_height = 660

screen = pygame.display.set_mode([screen_width, screen_height])
pygame.display.set_caption('Elevator Simulator')
clock = pygame.time.Clock()

# background = Background(SIZE, 'data/images/tile_bg.png')


elevator_height = screen_height / 11
elevator_width = elevator_height * 0.95
elevator1 = Elevator(screen)
elevator2 = Elevator(screen)
elevator3 = Elevator(screen)
elevator1.setup(2 * screen_width / 5 + screen_width / 6 / 2 - elevator_width / 2, screen_height - elevator_height,
                elevator_width, elevator_height, screen_height * 10 / 11)
elevator2.setup(3*screen_width/5 + screen_width/6/2 - elevator_width/2, screen_height - elevator_height, elevator_width, elevator_height, screen_height*10/11)
elevator3.setup(4*screen_width/5 + screen_width/6/2 - elevator_width/2, screen_height - elevator_height, elevator_width, elevator_height, screen_height*10/11)

butt = []
floor_y_pos = []
for i in range(10):
    y_pos = (screen_height / 11) * (i + 1)
    butt.append(Button(screen, screen_width / 5, y_pos + 16))
    floor_y_pos.append(y_pos)

person_cf = 3
person_tf = 9
person = Passenger(screen, 200, floor_y_pos[10 - person_cf] + 16, person_cf, person_tf)
person.state = 'away'

pygame.display.update()

move_up = False
move_down = False
doors = False
distance = 0
elevator_current_floor = 1
elevator_target_floor = 1
font = pygame.font.SysFont("None", 26)
Rb1 = -1
last_person_state = 'away'

t = 0
cnt = 0
operating = False


def build_floors():
    for i in reversed(range(10)):
        y_pos = (screen_height / 11) * (i + 1)
        pygame.draw.rect(screen, BLACK, [2 * screen_width / 5, y_pos, screen_width / 6, y_pos])
        pygame.draw.rect(screen, BLACK, [3 * screen_width / 5, y_pos, screen_width / 6, y_pos])
        pygame.draw.rect(screen, BLACK, [4 * screen_width / 5, y_pos, screen_width / 6, y_pos])

    cnt = 1
    for i in reversed(range(10)):
        y_pos = (screen_height / 11) * (i + 1)
        text = font.render('F{}'.format(cnt), True, RED)
        pygame.draw.rect(screen, DARKGREY,
                         [screen_width / 5, y_pos, 4 * screen_width / 5 - (screen_width / 5 - screen_width / 6), 5])
        screen.blit(text, [10, y_pos + 20])
        cnt += 1

    text = font.render('Elevator Emulator, Version 2.0', True, WHITE)
    screen.blit(text, (screen_width * 0.35, 8))
    text = font.render('   Developed by: Lin Junyang   ', True, WHITE)
    screen.blit(text, (screen_width * 0.35, 32))
