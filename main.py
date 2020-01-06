# Author        : linjunyang
# Date          : 2020/1/5
# File Name     : main.py


print()
print('-----------------------------------------------------------')
print('           Elevator Emulator & AI Controller')
print('                     Version 2.0')
print('                Author: Lin Junyang')
print('                Email : liynjy@163.com')
print('                WeChat: liynjy')
print('       This is Reinforcement Learning DQN Demon.')
print('Reinforcement Learning DQN usage in Smart Elevator Control.')
print('-----------------------------------------------------------')
print()

'''
[ Modification History ]
2020-1-5 
1) Simplified elevator logic:
   - only one passenger at a time.
   - only one elevator is used (other two reserved for future development).
2) Fixed some bugs.
3) Adjusted AI model parameters.
'''

import sys
from ele_emulator import *
from ele_controller import *


#####################################################################
""" Select to use AI Controller or Non-AI Controller """
USE_AI_CONTROLLER = True
ai_controller = Elevator_AI_Control()
el_controller = ElevatorBaseControl()
#####################################################################


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Random person show up
    if person.state == 'away':
        if person.random_showup():
            if person.cf < person.tf:
                butt[10 - person.tf].up_cur = butt[10 - person.tf].up_req
            else:
                butt[10 - person.tf].down_cur = butt[10 - person.tf].down_req

    # Elevator and Controller Status
    if elevator_current_floor == elevator_target_floor:
        if operating:
            operating = False  # End control operation
            if elevator_current_floor == person.cf and person.state == 'waiting':
                person.state = 'entering'
                Rb1 += 10.
            elif elevator_current_floor == person.tf and person.state == 'in_elevator':
                person.state = 'existing'
                Rb1 += 10.
                person.y = floor_y_pos[10 - person.tf] + 16
                butt[10 - elevator_current_floor].up_cur = butt[10 - elevator_current_floor].up
                butt[10 - elevator_current_floor].down_cur = butt[10 - elevator_current_floor].down

        if (person.state == 'waiting' or person.state == 'in_elevator'):
            t += 1

            ''' 
            if Rb1 >= 0:
                print("[{:f}] +{:d} \t{:s}".format(t, Rb1, person.state))
            else:
                print("[{:f}] {:d} \t{:s}".format(t, Rb1, person.state))
            '''

            # elevator control action
            if USE_AI_CONTROLLER == True:
                if person.state == 'waiting':
                    per_st = 0
                elif person.state == 'in_elevator':
                    per_st = 1
                else:
                    per_st = -1
                X = np.array([person.cf, person.tf, per_st, elevator_current_floor])
                elevator_target_floor = ai_controller.get_target_floor(X, Rb1)
            else:
                elevator_target_floor = el_controller.get_target_floor(person, elevator_current_floor)

            operating = True  # Start control operation

            Rb1 = (10 - abs(elevator_target_floor - elevator_current_floor)) * 0.  # 0.01

            last_person_state = person.state

            if elevator_target_floor > 10:
                # print("Requested same floor")
                elevator_target_floor = elevator_current_floor
                distance = 0
            else:
                current_pos = elevator1.floor_height * elevator_current_floor - elevator1.cabin_h + 1
                distance = abs((current_pos - elevator1.floor_height * elevator_target_floor) + elevator1.cabin_h - 1)

            # print("Target Floor:", target_floor)
            if elevator_current_floor < elevator_target_floor:
                move_up = True
            elif elevator_current_floor > elevator_target_floor:
                move_down = True
            doors = True

    # Movements
    if move_up:
        go = False
        if elevator1.doors_opened and doors:
            # print('Doors are:', elevator1.doors_opened)
            elevator1.close_doors()
        else:
            go = True
            doors = False
        if go and not doors:
            if distance <= 0:
                go = False
            else:
                elevator1.move_up()
                distance -= abs(elevator1.cabin.speed)

        if not go and not doors:
            if not elevator1.doors_opened:
                elevator1.open_doors()
            # print('Doors are:', elevator1.doors_opened)
            else:
                move_up = False
                elevator_current_floor = elevator_target_floor

    if move_down:
        go = False
        if elevator1.doors_opened and doors:
            # print('Doors are:', elevator1.doors_opened)
            elevator1.close_doors()
        else:
            go = True
            doors = False
        if go and not doors:
            if distance <= 0:
                go = False
                doors = False
            else:
                elevator1.move_down()
                distance -= abs(elevator1.cabin.speed)
        if not go and not doors:
            if not elevator1.doors_opened:
                elevator1.open_doors()
            # print('Doors are:', elevator1.doors_opened)
            else:
                move_down = False
                elevator_current_floor = elevator_target_floor

    cnt += 1
    if cnt % 100 == 0 or not USE_AI_CONTROLLER or not TRAINING_ACCELERATE:
        screen.fill(BLUE)
        build_floors()
        elevator2.draw()
        elevator3.draw()
        for i in range(10):
            butt[i].draw()

    elevator1.draw()
    person.draw()

    # Set FPS
    if USE_AI_CONTROLLER and TRAINING_ACCELERATE:
        clock.tick(2000)
    else:
        clock.tick(50)
    pygame.display.update()
