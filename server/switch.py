#!/usr/bin/env/python
# File name   : switch.py
# E-mail      : sect16@gmail.com
# Author      : Chin Pin Hon
# Date        : 07/06/2020
import logging
import time

import RPi.GPIO as GPIO

logger = logging.getLogger(__name__)
Motor_A_EN = 7
Motor_B_EN = 11

Motor_A_Pin1 = 37
Motor_A_Pin2 = 40
Motor_B_Pin1 = 13
Motor_B_Pin2 = 12
pwm_B = 0
frequency = 60


def switchSetup():
    global pwm_B
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(29, GPIO.OUT)
    GPIO.setup(31, GPIO.OUT)
    GPIO.setup(33, GPIO.OUT)
    GPIO.setup(Motor_B_EN, GPIO.IN)
    GPIO.setup(Motor_B_Pin1, GPIO.OUT)
    GPIO.setup(Motor_B_Pin2, GPIO.OUT)


def switch(port, status):
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
        print('Wrong Command: Example--switch(3, 1)->to switch on port3')


def channel_B(duty):
    """
    Sets output for L298P IC Motor B.
    :param duty: duty cycle 0 - 100
    """
    if not duty >= 0 <= 100:
        logger.error('Invalid duty cycle: %s', duty)
    if duty > 0:
        GPIO.output(Motor_B_Pin1, GPIO.HIGH)
        GPIO.output(Motor_B_Pin2, GPIO.LOW)
    else:
        GPIO.output(Motor_B_Pin1, GPIO.LOW)
        GPIO.output(Motor_B_Pin2, GPIO.LOW)


def set_all_switch_off():
    switch(1, 0)
    switch(2, 0)
    switch(3, 0)


def destroy():
    GPIO.cleanup()  # Release resource


if __name__ == '__main__':
    try:
        switchSetup()
        GPIO.setup(Motor_B_EN, GPIO.OUT)
        GPIO.setup(Motor_B_Pin1, GPIO.OUT)
        GPIO.setup(Motor_B_Pin2, GPIO.OUT)
        try:
            pwm_B = GPIO.PWM(Motor_B_EN, frequency)
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
