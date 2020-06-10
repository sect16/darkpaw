#!/usr/bin/env/python
# E-mail      : sect16@gmail.com
# Author      : Chin Pin Hon
# Date        : 16.01.2020

"""
This file contains constants and global variables.
"""

import cv2

TITLE = 'DarkPaw'
COLOR_SWT_ACT = '#4CAF50'
COLOR_BTN_ACT = '#00E676'
COLOR_BG = '#BBBBBB'  # Set background color
COLOR_TEXT_LABEL = '#000000'
# COLOR_BG = '#000000'  # Set background color
# COLOR_TEXT_LABEL = '#E1F5FE'
COLOR_TEXT = '#E1F5FE'  # Set text color
COLOR_BTN = '#0277BD'  # Set button color
COLOR_GREY = '#A7A7A7'
LABEL_BG = '#F44336'
COLOR_BTN_RED = '#FF6D00'
FONT = cv2.FONT_HERSHEY_SIMPLEX
MAX_CONTOUR_AREA = 5000
FONT_SIZE = 0.5

# Configuration
KEEPALIVE_INTERVAL = 20
INFO_PORT = 2256  # Define port serial
MAX_INFO_RETRY = 10
SERVER_PORT = 10223  # Define port serial
BUFFER_SIZE = 1024
ULTRA_PORT = 2257  # Define port serial
ULTRA_SENSOR = False
VIDEO_PORT = 5555
VIDEO_TIMEOUT = 10000
VIDEO_WIDTH = 640
VIDEO_HEIGHT = 480
POWER_MODULE = True
CAMERA_MODULE = True
DEBUG_MODE = True

ultra_data = 0

guiTuple = (
    "btn_left_side.place(x=30, y=195)", "btn_right_side.place(x=170, y=195)", "btn_low.place(x=330, y=230)",
    "btn_high.place(x=470, y=230)", "btn_left.place(x=330, y=195)", "btn_right.place(x=470, y=195)",
    "btn_Switch_1.place(x=30, y=265)", "btn_Switch_2.place(x=100, y=265)", "btn_Switch_3.place(x=170, y=265)",
    "btn_steady.place(x=30, y=465)", "btn_balance_front_left.place(x=237, y=195)",
    "btn_balance_front.place(x=267, y=195)", "btn_balance_front_right.place(x=297, y=195)",
    "btn_balance_left.place(x=237, y=230)", "btn_balance_center.place(x=267, y=230)",
    "btn_balance_right.place(x=297, y=230)", "btn_balance_back_left.place(x=237, y=265)",
    "btn_balance_back.place(x=267, y=265)", "btn_balance_back_right.place(x=297, y=265)",
    "label_e4.place(x=120, y=110)", "e4.place(x=160, y=110)",
    "label_ambient.place(x=250, y=15)",
    "btn_roll_left.place(x=330, y=265)", "btn_roll_right.place(x=470, y=265)"
)