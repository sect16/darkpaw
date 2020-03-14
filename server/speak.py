import os
import threading
import time
import logging

import config

logger = logging.getLogger(__name__)

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
