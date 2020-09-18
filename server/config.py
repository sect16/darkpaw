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
allow_speak = True
VIDEO_OUT = False
last_text = list([int(time.time()), ""])

LISTENER_MAX_ERROR = 10
LISTENER_TIMEOUT = 30
SPEAK_DELAY = 0.5
INFO_PORT = 2256  # Define port serial
SERVER_PORT = 10223  # Define port serial
BUFFER_SIZE = 1024  # Define buffer size
MAX_CONTOUR_AREA = 5000
VIDEO_PORT = 5555
RESOLUTION = [640, 480]
AUDIO_PORT = 3030
FRAME_RATE = 30
ULTRA_PORT = 2257
VOLTAGE_WARN = 7.2  # Low battery voltage warning threshold
VOLTAGE_SHUTDOWN = 6.8  # Critical voltage shutdown threshold
VOLTAGE_CHECK_SECS = 60  # Interval to check for Low and Critical voltage
VOLTAGE_OVERLOAD = 20  # Maximum allowed input voltage
INA219_POLLING = 1  # INA219 power module refresh rate

# Hardware configuration
POWER_MODULE = True  # INA219
SERVO_MODULE = True  # PCA9685
CAMERA_MODULE = True
GYRO_MODULE = True  # MPU6050
ULTRA_MODULE = False

# 100 = Leg spread out
DEFAULT_X = 60

lower_leg_h = 500  # DOWN
lower_leg_l = 150  # UP

lower_leg_h2 = 450  # DOWN
lower_leg_l2 = 100  # UP

upper_leg_h = 380  # IN
upper_leg_l = 100  # OUT
upper_leg_h2 = 500  # IN
upper_leg_l2 = 220  # OUT
torso_h = 450  # FORWARD
torso_l = 150  # BACKWARD
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
# Set maximum wiggle value
torso_w = int((torso_h - torso_l) / 2)

servo = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
servo_init = []
servo_h = [450, 500, 380, 450, 450, 500, 500, 450, 500, 500, 500, 380]
servo_l = [150, 150, 100, 150, 100, 220, 200, 100, 220, 200, 150, 100]
SPEED = 5
led = 50
height = 50

OFFSET_VOLTAGE = 0
OFFSET_CURRENT = 0
OFFSET_AMBIENT = 0
AUDIO_INPUT = 'hw:1,0'
CONTROLLER_POLL = 0.01

"""
auto: use automatic exposure mode
night: select setting for night shooting
nightpreview:
backlight: select setting for backlit subject
spotlight:
sports: select setting for sports (fast shutter etc.)
snow: select setting optimised for snowy scenery
beach: select setting optimised for beach
verylong: select setting for long exposures
fixedfps: constrain fps to a fixed value
antishake: antishake mode
fireworks: select setting optimised for fireworks
"""
CAMERA_EXPOSURE = 'auto'

"""
'off'     
'auto'     
'sunlight'
'cloudy'        
'shade' 
'tungsten'
'fluorescent'   
'incandescent'  
'flash'        
'horizon'       
"""
CAMERA_AWB = 'auto'
"""     
'average'
'spot'  
'backlit'
'matrix'
"""
CAMERA_METERING = 'backlit'