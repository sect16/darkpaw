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
frame_num = 0
fps = -1


def fps_thread(event):
    """
    This function calculates the number of frame per second.
    :param event: Event flag to signal termination.
    """
    global fps, frame_num
    logger.debug('Thread started')
    if fps == -1:
        while event.is_set():
            time.sleep(1)
            fps = frame_num
            frame_num = 0
    else:
        logger.error('Expected FPS == -1, previous thread not stopped.')
        return
    logger.debug('Thread stopped')
    fps = -1


def call_fpv(ip):
    """
    This function creates a ZMQ socket to receive video footage.
    :param ip: Server IP address to connect ZMQ socket.
    """
    global fpv_event, connect_event
    if connect_event.is_set() and not fpv_event.is_set() and not functions.thread_isAlive(
            'fps_thread') and not functions.thread_isAlive('open_cv_thread'):
        gui.btn_FPV['state'] = 'disabled'
        logger.info('Starting FPV')
        fpv_event.set()
        fps_threading = threading.Thread(target=fps_thread, args=([fpv_event]), daemon=True)
        fps_threading.setName('fps_thread')
        fps_threading.start()
        mq = zmq.Context().socket(zmq.SUB)
        mq.RCVTIMEO = config.VIDEO_TIMEOUT  # in milliseconds
        # mq.bind('tcp://*:%d' % config.VIDEO_PORT)
        mq.setsockopt(zmq.BACKLOG, 0)
        mq.set_hwm(1)
        mq.setsockopt(zmq.LINGER, 0)
        mq.setsockopt(zmq.CONFLATE, 1)
        mq.connect('tcp://%s:%d' % (ip, config.VIDEO_PORT))
        mq.setsockopt_string(zmq.SUBSCRIBE, numpy.unicode(''))
        # Define a thread for FPV and OpenCV
        video_threading = threading.Thread(target=open_cv_thread, args=([mq, fpv_event]), daemon=True)
        video_threading.setName('open_cv_thread')
        video_threading.start()
        mq.connect('tcp://%s:%d' % (ip, config.VIDEO_PORT))
        mq.setsockopt_string(zmq.SUBSCRIBE, numpy.unicode(''))
        gui.btn_FPV.config(bg='#00E676')
        gui.btn_FPV['state'] = 'normal'
    elif fpv_event.is_set() and functions.thread_isAlive('fps_thread') and functions.thread_isAlive('open_cv_thread'):
        logger.info('Stopping FPV')
        fpv_event.clear()
    else:
        logger.warning('Cannot start video at the moment.')
        logger.debug('Connected: %s, video_enabled: %s, fps_thread: %s, cv_thread: %s.', connect_event.is_set(),
                     fpv_event.is_set(), functions.thread_isAlive('fps_thread'),
                     functions.thread_isAlive('open_cv_thread'))


def open_cv_thread(mq, event):
    """
    This function creates an overlay for the received ZMQ video footage. Clears the fpv_event flag when exception occurs
    :param mq: ZMQ socket
    :param event: Event flag to signal termination.
    """
    logger.debug('Thread started')
    global frame_num, fps
    zoom = 1
    multiplier = 0.1
    functions.send('start_video')
    stream = 'FPV Live Video Stream'
    while event.is_set():
        try:
            frame = mq.recv_string()
            img = base64.b64decode(frame)
            numpy_image = numpy.frombuffer(img, dtype=numpy.uint8)
            source = cv2.imdecode(numpy_image, 1)
            cv2.putText(source, ('PC FPS: %s' % fps), (40, 40), config.FONT, config.FONT_SIZE, (255, 255, 255), 1,
                        cv2.LINE_AA)
            if config.POWER_MODULE:
                cv2.putText(source, ('Voltage: %s' % functions.voltage),
                            (int(config.VIDEO_WIDTH) - 160, int(config.VIDEO_HEIGHT) - 150), config.FONT,
                            config.FONT_SIZE,
                            (128, 255, 128), 1,
                            cv2.LINE_AA)
                cv2.putText(source, ('Current: %s' % functions.current),
                            (int(config.VIDEO_WIDTH) - 160, int(config.VIDEO_HEIGHT) - 120), config.FONT,
                            config.FONT_SIZE,
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
    mq.__exit__()
    logger.debug('Thread stopped')
    fpv_event.clear()
    gui.btn_FPV.config(bg=config.COLOR_BTN)
    gui.btn_FPV['state'] = 'normal'
