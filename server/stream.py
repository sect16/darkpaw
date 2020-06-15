# import the necessary packages
import logging
import time
from threading import Thread

from picamera import PiCamera
from picamera.array import PiRGBArray

import config

logger = logging.getLogger(__name__)


class Stream:
    def __init__(self, **kwargs):
        # initialize the camera
        self.camera = PiCamera()
        # set camera parameters
        self.camera.resolution = config.RESOLUTION
        self.camera.framerate = config.FRAME_RATE
        # set optional camera parameters (refer to PiCamera docs)
        for (arg, value) in kwargs.items():
            setattr(self.camera, arg, value)
        # initialize the stream
        self.rawCapture = PiRGBArray(self.camera, size=config.RESOLUTION)
        time.sleep(1)
        self.camera.exposure_mode = config.CAMERA_EXPOSURE  # Lock gains and disable auto exposure
        self.camera.awb_mode = config.CAMERA_AWB
        self.camera.meter_mode = config.CAMERA_METERING
        # Automatic shutter
        self.camera.shutter_speed = 0
        self.camera.exposure_compensation = 1
        self.camera.video_denoise = True
        self.camera.video_stabilization = False
        self.camera.stop_preview()
        self.stream = self.camera.capture_continuous(self.rawCapture,
                                                     format="bgr", use_video_port=True, resize=None, splitter_port=0)
        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.frame = None
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        t = Thread(target=self.update, args=(), daemon=True)
        t.setName('stream_thread')
        t.start()
        return self

    def update(self):
        logger.info('Thread started')
        # keep looping infinitely until the thread is stopped
        for f in self.stream:
            # grab the frame from the stream and clear the stream in
            # preparation for the next frame
            self.frame = f.array
            self.rawCapture.truncate(0)
            # if the thread indicator variable is set, stop the thread
            # and resource camera resources
            if self.stopped:
                logger.info('Stopping stream and closing camera.')
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
                logger.info('Thread stopped')
                return

    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
