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
REDUCED_FRAME_RATE = 12
frame_image = None
average = None
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
        """
        Main video capture thread. Sends frames to CV2 for image processing when mode is set.
        Automatically reduces frame rate to reduce CPU usage when function mode is enabled.

        :param event: Signals thread to stop when event is set.
        :return: void
        """
        global frame_image, last_motion_captured
        logger.info('Thread started')
        ap = argparse.ArgumentParser()  # OpenCV initialization
        ap.add_argument("-b", "--buffer", type=int, default=64,
                        help="max buffer size")
        args = vars(ap.parse_args())
        pts = deque(maxlen=args["buffer"])
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
                frame_rate_mili = int(1000000 / REDUCED_FRAME_RATE)
                text = find_color(self, pts, args)
            elif WatchDogMode:
                frame_rate_mili = int(1000000 / REDUCED_FRAME_RATE)
                text = watchdog()
            else:
                frame_rate_mili = int(1000000 / config.FRAME_RATE)
                last_motion_captured = datetime.datetime.now()
                text = ''
            if config.VIDEO_OUT:
                cv2.putText(frame_image, text, (40, 60), config.FONT, config.FONT_SIZE, (255, 255, 255), 1,
                            cv2.LINE_AA)
                if mq.closed:
                    logger.info('Initializing ZMQ client...')
                    mq = init_client()
                try:
                    encoded, buffer = cv2.imencode('.jpg', frame_image)
                    mq.send(base64.b64encode(buffer), zmq.NOBLOCK)
                except:
                    logger.warning('Unable to encode frame.')
                    pass
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
    global average, last_motion_captured, motion_counter, frame_image, image_loop_start
    last_run = datetime.datetime.now()
    # Convert frame to grayscale, and blur it
    grayscale = cv2.cvtColor(frame_image, cv2.COLOR_BGR2GRAY)
    grayscale = cv2.GaussianBlur(grayscale, (21, 21), 0)
    # if the background frame is None, initialize it
    if average is None:
        logger.info("Saving background model for motion detection")
        average = grayscale.copy().astype("float")
    # Get 50% of the new frame and add it to 50% of the accumulator
    cv2.accumulateWeighted(grayscale, average, 0.5)
    delta = cv2.absdiff(grayscale, cv2.convertScaleAbs(average))
    # threshold the delta image, dilate the thresholded image to fill
    # in holes, then find contours on thresholded image
    # threshold = cv2.threshold(delta, 50, 255, cv2.THRESH_BINARY)[1]
    threshold = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]
    threshold = cv2.dilate(threshold, None, iterations=2)
    contours = cv2.findContours(threshold.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    # loop over the contours
    for c in contours:
        # if the contour is too small, ignore it
        if cv2.contourArea(c) < config.MAX_CONTOUR_AREA:
            # logger.debug('Contour too small (%s), ignoring...', cv2.contourArea(c))
            continue
        logger.debug('Contour detected (%s)', cv2.contourArea(c))
        speak(speak_dict.bark)
        # compute the bounding box for the contour, draw it on the frame, and update the text
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame_image, (x, y), (x + w, y + h), (128, 255, 0), 1)
        motion_counter += 1
        logger.info('Motion frame counter: %s', motion_counter)
        led.color_set(WATCH_ALERT)
        last_motion_captured = last_run
        # Write last detected buffer, threshold and delta image to disk
        with open('buffer.jpg', mode='wb') as file:
            encoded, buffer = cv2.imencode('.jpg', frame_image)
            file.write(buffer)
        with open('delta.jpg', mode='wb') as file:
            encoded, buffer = cv2.imencode('.jpg', delta)
            file.write(buffer)
        with open('threshold.jpg', mode='wb') as file:
            encoded, buffer = cv2.imencode('.jpg', threshold)
            file.write(buffer)
        return 'Motion detected'
    if (last_run - last_motion_captured).seconds >= 3:
        led.color_set(WATCH_STANDBY)
        return 'No motion detected for ' + str(last_run - last_motion_captured).split('.', 2)[0]
    else:
        return 'No motion detected'


def find_color(self, pts, args):
    global Y_lock, X_lock
    hsv = cv2.cvtColor(frame_image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, self.colorLower, self.colorUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)[-2]
    if len(cnts) > 0:
        text = 'Target Detected'
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
            outv_Y = move.normalize(int(round((pid.GenOut(error)), 0)), 80, 0)
            move.robot_pitch_roll(-outv_Y, 0)
            Y_lock = 0
        elif Y > (config.RESOLUTION[1] / 2 + tor):
            error = (Y - config.RESOLUTION[1]) / 2.2
            outv_Y = move.normalize(int(round((pid.GenOut(error)), 0)), 80, 0)
            move.robot_pitch_roll(outv_Y, 0)
            Y_lock = 0
        else:
            Y_lock = 1

        if X < (config.RESOLUTION[0] / 2 - tor):
            error_X = abs(X - config.RESOLUTION[0] / 2) / config.RESOLUTION[0] / 2 * 100
            outv_X = int(round((pid.GenOut(error_X)), 0))
            move.robot_yaw(outv_X)
            X_lock = 0
        elif X > (config.RESOLUTION[0] / 2 + tor):
            error_X = abs(X - config.RESOLUTION[0] / 2) / config.RESOLUTION[0] / 2 * 100
            outv_X = int(round((pid.GenOut(error_X)), 0))
            move.robot_yaw(-outv_X)
            X_lock = 0
        else:
            X_lock = 1
        # logger.debug('Find color position output (X,Y) = (%s,%s)', outv_X, outv_Y)
        # if X_lock == 1 and Y_lock == 1:
        led.color_set('red')
    else:
        text = 'Detecting target'
        led.color_set('yellow')

    for i in range(1, len(pts)):
        if pts[i - 1] is None or pts[i] is None:
            continue
        thickness = int(numpy.sqrt(args["buffer"] / float(i + 1)) * 2.5)
        cv2.line(frame_image, pts[i - 1], pts[i], (0, 0, 255), thickness)
    return text


if __name__ == '__main__':
    import threading

    event = threading.event
    event.is_set = False
    camera = Camera()
    while 1:
        camera.capture_thread(event)
        pass
