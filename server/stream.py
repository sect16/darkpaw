#!/usr/bin/python3
# File name   : stream.py
# Description : PiCamera2 video capture and serve HTTP requests at http:<this-ip-address>:8000. Needs simplejpeg to be installed (pip3 install simplejpeg).
# E-mail      : sect16@gmail.com
# Author      : Chin Pin Hon (Mostly copied from https://picamera.readthedocs.io/en/release-1.13/recipes2.html)
# Date        : 18/07/2024
#

import io
import logging
import socketserver
import time
from http import server
from queue import LifoQueue
from threading import Condition
from threading import Thread

import cv2
from libcamera import controls
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput

import config

logger = logging.getLogger(__name__)

PAGE = """\
<html>
<head>
<title>darkpaw MJPEG streaming</title>
</head>
<body>
<h1>darkpaw MJPEG Streaming</h1>
"""

image_tag = "<img src=\"stream.mjpg\" width=\"" + str(config.RESOLUTION[0]) + "\" height=\"" + str(
    config.RESOLUTION[1]) + "\" />"
PAGE += image_tag

PAGE += """\
</body>
</html>
"""


class FileVideoStream:
    def __init__(self, queueSize=2):
        # initialize the file video stream along with the boolean
        # used to indicate if the thread should be stopped or not
        self.cap = cv2.VideoCapture('http://localhost:' + str(config.VIDEO_PORT + 1) + '/stream.mjpg')
        self.stopped = False
        # initialize the queue used to store frames read from
        # the video file
        self.Q = LifoQueue(maxsize=queueSize)

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True

    def read(self):
        # return next frame in the queue
        return self.Q.get()

    def more(self):
        # return True if there are still frames in the queue
        return self.Q.qsize() > 0

    def update(self):
        # keep looping infinitely
        while True:
            # if the thread indicator variable is set, stop the
            # thread
            if self.stopped:
                return
            # read the next frame from the file
            ret, frame_image = self.cap.read()
            if ret:
                # add the frame to the queue
                self.Q.put(frame_image)
            if self.Q.qsize() > 1:
                self.Q.get()

    def start(self):
        # start a thread to read frames from the file video stream
        frame_thread = Thread(target=self.update, args=())
        frame_thread.setName("frame_thread")
        frame_thread.daemon = True
        frame_thread.start()
        return self


class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()


streamingOutput = StreamingOutput()
piCamera2 = Picamera2()


class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                # tracking serving time
                start_time = time.time()
                frame_count = 0
                # endless stream
                while True:
                    with streamingOutput.condition:
                        streamingOutput.condition.wait()
                        frame = streamingOutput.frame
                        frame_count += 1
                        # calculate FPS every 5s
                        if (time.time() - start_time) > 5:
                            logger.debug("FPS: " + str(frame_count / (time.time() - start_time)))
                            frame_count = 0
                            start_time = time.time()
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


class Stream():
    def __init__(self):
        self.streamingServer = StreamingServer(('', config.VIDEO_PORT + 1), StreamingHandler)

    def start(self):
        # start a thread to read frames from the file video stream
        stream_thread = Thread(target=self.serveHttp, args=())
        stream_thread.setName("stream_thread")
        stream_thread.daemon = True
        stream_thread.start()
        return self

    def serveHttp(self):
        piCamera2.configure(
            piCamera2.create_video_configuration(queue=False,
                                                 main={"size": (config.RESOLUTION[0], config.RESOLUTION[1])}))
        piCamera2.start_recording(JpegEncoder(), FileOutput(streamingOutput))
        piCamera2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
        try:
            self.streamingServer.serve_forever()
        finally:
            logger.info('Stopping piCamera2 recording.')
            piCamera2.stop_recording()
            self.streamingServer.socket.close()
        # start the thread to read frames from the video stream
        return self

    def stop(self):
        logger.info('stopping server on port {}'.format(self.streamingServer.server_port))
        self.streamingServer.shutdown()
        return self


if __name__ == "__main__":
    stream = Stream()
    stream.serveHttp()
