import logging
import random
import subprocess
import threading
import time

import config

logger = logging.getLogger(__name__)

def speak(text):
    speak_threading = threading.Thread(target=speak_thread, args=[text], daemon=True)
    speak_threading.setName('speak_thread')
    speak_threading.start()


def speak_thread(input_text):
    logger.info('Text to speech received: "%s"', input_text)
    while True:
        if config.allow_speak and abs(int(time.time()) - config.last_text[0]) > config.SPEAK_DELAY:
            config.allow_speak = False
            if type(input_text) == str:
                speak_command(input_text)
                pass
            elif type(input_text == tuple):
                speak_command(input_text[random.randint(0, len(input_text) - 1)])
                pass
            else:
                logger.error('Unknown input_text type: %s', input_text)
            config.allow_speak = True
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
    #subprocess.call(
    #    #['mimic', '-t', text, '-voice', 'slt'])
    #    ['espeak-ng', '-s', str(config.SPEAK_SPEED), '-p', str(config.SPEAK_PITCH), '-a', str(config.SPEAK_AMP), text])
    import requests
    params = {
        "voice": "larynx:southern_english_female-glow_tts",
        "text": text,
        "vocoder": "low",
        "denoiserStrength": "0.03",
        "cache": "false"
    }
    headers = {"accept": "*/*"}
    try:
        response = requests.get(config.OPENTTS_URL, params=params, headers=headers)
        # Check if the response was successful (status code 200)
        if response.status_code == 200:
            # Use subprocess to play the audio
            subprocess.Popen(["aplay"], stdin=subprocess.PIPE).communicate(response.content)
        else:
            print("Error: ", response.status_code)
            speak_fallback(text)
    except:
        speak_fallback(text)

