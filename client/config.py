#!/usr/bin/env/python
# E-mail      : sect16@gmail.com
# Author      : Chin Pin Hon
# Date        : 14.01.2020

"""
This file contains constants and global variables.
"""

import cv2

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

# Configuration
INFO_PORT = 2256  # Define port serial
SERVER_PORT = 10223  # Define port serial
BUFFER_SIZE = 1024
ULTRA_PORT = 2257  # Define port serial
ULTRA_SENSOR = None
VIDEO_PORT = 5555
VIDEO_TIMEOUT = 10000

ultra_data = 0
