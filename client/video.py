# E-mail      : sect16@gmail.com
# Author      : Chin Pin Hon
# Date        : 14.01.2020

"""
This script creates the video window, initiates the connection and inserts an overlay.
"""

import base64
import logging
import threading
import time
import traceback

import cv2
import numpy
import zmq

import config
import functions
import gui

logger = logging.getLogger(__name__)

# Variables
connect_event = functions.connect_event
fpv_event = functions.fpv_event
footage_socket_server = None
frame_num = 0
fps = 0


def get_fps_thread(event):
    """
    This function calculates the number of frame per second.
    :param event: Event flag to signal termination.
    """
    global fps, frame_num
    logger.debug('Thread started')
    while event.is_set():
        time.sleep(1)
        fps = frame_num
        frame_num = 0
    logger.debug('Thread stopped')


def call_fpv(event):
    """
    This function creates a ZMQ socket server to receive video footage.
    :param event: Event flag to signal termination.
    """
    global footage_socket_server, fpv_event, connect_event
    if str(gui.btn_FPV['state']) == 'normal':
        gui.btn_FPV['state'] = 'disabled'
    if not fpv_event.is_set():
        logger.info('Starting FPV')
        if connect_event.is_set():
            fpv_event.set()
            fps_threading = threading.Thread(target=get_fps_thread, args=([fpv_event]), daemon=True)
            fps_threading.start()
            footage_socket_server = zmq.Context().socket(zmq.SUB)
            footage_socket_server.RCVTIMEO = config.VIDEO_TIMEOUT  # in milliseconds
            footage_socket_server.bind('tcp://*:%d' % config.VIDEO_PORT)
            footage_socket_server.setsockopt_string(zmq.SUBSCRIBE, numpy.unicode(''))
            # Define a thread for FPV and OpenCV
            video_threading = threading.Thread(target=open_cv_thread, args=([fpv_event]), daemon=True)
            video_threading.start()
            gui.btn_FPV.config(bg='#00E676')
            gui.btn_FPV['state'] = 'normal'
        else:
            logger.info('Cannot start FPV when not connected')
    elif fpv_event.is_set():
        logger.info('Stopping FPV')
        fpv_event.clear()


def open_cv_thread(event):
    """
    This function creates an overlay for the received video footage.
    :param event: Event flag to signal termination.
    """
    logger.debug('Thread started')
    global frame_num, footage_socket_server, fps
    zoom = 1
    multiplier = 0.1
    functions.send('start_video')
    stream = 'FPV Live Video Stream'
    while event.is_set():
        try:
            frame = footage_socket_server.recv_string()
            img = base64.b64decode(frame)
            numpy_image = numpy.frombuffer(img, dtype=numpy.uint8)
            source = cv2.imdecode(numpy_image, 1)
            cv2.putText(source, ('PC FPS: %s' % fps), (40, 40), config.FONT, config.FONT_SIZE, (255, 255, 255), 1,
                        cv2.LINE_AA)
            cv2.putText(source, ('Voltage: %s' % functions.voltage),
                        (int(config.VIDEO_WIDTH) - 160, int(config.VIDEO_HEIGHT) - 150), config.FONT, config.FONT_SIZE,
                        (128, 255, 128), 1,
                        cv2.LINE_AA)
            cv2.putText(source, ('Current: %s' % functions.current),
                        (int(config.VIDEO_WIDTH) - 160, int(config.VIDEO_HEIGHT) - 120), config.FONT, config.FONT_SIZE,
                        (128, 255, 128), 1,
                        cv2.LINE_AA)
            cv2.putText(source, ('CPU Temp: %s' % functions.cpu_temp),
                        (int(config.VIDEO_WIDTH) - 160, int(config.VIDEO_HEIGHT) - 90), config.FONT, config.FONT_SIZE,
                        (128, 255, 128), 1,
                        cv2.LINE_AA)
            cv2.putText(source, ('CPU Usage: %s' % functions.cpu_use),
                        (int(config.VIDEO_WIDTH) - 160, int(config.VIDEO_HEIGHT) - 60), config.FONT, config.FONT_SIZE,
                        (128, 255, 128), 1,
                        cv2.LINE_AA)
            cv2.putText(source, ('RAM Usage: %s' % functions.ram_use),
                        (int(config.VIDEO_WIDTH) - 160, int(config.VIDEO_HEIGHT) - 30), config.FONT, config.FONT_SIZE,
                        (128, 255, 128), 1,
                        cv2.LINE_AA)
            # Ultra thread with data is called from GUI
            if gui.ultrasonic_mode == 1:
                cv2.line(source, (int(config.VIDEO_WIDTH / 2), int(config.VIDEO_HEIGHT / 2)),
                         (int(config.VIDEO_WIDTH / 2) - 60, int(config.VIDEO_HEIGHT / 2) + 60), (255, 255, 255), 1)
                cv2.line(source, (int(config.VIDEO_WIDTH / 2) - 110, int(config.VIDEO_HEIGHT / 2) + 60),
                         (int(config.VIDEO_WIDTH / 2) - 60, int(config.VIDEO_HEIGHT / 2) + 60), (255, 255, 255), 2)
                cv2.putText(source, ('%sm' % config.ultra_data),
                            (int(config.VIDEO_WIDTH / 2) - 110, int(config.VIDEO_HEIGHT / 2) + 50), config.FONT, 0.5,
                            (255, 255, 255), 1,
                            cv2.LINE_AA)
            cv2.namedWindow(stream, cv2.WINDOW_NORMAL)
            cv2.imshow(stream, source)
            frame_num += 1
            c = chr(cv2.waitKey(1) & 255)
            if 'q' == c or cv2.getWindowProperty(stream, cv2.WND_PROP_VISIBLE) == 0:
                fpv_event.clear()
            elif '+' == c:
                zoom += multiplier
                cv2.resizeWindow(stream, int(config.VIDEO_WIDTH * zoom), int(config.VIDEO_HEIGHT * zoom))
            elif '-' == c and config.VIDEO_WIDTH * zoom > 150:
                zoom -= multiplier
                cv2.resizeWindow(stream, int(config.VIDEO_WIDTH * zoom), int(config.VIDEO_HEIGHT * zoom))
            elif '0' == c:
                zoom = 1
                cv2.resizeWindow(stream, config.VIDEO_WIDTH, config.VIDEO_HEIGHT)
        except:
            logger.error('Thread exception: %s', traceback.format_exc())
            time.sleep(0.5)
            break
    if connect_event.is_set():
        try:
            functions.send('stop_video')
        except:
            logger.error('Unable to send command.')
    logger.info('Destroying all CV2 windows')
    cv2.destroyAllWindows()
    footage_socket_server.__exit__()
    gui.btn_FPV.config(bg=config.COLOR_BTN)
    gui.btn_FPV['state'] = 'normal'
    logger.debug('Thread stopped')
    fpv_event.clear()
