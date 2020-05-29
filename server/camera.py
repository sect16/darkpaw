#!/usr/bin/env/python3
# File name   : camera.py
# Description : FPV video and OpenCV functions
# E-mail      : sect16@gmail.com
# Author      : Chin Pin Hon (Based on Adrian Rosebrock's OpenCV code on pyimagesearch.com)
# Date        : 16/05/2020

import argparse
import base64
import datetime
import logging
import time
from collections import deque

import cv2
import imutils
import numpy
import zmq

import config
import led
import move
import pid
import speak_dict
import stream
from speak import speak

logger = logging.getLogger(__name__)

led = led.Led()
pid = pid.Pid()
pid.SetKp(10)
pid.SetKd(0)
pid.SetKi(0)

Y_lock = 0
X_lock = 0
tor = 50
FindColorMode = 0
WatchDogMode = 0
WATCH_STANDBY = 'blue'
WATCH_ALERT = 'red'
frame_image = None
# Init watchdog variables
avg = None
motion_counter = 0
last_motion_captured = datetime.datetime.now()
image_loop_start = datetime.datetime.now()
UltraData = 0.45


class Camera:
    def __init__(self):
        self.frame_num = 0
        self.fps = 0
        self.colorUpper = (44, 255, 255)
        self.colorLower = (24, 100, 100)

    def SetIP(self, invar):
        self.IP = invar

    def FindColor(self, invar):
        global FindColorMode, UltraData
        UltraData = 0.45
        FindColorMode = invar
        if not FindColorMode:
            move.robot_home()

    def WatchDog(self, invar):
        global WatchDogMode
        WatchDogMode = invar

    def UltraData(self, invar):
        global UltraData
        UltraData = invar

    def capture_thread(self, event):
        global frame_image
        logger.info('Thread started')
        ap = argparse.ArgumentParser()  # OpenCV initialization
        ap.add_argument("-b", "--buffer", type=int, default=64,
                        help="max buffer size")
        args = vars(ap.parse_args())
        pts = deque(maxlen=args["buffer"])
        frame_rate_mili = int(1000000 / config.FRAME_RATE)
        video_stream = stream.Stream().start()
        frame_image = video_stream.read()
        context = zmq.Context()
        mq = context.socket(zmq.PUB)
        mq.close()
        while not event.is_set():
            # Draw crosshair lines
            cv2.line(frame_image, (int(config.RESOLUTION[0] / 2) - 20, int(config.RESOLUTION[1] / 2)),
                     (int(config.RESOLUTION[0] / 2) + 20, int(config.RESOLUTION[1] / 2)), (128, 255, 128), 1)
            cv2.line(frame_image, (int(config.RESOLUTION[0] / 2), int(config.RESOLUTION[1] / 2) - 20),
                     (int(config.RESOLUTION[0] / 2), int(config.RESOLUTION[1] / 2) + 20), (128, 255, 128), 1)
            if FindColorMode:
                find_color(self, pts, args)

            elif WatchDogMode:
                watchdog()

            if config.VIDEO_OUT:
                if mq.closed:
                    logger.info('Initializing ZMQ client...')
                    mq = init_client()
                try:
                    encoded, buffer = cv2.imencode('.jpg', frame_image)
                    mq.send(base64.b64encode(buffer), zmq.NOBLOCK)
                except:
                    logger.warning('Unable to encode frame.')
                    pass
                # with open('buffer.jpg', mode='wb') as file:
                #     file.write(buffer)
                # logger.debug('Sending footage using ZMQ')
            elif not config.VIDEO_OUT and not mq.closed:
                destroy_client(mq)
            limit_framerate(frame_rate_mili)
            frame_image = video_stream.read()
        logger.info('Stopping thread.')
        video_stream.stop()


def limit_framerate(frame_rate):
    global image_loop_start
    """
    This function does not do anything if framerate is below preset value.
    If framerate is above preset value, the function sleeps for the remaining amount of time derived from datetime input param. 
    
    :param frame_rate: Frame rate in milliseconds.
    :param image_loop_start: Last run time.
    :return: void
    """
    timelapse = datetime.datetime.now() - image_loop_start
    if timelapse < datetime.timedelta(microseconds=frame_rate):
        time.sleep((frame_rate - timelapse.microseconds) / 1000000)
    image_loop_start = datetime.datetime.now()


def init_client():
    context = zmq.Context()
    mq = context.socket(zmq.PUB)
    mq.setsockopt(zmq.BACKLOG, 0)
    mq.set_hwm(1)
    mq.setsockopt(zmq.LINGER, 0)
    mq.setsockopt(zmq.CONFLATE, 1)
    # mq.connect('tcp://%s:%d' % (client_ip_address, config.FPV_PORT))
    logger.info('FPV ZMQ connection listening on port: %s', config.VIDEO_PORT)
    mq.bind('tcp://*:%d' % config.VIDEO_PORT)
    return mq


def destroy_client(mq):
    logger.info('Terminating ZMQ client.')
    mq.close()


def watchdog():
    global avg, last_motion_captured, motion_counter, frame_image
    timestamp = datetime.datetime.now()
    gray = cv2.cvtColor(frame_image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    if avg is None:
        logger.info("Starting background model for watchdog...")
        avg = gray.copy().astype("float")
    cv2.accumulateWeighted(gray, avg, 0.5)
    frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))

    # threshold the delta image, dilate the thresholded image to fill
    # in holes, then find contours on thresholded image
    thresh = cv2.threshold(frameDelta, 5, 255,
                           cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    # loop over the contours
    for c in cnts:
        # if the contour is too small, ignore it
        if cv2.contourArea(c) < config.MAX_CONTOUR_AREA:
            logger.debug('Contour too small (%s), ignoring...', cv2.contourArea(c))
            continue
        else:
            speak(speak_dict.bark)
        # compute the bounding box for the contour, draw it on the frame,
        # and update the text
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame_image, (x, y), (x + w, y + h), (128, 255, 0), 1)
        motion_counter += 1
        logger.info('Motion frame counter: %s', motion_counter)
        led.color_set(WATCH_ALERT)
        last_motion_captured = timestamp
        with open('buffer.jpg', mode='wb') as file:
            encoded, buffer = cv2.imencode('.jpg', frame_image)
            file.write(buffer)
    if (timestamp - last_motion_captured).seconds >= 0.5:
        logger.debug('No motion detected.')
        # timer = str(timestamp - last_motion_captured).split('.', 2)[0]
        # cv2.putText(frame_image, 'No motion detected for ' + timer, (40, 60), config.FONT, config.FONT_SIZE, (255, 255, 255), 1,
        #             cv2.LINE_AA)
        led.color_set(WATCH_STANDBY)


def find_color(self, pts, args):
    global Y_lock, X_lock
    ####>>>OpenCV Start<<<####
    hsv = cv2.cvtColor(frame_image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, self.colorLower, self.colorUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)[-2]
    if len(cnts) > 0:
        cv2.putText(frame_image, 'Target Detected', (40, 60), config.FONT, config.FONT_SIZE, (255, 255, 255), 1,
                    cv2.LINE_AA)
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        X = int(x)
        Y = int(y)
        if radius > 10:
            cv2.rectangle(frame_image, (int(x - radius), int(y + radius)),
                          (int(x + radius), int(y - radius)), (255, 255, 255), 1)
        logger.debug('Target input frame position X: %d Y: %d', X, Y)
        if Y < (config.RESOLUTION[1] / 2 - tor):
            error = (config.RESOLUTION[1] - Y) / 2.2
            outv_Y = move.ctrl_range(int(round((pid.GenOut(error)), 0)), 80, 0)
            move.ctrl_pitch_roll(-outv_Y, 0)
            Y_lock = 0
        elif Y > (config.RESOLUTION[1] / 2 + tor):
            error = (Y - config.RESOLUTION[1]) / 2.2
            outv_Y = move.ctrl_range(int(round((pid.GenOut(error)), 0)), 80, 0)
            move.ctrl_pitch_roll(outv_Y, 0)
            Y_lock = 0
        else:
            Y_lock = 1

        if X < (config.RESOLUTION[0] / 2 - tor):
            error_X = abs(X - config.RESOLUTION[0] / 2) / config.RESOLUTION[0] / 2 * 100
            outv_X = int(round((pid.GenOut(error_X)), 0))
            move.ctrl_yaw(config.torso_w, outv_X)
            X_lock = 0
        elif X > (config.RESOLUTION[0] / 2 + tor):
            error_X = abs(X - config.RESOLUTION[0] / 2) / config.RESOLUTION[0] / 2 * 100
            outv_X = int(round((pid.GenOut(error_X)), 0))
            move.ctrl_yaw(config.torso_w, -outv_X)
            X_lock = 0
        else:
            X_lock = 1
        # logger.debug('Find color position output (X,Y) = (%s,%s)', outv_X, outv_Y)
        # if X_lock == 1 and Y_lock == 1:
        led.color_set('red')

    else:
        cv2.putText(frame_image, 'Detecting target', (40, 60), config.FONT, config.FONT_SIZE, (255, 255, 255), 1,
                    cv2.LINE_AA)
        led.color_set('yellow')

    for i in range(1, len(pts)):
        if pts[i - 1] is None or pts[i] is None:
            continue
        thickness = int(numpy.sqrt(args["buffer"] / float(i + 1)) * 2.5)
        cv2.line(frame_image, pts[i - 1], pts[i], (0, 0, 255), thickness)
    ####>>>OpenCV Ends<<<####


if __name__ == '__main__':
    import threading

    event = threading.event
    event.is_set = False
    camera = Camera()
    while 1:
        camera.capture_thread(event)
        pass
