#!/usr/bin/python3

# Mostly copied from https://picamera.readthedocs.io/en/release-1.13/recipes2.html
# Run this script, then point a web browser at http:<this-ip-address>:8000
# Note: needs simplejpeg to be installed (pip3 install simplejpeg).

import io
import logging
import socketserver
import time
from http import server
from queue import LifoQueue
from threading import Condition
from threading import Thread

import cv2
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput

import config

logger = logging.getLogger(__name__)

PAGE = """\
<html>
<head>
<title>picamera2 MJPEG streaming demo</title>
</head>
<body>
<h1>Picamera2 MJPEG Streaming Demo</h1>
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
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self


class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()


output = StreamingOutput()
picam2 = Picamera2()


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
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
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
    def start(self, event, server):
        picam2.configure(picam2.create_video_configuration(main={"size": (config.RESOLUTION[0], config.RESOLUTION[1])}))
        picam2.start_recording(JpegEncoder(), FileOutput(output))
        try:
            while not event.is_set():
                server.serve_forever()
        finally:
            picam2.stop_recording()
            logger.info('Stopping thread.')
        # start the thread to read frames from the video stream
        return self

    def read(self):
        return self.output.frame


if __name__ == "__main__":
    import threading

    kill_event = threading.Event()
    kill_event.clear()
    stream = Stream()
    server = StreamingServer(('', config.VIDEO_PORT + 1), StreamingHandler)
    while 1:
        stream.start(kill_event, server)
        pass
