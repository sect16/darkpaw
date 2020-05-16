#!/usr/bin/env/python
# File name   : config.py
# Description : Global variables across modules for DarkPaw
# E-mail      : sect16@gmail.com
# Author      : Chin Pin Hon
# Date        : 2019/11/20

import time

import cv2

FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SIZE = 0.5

SPEAK_SPEED = 150
allow_speak = 1
VIDEO_OUT = 0
last_text = list([int(time.time()), ""])

SPEAK_DELAY = 2
INFO_PORT = 2256  # Define port serial
SERVER_PORT = 10223  # Define port serial
BUFFER_SIZE = 1024  # Define buffer size
MAX_CONTOUR_AREA = 5000
FPV_PORT = 5555
RESOLUTION = [640, 480]
AUDIO_PORT = 3030
FRAME_RATE = 32

"""
The range of the legs wiggling, you can decrease it to make the robot slower while the frequency unchanged.
DO NOT increase or it may cause mechanical collisions.
"""
DEFAULT_X = 50
speed_set = 100  # Maximum radius of servo motors

lower_leg_h = 500  # DOWN
lower_leg_l = 150  # UP

lower_leg_h2 = 450  # DOWN
lower_leg_l2 = 100  # UP

upper_leg_h = 380  # IN
upper_leg_l = 100  # OUT
upper_leg_h2 = 500  # IN
upper_leg_l2 = 220  # OUT
torso_h = 400  # FORWARD
torso_l = 100  # BACKWARD
torso_h2 = 500  # FORWARD
torso_l2 = 200  # BACKWARD

lower_leg_m = int((lower_leg_h - lower_leg_l) / 2 + lower_leg_l)
lower_leg_m2 = int((lower_leg_h2 - lower_leg_l2) / 2 + lower_leg_l2)
upper_leg_m = int((upper_leg_h - upper_leg_l) / 2 + upper_leg_l)
upper_leg_m2 = int((upper_leg_h2 - upper_leg_l2) / 2 + upper_leg_l2)
torso_m = int((torso_h - torso_l) / 2 + torso_l)
torso_m2 = int((torso_h2 - torso_l2) / 2 + torso_l2)

lower_leg_w = int((lower_leg_h - lower_leg_l) / 2)
upper_leg_w = int((upper_leg_h - upper_leg_l) / 2)
torso_w = int((torso_h - torso_l) / 2)

servo = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
servo_init = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
servo_motion = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
resolution = 3
