#!/usr/bin/python3
# File name   : LED.py
# Description : WS2812
# E-mail      : sect16@gmail.com
# Author      : Chin Pin Hon
# Date        : 25/04/2020
import logging
import time

import spidev

import ws2812

logger = logging.getLogger(__name__)
mode = 1
color = 'cyan'
frequency = 50
delay = 0.1
step = 0
LED_COUNT = 6  # Number of LED pixels.
brightness = 255  # Set to 0 for darkest and 255 for brightest
SPI = spidev.SpiDev()
SPI.open(0, 0)
THREAD_REFRESH = 0.2
COLORS = ['green', 'red', 'blue', 'cyan', 'yellow', 'magenta']


def color_convert(var, i):
    """
    This function takes a color text and brightness
    :param var: Color text value ('green', 'red', 'blue', 'cyan', 'yellow', 'magenta')
    :param i: Brightness value between 0 - 255
    :returns List of LED values
    """
    if color_check(var):
        if var == 'green':
            return [i, 0, 0]
        elif var == 'red':
            return [0, i, 0]
        elif var == 'magenta':
            return [0, i, i]
        elif var == 'cyan':
            return [i, 0, i]
        elif var == 'blue':
            return [0, 0, i]
        elif var == 'yellow':
            return [i, i, 0]


def color_check(var):
    """
    This function performs a sanity check on the input color string value.
    :param var: Color string value
    :return: boolean
    """
    global COLORS
    if COLORS.count(var) == 1:
        return True
    else:
        logger.error('Invalid input variable: ', var)
        return False


class LED:

    def mode_set(self, var):
        """
        Sets LED light effect.
        0 = Turn off all effects.
        1 = Breathing effect.
        2 = Color loop effect.
        3 = Running effect.
        :param var: integer value 0 - 3.
        :return: void
        """
        if var == 0:
            status = 'OFF'
        elif var == 1:
            status = 'Breathing effect'
        elif var == 2:
            status = 'Color loop effect'
        elif var == 3:
            status = 'Running effect'
        logger.debug('Setting effect mode: ' + status)
        global mode
        mode = var

    def color_set(self, var):
        """
        Sets color of the breathing LED light effect.
        :param status: 1 for enable, 0 for disable
        :return: void
        """
        logger.debug('Setting thread color = %s', var)
        if color_check(var):
            global color
            color = var

    def brightness(self, var):
        """
        Sets LED brightness.
        :param var: integer range 0 - 255
        :return: void
        """
        logger.debug('Setting thread color = %s', var)
        if color_check(var):
            global color
            color = var

    def breathe_frequency_set(self, var):
        """
        Sets speed of the breathing LED light effect.
        :param var: Nominal value is 50. Any value between 1 and 255.
        :return: void
        """
        if 0 < var < 255:
            global frequency
            frequency = var
        else:
            logger.error('Invalid breathe speed: ' + var)

    def update_frequency_set(self, var):
        """
        Sets speed LED light changes.
        :param var: Nominal value is 0.1.
        :return: void
        """
        global delay
        delay = var

    # Define functions which animate LEDs in various ways.
    def colorWipe(self, var):
        """
        Changes all LED color output. For example:

        Green = [255, 0, 0]
        Red = [0, 255, 0]
        Blue = [0, 0, 255]
        Cyan = [255, 0, 255]
        Yellow = [255, 255, 0]
        Magenta = [0, 255, 255]

        :param var: A list containing 3 records containing Green, Red, Blue values
        :return void
        """
        if len(var) == 3 and isinstance(var[0], int) and isinstance(var[1], int) and isinstance(var[2], int):
            data = []
            for x in range(LED_COUNT):
                data.append(var)
            ws2812.write2812(SPI, data)
        else:
            logger.error('Error invalid input value: %s', var)

    def led_thread(self):
        """
        This function runs as a thread to animate LED light effects.
        """
        while True:
            if mode == 1:
                self.breathe_effect()
            elif mode == 2:
                self.loop_effect()
                pass
            elif mode == 3:
                self.running_effect()
                pass
            else:
                time.sleep(THREAD_REFRESH)

    def breathe_effect(self):
        for a in range(0, brightness, frequency):
            if not mode:
                break
            else:
                self.colorWipe(color_convert(color, a))
                time.sleep(delay)
        for b in range(0, brightness, frequency):
            if not mode:
                break
            else:
                self.colorWipe(color_convert(color, int((brightness - 1) - b)))
                time.sleep(delay)

    def loop_effect(self):
        """
        Loop through all possible colors using all LED
        """
        global brightness, COLORS
        for i in COLORS:
            self.colorWipe(color_convert(i, brightness))
            time.sleep(delay)

    def running_effect(self):
        """
        Loop through all possible LED one at a time
        """
        global delay, step, LED_COUNT, brightness
        d = [[0, 0, 0]] * LED_COUNT
        d[step % LED_COUNT] = color_convert(color, brightness)
        ws2812.write2812(SPI, d)
        step = (step + 1) % LED_COUNT
        time.sleep(delay)


if __name__ == '__main__':
    led = LED()
    # led.test(255)
    # LED()
    mode = 3
    led.led_thread()
    # led.loop(255)
    # led.colorWipe(Color(0, 0, 0))
    pass
