#!/usr/bin/env/python
# File name   : switch.py
# E-mail      : sect16@gmail.com
# Author      : Chin Pin Hon
# Date        : 07/06/2020
import logging
import time

import RPi.GPIO as GPIO

logger = logging.getLogger(__name__)
Channel_A_EN = 7
Channel_A_Pin1 = 37
Channel_A_Pin2 = 15
Channel_B_EN = 11
Channel_B_Pin1 = 13
Channel_B_Pin2 = 16
pwm_B = 0
frequency = 60


def switchSetup():
    """
    Initialize GPIO for switch ports 1-3 on Robot HAT.
    :return: void
    """
    global pwm_B
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(29, GPIO.OUT)
    GPIO.setup(31, GPIO.OUT)
    GPIO.setup(33, GPIO.OUT)
    GPIO.setup(Channel_B_EN, GPIO.IN)
    GPIO.setup(Channel_B_Pin1, GPIO.OUT)
    GPIO.setup(Channel_B_Pin2, GPIO.OUT)


def switch(port, status):
    """
    Turns on or off the ports of Robot HAT.
    Example--switch(3, 1)->to switch on port3
    :param port: 1-3
    :param status: 1 On, 0 Off
    :return: void
    """
    if port == 1:
        if status == 1:
            GPIO.output(29, GPIO.HIGH)
        elif status == 0:
            GPIO.output(29, GPIO.LOW)
        else:
            pass
    elif port == 2:
        if status == 1:
            GPIO.output(31, GPIO.HIGH)
        elif status == 0:
            GPIO.output(31, GPIO.LOW)
        else:
            pass
    elif port == 3:
        if status == 1:
            GPIO.output(33, GPIO.HIGH)
        elif status == 0:
            GPIO.output(33, GPIO.LOW)
        else:
            pass
    else:
        logger.error('Invalid Robot HAT port number')


def channel_B(duty):
    """
    Enable/Disable output for L298P IC channel B. Motor A is connected to channel B while Motor B is Channel A.
    In case duty cycle is zero, channel B output is turned OFF. Any other values enables channel
    B output.
    :param duty: duty cycle 0 - 100
    """
    if not duty >= 0 <= 100:
        logger.error('Invalid duty cycle: %s', duty)
    if duty > 0:
        GPIO.output(Channel_B_Pin1, GPIO.HIGH)
        GPIO.output(Channel_B_Pin2, GPIO.LOW)
    else:
        GPIO.output(Channel_B_Pin1, GPIO.LOW)
        GPIO.output(Channel_B_Pin2, GPIO.LOW)


def set_all_switch_off():
    """
    Sets all 3 ports to OFF.
    :return: void
    """
    switch(1, 0)
    switch(2, 0)
    switch(3, 0)
    GPIO.output(Channel_B_Pin1, GPIO.LOW)
    GPIO.output(Channel_B_Pin2, GPIO.LOW)
    # GPIO.output(Channel_A_Pin1, GPIO.LOW)
    # GPIO.output(Channel_A_Pin2, GPIO.LOW)


def destroy():
    """
    Release GPIO resource.
    :return: void
    """
    GPIO.cleanup()


if __name__ == '__main__':
    try:
        switchSetup()
        GPIO.setup(Channel_B_EN, GPIO.OUT)
        GPIO.setup(Channel_B_Pin1, GPIO.OUT)
        GPIO.setup(Channel_B_Pin2, GPIO.OUT)
        try:
            pwm_B = GPIO.PWM(Channel_B_EN, frequency)
        except:
            pass
        pwm_B.start(0)
        while True:
            # break
            for dc in range(0, 101, 5):
                pwm_B.ChangeDutyCycle(dc)
                time.sleep(0.1)
            for dc in range(100, -1, -5):
                pwm_B.ChangeDutyCycle(dc)
                time.sleep(0.1)
        while True:
            break
            frequency += 10
            print('Frequency = ', frequency)
            pwm_B.ChangeFrequency(frequency)
            pwm_B.ChangeDutyCycle(5)
            time.sleep(3)
        pwm_B.ChangeFrequency(50)
        pwm_B.ChangeDutyCycle(5)
        time.sleep(6000)
        destroy()
    except KeyboardInterrupt:
        destroy()
        pass
