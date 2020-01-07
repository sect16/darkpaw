#!/bin/python3
import pdb

import Adafruit_PCA9685

pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(50)
print("pwm.set_pwm(12,0,500)")
pdb.set_trace()
input()
