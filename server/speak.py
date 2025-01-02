import logging
import random
import subprocess
import threading
import time
import requests

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
    try:
        if config.TTS == "gtts":
            speak_google_tts(text)
        elif config.TTS == "opentts":
            speak_open_tts(text)
        elif config.TTS == "mimic":
            subprocess.call(
                ['mimic', '-t', text, '-voice', 'slt'])
        elif config.TTS == "espeak":
            subprocess.call(
                ['espeak-ng', '-s', str(config.SPEAK_SPEED), '-p', str(config.SPEAK_PITCH), '-a', str(config.SPEAK_AMP), text])
        else:
            logger.error('Unsupported TTS option specified in config.TTS')
            speak_fallback(text)

        # Python 3.10 and above only
        """
        match config.TTS:
            case config.TTS = "gtts":
                speak_google_tts(text)
            case config.TTS = "opentts":
                speak_open_tts(text)
            case config.TTS = "mimic:
                subprocess.call(
                    ['mimic', '-t', text, '-voice', 'slt'])
            case config.TTS = "espeak":
                subprocess.call(
                    ['espeak-ng', '-s', str(config.SPEAK_SPEED), '-p', str(config.SPEAK_PITCH), '-a', str(config.SPEAK_AMP), text])
            case _:
                logger.error('Unsupported TTS option specified in config.TTS')
                speak_fallback(text)
        """
    except Exception as e:
        logger.error('TTS exception occurred: ', e)
        speak_fallback(text)

def speak_opentts(text):
    #subprocess.call(
    #    #['mimic', '-t', text, '-voice', 'slt'])
    #    ['espeak-ng', '-s', str(config.SPEAK_SPEED), '-p', str(config.SPEAK_PITCH), '-a', str(config.SPEAK_AMP), text])
    params = {
        # "voice": "larynx:southern_english_female-glow_tts",
        "voice": "nanotts:en-US",
        "text": text,
        "vocoder": "low",
        "denoiserStrength": "0.03",
        "cache": "false"
    }
    headers = {"accept": "*/*"}
    response = requests.get(config.OPENTTS_URL, params=params, headers=headers)
    # Check if the response was successful (status code 200)
    if response.status_code == 200:
        # Use subprocess to play the audio
        subprocess.Popen(["aplay"], stdin=subprocess.PIPE).communicate(response.content)
    else:
        print("Error: ", response.status_code)
        speak_fallback(text)

def speak_google_tts(text, lang='en'):
    # Construct the URL for the Google Translate TTS service
    url = f"http://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&q={text}&tl={lang}"
    # Make a GET request to check if the URL is valid
    response = requests.get(url)
    # Check the status code
    if response.status_code == 200:
        # Use ffmpeg to pipe the audio directly to aplay
        process = subprocess.Popen(
            ['ffmpeg', '-i', 'pipe:0', '-f', 'wav', 'pipe:1'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        # Write the audio data to ffmpeg's stdin
        audio_output, error = process.communicate(input=response.content)
        # Play the audio using aplay
        if audio_output:
            aplay_process = subprocess.Popen(['aplay'], stdin=subprocess.PIPE)
            aplay_process.communicate(input=audio_output)
        else:
            print("Error in audio output:", error.decode())
    else:
        print(f"Failed to fetch audio. Status code: {response.status_code}")
        speak_fallback(text)

def speak_fallback(text):
    subprocess.call(
    #    ['mimic', '-t', text, '-voice', 'slt'])
        ['espeak-ng', '-s', str(config.SPEAK_SPEED), '-p', str(config.SPEAK_PITCH), '-a', str(config.SPEAK_AMP), text])

