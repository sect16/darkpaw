import base64
import logging
import threading
import time
import traceback

import coloredlogs
import cv2
import numpy
import zmq

import gui
import interface

# Configuration
VIDEO_PORT = 5555
VIDEO_TIMEOUT = 10000
FONT = cv2.FONT_HERSHEY_SIMPLEX

# Create a logger object.
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG',
                    fmt='%(asctime)s.%(msecs)03d %(levelname)7s %(thread)5d --- [%(threadName)16s] %(funcName)-39s: %(message)s')

# Variables
connect_event = interface.connect_event
fpv_event = interface.fpv_event
footage_socket_server = None
frame_num = 0
fps = 0


def get_fps_thread(event):
    global fps, frame_num
    logger.debug('Thread started')
    while event.is_set():
        time.sleep(1)
        fps = frame_num
        frame_num = 0
    logger.debug('Thread stopped')


def call_fpv(event):
    global footage_socket_server, FONT, VIDEO_PORT, fpv_event, connect_event, VIDEO_TIMEOUT
    if str(gui.btn_FPV['state']) == 'normal':
        gui.btn_FPV['state'] = 'disabled'
    if not fpv_event.is_set():
        logger.info('Starting FPV')
        if connect_event.is_set():
            fpv_event.set()
            fps_threading = threading.Thread(target=get_fps_thread, args=([fpv_event]), daemon=True)
            fps_threading.start()
            footage_socket_server = zmq.Context().socket(zmq.SUB)
            footage_socket_server.RCVTIMEO = VIDEO_TIMEOUT  # in milliseconds
            footage_socket_server.bind('tcp://*:%d' % VIDEO_PORT)
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
    logger.debug('Thread started')
    global frame_num, footage_socket_server, FONT, fps
    interface.tcp_client_socket.send('start_video'.encode())
    while event.is_set():
        try:
            frame = footage_socket_server.recv_string()
            img = base64.b64decode(frame)
            numpy_image = numpy.frombuffer(img, dtype=numpy.uint8)
            source = cv2.imdecode(numpy_image, 1)
            cv2.putText(source, ('PC FPS: %s' % fps), (40, 20), FONT, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(source, ('CPU Temperature: %s' % interface.cpu_temp), (370, 350), FONT, 0.5, (128, 255, 128), 1,
                        cv2.LINE_AA)
            cv2.putText(source, ('CPU Usage: %s' % interface.cpu_use), (370, 380), FONT, 0.5, (128, 255, 128), 1,
                        cv2.LINE_AA)
            cv2.putText(source, ('RAM Usage: %s' % interface.ram_use), (370, 410), FONT, 0.5, (128, 255, 128), 1,
                        cv2.LINE_AA)
            cv2.imshow("Stream", source)
            frame_num += 1
            cv2.waitKey(1)
        except:
            logger.error('Thread exception: %s', traceback.format_exc())
            time.sleep(0.5)
            break
    if connect_event.is_set():
        try:
            interface.tcp_client_socket.send('stop_video'.encode())
        except:
            logger.error('Unable to send command.')
    logger.debug('Destroying all CV2 windows')
    cv2.destroyAllWindows()
    footage_socket_server.__exit__()
    gui.btn_FPV.config(bg=gui.color_btn)
    gui.btn_FPV['state'] = 'normal'
    logger.debug('Thread stopped')
    fpv_event.clear()
