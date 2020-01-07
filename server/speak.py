import logging
import os
import threading
import time

import coloredlogs

import config

# Create a logger object.
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG',
                    fmt='%(asctime)s.%(msecs)03d %(levelname)7s %(thread)5d --- [%(threadName)16s] %(funcName)-39s: %(message)s',
                    logger=logger)


def speak(text):
    speak_threading = threading.Thread(target=speak_thread, args=[text], daemon=True)
    speak_threading.start()


def speak_thread(text):
    logger.info('Text to speech received: "%s"', text)
    while True:
        if config.allow_speak == 1:
            config.allow_speak = 0
            logger.info('Speaking "%s"', text)
            config.last_text = text
            # subprocess.Popen([str('espeak-ng "%s" -s %d' % (text, config.SPEAK_SPEED))], shell=True)
            os.system(str('espeak-ng "%s" -s %d' % (text, config.SPEAK_SPEED)))
            config.allow_speak = 1
            break
        elif text == config.last_text:
            logger.info('Skipping redundant speech')
            break
        else:
            logger.info('Not allowed to speak, waiting...')
            time.sleep(0.5)
