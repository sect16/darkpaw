#!/usr/bin/env/python
# File name   : config.py
# Description : Global programe variables across modules for DarkPaw
# E-mail      : sect16@gmail.com
# Author      : Chin Pin Hon
# Date        : 2019/11/20

'''
The range of the legs wiggling, you can decrease it to make the robot slower while the frequency unchanged.
DO NOT increase or it may cause mechanical collisions.
'''
speed_set = 190     # Maximum radius of servo motors

lower_leg_h = 500   # DOWN
lower_leg_l = 150   # UP
upper_leg_h = 370   # IN
upper_leg_l = 100   # OUT
torso_h = 400 # FORWARD
torso_l = 100 # BACKWARD

lower_leg_m = int(lower_leg_h - lower_leg_l + lower_leg_l)
upper_leg_m = int(upper_leg_h - upper_leg_l + upper_leg_l)
torso_m = int(torso_h - torso_l + torso_l)

