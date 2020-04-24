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
COLOR_BG = '#000000'  # Set background color
COLOR_TEXT = '#E1F5FE'  # Set text color
COLOR_BTN = '#0277BD'  # Set button color
COLOR_GREY = '#A7A7A7'
LABEL_BG = '#F44336'
# color_line = '#01579B'  # Set line color
# color_can = '#212121'  # Set canvas color
# color_oval = '#2196F3'  # Set oval color
COLOR_BTN_RED = '#FF6D00'
FONT = cv2.FONT_HERSHEY_SIMPLEX
MAX_CONTOUR_AREA = 5000

# Configuration
INFO_PORT = 2256  # Define port serial
SERVER_PORT = 10223  # Define port serial
BUFFER_SIZE = 1024
ULTRA_PORT = 2257  # Define port serial
ULTRA_SENSOR = None
VIDEO_PORT = 5555
VIDEO_TIMEOUT = 10000
VIDEO_WIDTH = 640
VIDEO_HEIGHT = 480

ultra_data = 0

guiTuple = (
    "btn_left_side.place(x=30, y=195)", "btn_right_side.place(x=170, y=195)", "btn_low.place(x=330, y=230)",
    "btn_high.place(x=470, y=230)", "btn_left.place(x=330, y=195)", "btn_right.place(x=470, y=195)",
    "btn_Switch_1.place(x=30, y=265)", "btn_Switch_2.place(x=100, y=265)", "btn_Switch_3.place(x=170, y=265)",
    "btn_steady.place(x=30, y=465)"
    # Place holder for future implementation
    # "btn_smooth.place(x=285, y=465)"
)