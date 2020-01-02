#!/usr/bin/env/python
# File name   : config.py
# Description : Global variables across modules for DarkPaw
# E-mail      : sect16@gmail.com
# Author      : Chin Pin Hon
# Date        : 2019/11/20

'''
The range of the legs wiggling, you can decrease it to make the robot slower while the frequency unchanged.
DO NOT increase or it may cause mechanical collisions.
'''
default_X = 50
speed_set = 100     # Maximum radius of servo motors

lower_leg_h = 500   # DOWN
lower_leg_l = 150   # UP

lower_leg_h2 = 450   # DOWN
lower_leg_l2 = 100   # UP

upper_leg_h = 380   # IN
upper_leg_l = 100   # OUT
upper_leg_h2 = 500   # IN
upper_leg_l2 = 220   # OUT
torso_h = 400 # FORWARD
torso_l = 100 # BACKWARD
torso_h2 = 500 # FORWARD
torso_l2 = 200 # BACKWARD

lower_leg_m = int((lower_leg_h - lower_leg_l)/2 + lower_leg_l)
lower_leg_m2 = int((lower_leg_h2 - lower_leg_l2)/2 + lower_leg_l2)
upper_leg_m = int((upper_leg_h - upper_leg_l)/2 + upper_leg_l)
upper_leg_m2 = int((upper_leg_h2 - upper_leg_l2)/2 + upper_leg_l2)
torso_m = int((torso_h - torso_l)/2 + torso_l)
torso_m2 = int((torso_h2 - torso_l2)/2 + torso_l2)

lower_leg_w = int((lower_leg_h - lower_leg_l)/2)
upper_leg_w = int((upper_leg_h - upper_leg_l)/2)
torso_w = int((torso_h - torso_l)/2)

servo = [0,0,0,0,0,0,0,0,0,0,0,0]
servo_init = [0,0,0,0,0,0,0,0,0,0,0,0]