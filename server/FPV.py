#!/usr/bin/env/python3
# File name   : server.py
# Description : for FPV video and OpenCV functions
# E-mail      : sect16@gmail.com
# Author      : Chin Pin Hon(Based on Adrian Rosebrock's OpenCV code on pyimagesearch.com)
# Date        : 30/12/2019

import cv2
import zmq
import base64
import picamera
from picamera.array import PiRGBArray
import argparse
import imutils
from collections import deque
# import LED
import datetime
# from rpi_ws281x import *
import move
import config
import coloredlogs, logging
import PID
pid = PID.PID()
pid.SetKp(10)
pid.SetKd(0)
pid.SetKi(0)
# Create a logger object.
logger = logging.getLogger(__name__)

# By default the install() function installs a handler on the root logger,
# this means that log messages from your code and log messages from the
# libraries that you use will all show up on the terminal.
# coloredlogs.install(level='DEBUG')
coloredlogs.install(level='DEBUG',
                    fmt='%(asctime)s.%(msecs)03d %(levelname)7s %(thread)5d --- [%(threadName)16s] %(funcName)-39s: %(message)s', logger=logger)
Y_lock = 0
X_lock = 0
tor = 50
FindColorMode = 0
WatchDogMode = 0
# LED = LED.LED()

class FPV:
    def __init__(self):
        self.frame_num = 0
        self.fps = 0
        self.colorUpper = (44, 255, 255)
        self.colorLower = (24, 100, 100)

    def SetIP(self, invar):
        self.IP = invar

    def FindColor(self, invar):
        global FindColorMode
        FindColorMode = invar
        if not FindColorMode:
            move.look_home()

    def WatchDog(self, invar):
        global WatchDogMode
        WatchDogMode = invar

    def fpv_capture_thread(self, IPinver, event):
        ap = argparse.ArgumentParser()  # OpenCV initialization
        ap.add_argument("-b", "--buffer", type=int, default=64,
                        help="max buffer size")
        args = vars(ap.parse_args())
        pts = deque(maxlen=args["buffer"])

        font = cv2.FONT_HERSHEY_SIMPLEX

        camera = picamera.PiCamera()
        camera.resolution = (640, 480)
        camera.framerate = 20
        rawCapture = PiRGBArray(camera, size=(640, 480))

        PORT = 5555
        #IPinver = IPinver + ':' + PORT
        context = zmq.Context()
        footage_socket = context.socket(zmq.PUB)
        logger.debug('Capture connection (%s:%s)', IPinver, PORT)
        footage_socket.connect('tcp://%s:%d' % (IPinver, PORT))

        avg = None
        motionCounter = 0
        lastMovtionCaptured = datetime.datetime.now()

        for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

            if event.is_set():
                camera.close()
                break

            frame_image = frame.array
            cv2.line(frame_image, (300, 240), (340, 240), (128, 255, 128), 1)
            cv2.line(frame_image, (320, 220), (320, 260), (128, 255, 128), 1)
            timestamp = datetime.datetime.now()

            if not FindColorMode:
                pass
            else:
                ####>>>OpenCV Start<<<####
                hsv = cv2.cvtColor(frame_image, cv2.COLOR_BGR2HSV)
                mask = cv2.inRange(hsv, self.colorLower, self.colorUpper)
                mask = cv2.erode(mask, None, iterations=2)
                mask = cv2.dilate(mask, None, iterations=2)
                cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                        cv2.CHAIN_APPROX_SIMPLE)[-2]
                center = None
                if len(cnts) > 0:
                    cv2.putText(frame_image, 'Target Detected', (40, 60), font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                    c = max(cnts, key=cv2.contourArea)
                    ((x, y), radius) = cv2.minEnclosingCircle(c)
                    M = cv2.moments(c)
                    center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                    X = int(x)
                    Y = int(y)
                    if radius > 10:
                        cv2.rectangle(frame_image, (int(x - radius), int(y + radius)),
                                      (int(x + radius), int(y - radius)), (255, 255, 255), 1)
                    logger.debug('Target position X: %d Y: %d', X, Y)
                    if Y < (240 - tor):
                        error = (240 - Y) / 1.2
                        outv = int(round((pid.GenOut(error)), 0))
                        #outv = int(error)
                        if outv > 100:
                            outv = 100
                        # move.look_up(outv)
                        move.ctrl_pitch_roll(-outv, 0)
                        Y_lock = 0
                    elif Y > (240 + tor):
                        error = (Y - 240) / 1.2
                        outv = int(round((pid.GenOut(error)), 0))
                        #outv = int(error)
                        if outv > 100:
                            outv = 100
                        # move.look_down(outv)
                        move.ctrl_pitch_roll(outv, 0)
                        Y_lock = 0
                    else:
                        Y_lock = 1

                    if X < (320 - tor):
                        error_X = (320 - X) / 1.6
                        outv_X = int(round((pid.GenOut(error_X)), 0))
                        #outv_X = int(error_X)
                        if outv_X > 100:
                            outv_X = 100
                        # move.look_left(outv_X)
                        move.ctrl_yaw(config.torso_w, outv_X)
                        X_lock = 0
                    elif X > (320 + tor):
                        error_X = (X - 320) / 1.6
                        outv_X = int(round((pid.GenOut(error_X)), 0))
                        # outv_X = int(error_X)
                        if outv_X > 100:
                            outv_X = 100
                        # move.look_right(outv_X)
                        move.ctrl_yaw(config.torso_w, -outv_X)
                        X_lock = 0
                    else:
                        X_lock = 1

                    # if X_lock == 1 and Y_lock == 1:
                    # LED.breath_color_set('red')

                else:
                    cv2.putText(frame_image, 'Target Detecting', (40, 60), font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                    # LED.breath_color_set('yellow')

                for i in range(1, len(pts)):
                    if pts[i - 1] is None or pts[i] is None:
                        continue
                    thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
                    cv2.line(frame_image, pts[i - 1], pts[i], (0, 0, 255), thickness)
                ####>>>OpenCV Ends<<<####

            if not WatchDogMode:
                pass
            else:
                gray = cv2.cvtColor(frame_image, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (21, 21), 0)

                if avg is None:
                    print("[INFO] starting background model...")
                    avg = gray.copy().astype("float")
                    rawCapture.truncate(0)
                    continue

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
                # print('x')

                # loop over the contours
                for c in cnts:
                    # if the contour is too small, ignore it
                    if cv2.contourArea(c) < 5000:
                        continue

                    # compute the bounding box for the contour, draw it on the frame,
                    # and update the text
                    (x, y, w, h) = cv2.boundingRect(c)
                    cv2.rectangle(frame_image, (x, y), (x + w, y + h), (128, 255, 0), 1)
                    text = "Occupied"
                    motionCounter += 1
                    # print(motionCounter)
                    # print(text)
                    # LED.breath_color_set('red')
                    lastMovtionCaptured = timestamp

                # if (timestamp - lastMovtionCaptured).seconds >= 0.5:
                # LED.breath_color_set('blue')

            encoded, buffer = cv2.imencode('.jpg', frame_image)
            jpg_as_text = base64.b64encode(buffer)
            footage_socket.send(jpg_as_text)

            rawCapture.truncate(0)


if __name__ == '__main__':
    fpv = FPV()
    while 1:
        fpv.fpv_capture_thread('127.0.0.1')
        pass
