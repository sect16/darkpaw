import logging
import os
import random
import threading
import time

import config

logger = logging.getLogger(__name__)

def speak(text):
    speak_threading = threading.Thread(target=speak_thread, args=[text], daemon=True)
    speak_threading.start()


def speak_thread(input_text):
    logger.info('Text to speech received: "%s"', input_text)
    while True:
        if config.allow_speak == 1 and abs(int(time.time()) - config.last_text[0]) > config.SPEAK_DELAY:
            config.allow_speak = 0
            if type(input_text) == str:
                speak_command(input_text)
                pass
            elif type(input_text == tuple):
                speak_command(input_text[random.randint(0, len(input_text) - 1)])
                pass
            else:
                logger.error('Unknow input_text type: %s', input_text)
            config.allow_speak = 1
            config.last_text[0] = int(time.time())
            config.last_text[1] = input_text
            break
        elif input_text == config.last_text[1]:
            logger.warning('Discard redundant speech request')
            break
        else:
            logger.warning('Not allowed to speak, waiting...')
            time.sleep(0.5)


def speak_command(text):
    logger.debug('Speaking "%s"', text)
    # subprocess.Popen([str('espeak-ng "%s" -s %d' % (text, config.SPEAK_SPEED))], shell=True)
    # TO-DO test is below subprocess call works
    # subprocess.call(['espeak-ng', '-s' + config.SPEAK_SPEED, test])
    os.system(str('espeak-ng "%s" -s %d' % (text, config.SPEAK_SPEED)))
