#! /usr/bin/python
# File name   : move.py
# Description : Controlling all servos
# E-mail      : sect16@gmail.com
# Author      : Chin Pin Hon
# Date        : 29/11/2019
import time
import Adafruit_PCA9685

import Kalman_filter
import PID

import config
import coloredlogs, logging

# Create a logger object.
logger = logging.getLogger(__name__)

# By default the install() function installs a handler on the root logger,
# this means that log messages from your code and log messages from the
# libraries that you use will all show up on the terminal.
# coloredlogs.install(level='DEBUG')
coloredlogs.install(level='DEBUG',
                    fmt='%(asctime)s.%(msecs)03d %(levelname)7s %(thread)5d --- [%(threadName)16s] %(funcName)-39s: %(message)s', logger=logger)
pca = Adafruit_PCA9685.PCA9685()
pca.set_pwm_freq(50)
'''
# Configure min and max servo pulse lengths
i=0
for i in range(0,12):
    if i == 0 or i == 3:
        exec('pwm%d=config.torso_m'%i)
        exec('pwm%d_max=config.torso_h'%i)
        exec('pwm%d_min=config.torso_l'%i)

    if i == 6 or i == 9:
        exec('pwm%d=config.torso_m2'%i)
        exec('pwm%d_max=config.torso_h2'%i)
        exec('pwm%d_min=config.torso_l2'%i)

    if i == 1 or i == 10:
        exec('pwm%d=config.lower_leg_m'%i)
        exec('pwm%d_max=config.lower_leg_h'%i)
        exec('pwm%d_min=config.lower_leg_l'%i)

    if i == 4 or i == 7:
        exec('pwm%d=config.lower_leg_m2'%i)
        exec('pwm%d_max=config.lower_leg_h2'%i)
        exec('pwm%d_min=config.lower_leg_l2'%i)


    if i == 2 or i == 11:
        exec('pwm%d=config.upper_leg_m'%i)
        exec('pwm%d_max=config.upper_leg_h'%i)
        exec('pwm%d_min=config.upper_leg_l'%i)

    if i == 5 or i == 8:
        exec('pwm%d=config.upper_leg_m2'%i)
        exec('pwm%d_max=config.upper_leg_h2'%i)
        exec('pwm%d_min=config.upper_leg_l2'%i)
'''        
'''
Leg_I   --- forward --- Leg_III
               |
           robotbody
               |
Leg_II  -- backward --- Leg_IV 
'''
Set_Direction = 1
reach_wiggle = 100
max_wiggle = config.upper_leg_m

'''
the bigger pixel is, the slower the servos will run.
'''
pixel = 50

'''
Set PID
'''
P = 3
I = 0.1
D = 0

'''
>>> instantiation <<<
'''
X_fix_output = 0
Y_fix_output = 0
X_steady = 0
Y_steady = 0
X_pid = PID.PID()
X_pid.SetKp(P)
X_pid.SetKd(I)
X_pid.SetKi(D)
Y_pid = PID.PID()
Y_pid.SetKp(P)
Y_pid.SetKd(I)
Y_pid.SetKi(D)

try:
    from mpu6050 import mpu6050
    sensor = mpu6050(0x68)
except:
    pass

kalman_filter_X =  Kalman_filter.Kalman_filter(0.001,0.1)
kalman_filter_Y =  Kalman_filter.Kalman_filter(0.001,0.1)


'''
if the robot roll over when turning, decrease this value below.
'''
turn_steady = 4/5  # 2/3 4/5 5/6 ...

def set_pwm(servo, pos):
    pca.set_pwm(servo, 0, pos)
    config.servo[servo] = pos
    if config.servo_init.count(0) == 12:
        if config.servo.count(0) == 0:
            config.servo_init = list(config.servo)

def leg_I(x,y,z):
    set_pwm(0, int(config.upper_leg_m + (config.upper_leg_w*y/100)))
    set_pwm(1, int(config.lower_leg_m + (config.lower_leg_w*z/100)))
    set_pwm(2, int(config.torso_m + (config.torso_w*-x/100)))

def leg_II(x,y,z):
    set_pwm(3, int(config.upper_leg_m + (config.upper_leg_w*y/100)))
    set_pwm(4, int(config.lower_leg_m2 + (config.lower_leg_w*-z/100)))
    set_pwm(5, int(config.torso_m2 + (config.torso_w*x/100)))

def leg_III(x,y,z):
    set_pwm(6, int(config.upper_leg_m2 + (config.upper_leg_w*y/100)))
    set_pwm(7, int(config.lower_leg_m2 + (config.lower_leg_w*-z/100)))
    set_pwm(8, int(config.torso_m2 + (config.torso_w*x/100)))
    
def leg_IV(x,y,z):
    set_pwm(9, int(config.upper_leg_m2 + (config.upper_leg_w*-y/100)))
    set_pwm(10, int(config.upper_leg_m + (config.upper_leg_w*z/100)))
    set_pwm(11, int(config.torso_m + (config.torso_w*-x/100)))

def mpu6050Test():
    while 1:
        accelerometer_data = sensor.get_accel_data()
        logger.debug('X=%f, Y=%f, Z=%f', accelerometer_data['x'], accelerometer_data['y'], accelerometer_data['x'])
        time.sleep(0.3)
'''
def move_diagonal(step):
    if step == 1:
        leg_move_diagonal('I', 1, config.speed_set)
        leg_move_diagonal('IV', 1, config.speed_set)

        leg_move_diagonal('II', 3, config.speed_set)
        leg_move_diagonal('III', 3, config.speed_set)
    elif step == 2:
        leg_move_diagonal('I', 2, config.speed_set)
        leg_move_diagonal('IV', 2, config.speed_set)

        leg_move_diagonal('II', 4, config.speed_set)
        leg_move_diagonal('III', 4, config.speed_set)
    elif step == 3:
        leg_move_diagonal('I', 3, config.speed_set)
        leg_move_diagonal('IV', 3, config.speed_set)

        leg_move_diagonal('II', 1, config.speed_set)
        leg_move_diagonal('III', 1, config.speed_set)
    elif step == 4:
        leg_move_diagonal('I', 4, config.speed_set)
        leg_move_diagonal('IV', 4, config.speed_set)

        leg_move_diagonal('II', 2, config.speed_set)
        leg_move_diagonal('III', 2, config.speed_set)

def leg_tripod(name, pos, spot, speed): #Step, Leg pos, iterator, wiggle
    increase = spot/pixel
    wiggle = speed/100
    balance = 50
    if wiggle > 0:
        direction = 1
    else:
        direction = 0
        wiggle=-wiggle

    if name == 'I':
        if pos == 1:
            if direction:
                set_pwm(0, 0, int(config.servo_init[0]-(config.torso_w-balance*wiggle)*increase))
            else:
                set_pwm(0, 0, int(config.servo_init[0]+(config.torso_w-balance*wiggle)*increase))
                pass
        elif pos == 2:
                pass
 
    elif name == 'II':
        
        if pos == 1:
            if direction:
                set_pwm(3, 0, int(config.servo_init[3]+(config.torso_w-balance*wiggle)*increase))
            else:
                set_pwm(3, 0, int(config.servo_init[3]-(config.torso_w-balance*wiggle)*increase))
                pass
        elif pos == 2:
            if direction:
                set_pwm(4, 0, int(config.servo[4]+(config.torso_w*wiggle)*increase))
                set_pwm(3, 0, int(config.servo[3]-(config.torso_w*wiggle)*increase))
            else:
                set_pwm(4, 0, int(config.servo[4]-(config.torso_w*wiggle)*increase))
                set_pwm(3, 0, int(config.servo[3]+(config.torso_w*wiggle)*increase))
                pass

    elif name == 'III':
        if pos == 1:
            if direction:
                set_pwm(6, 0, int(config.servo_init[6]+(config.torso_w-balance*wiggle)*increase))
            else:
                set_pwm(6, 0, int(config.servo_init[6]-(config.torso_w-balance*wiggle)*increase))
                pass
        elif pos == 2:
            if direction:
                set_pwm(6, 0, int(config.servo_init[6]-(config.torso_w-balance*wiggle)*increase))
            else:
                set_pwm(6, 0, int(config.servo_init[6]+(config.torso_w-balance*wiggle)*increase))
                pass
                
    elif name == 'IV':
        if pos == 1:
            if direction:
                set_pwm(9, 0, int(config.servo_init[9]-(config.torso_w-balance*wiggle)*increase))
            else:
                set_pwm(9, 0, int(config.servo_init[9]+(config.torso_w-balance*wiggle)*increase))
                pass
        elif pos == 2:
            if direction:
                set_pwm(9, 0, int(config.servo_init[9]-(config.torso_w-balance*wiggle)*increase))
            else:
                set_pwm(9, 0, int(config.servo_init[9]+(config.torso_w-balance*wiggle)*increase))
                pass

def dove_move_tripod(step, speed, command):
    step_I  = step
    step_II = step
    step_III= step
    step_IV = step
    if step_II > 8:
        step_II = step_II - 8
    if step_III> 8:
        step_III= step_III- 8
    if step_IV > 8:
        step_IV = step_IV - 8
    if command == 'forward':
        for i in range(1,(pixel+1)):
            leg_tripod('I', step_I, i, speed)
            leg_tripod('II', step_II, i, speed)

            leg_tripod('III', step_III, i, speed)
            leg_tripod('IV', step_IV, i, speed)

    elif command == 'backward':
        for i in range(1,(pixel+1)):
            leg_tripod('I', step_I, i, -speed)
            leg_tripod('II', step_II, i, -speed)

            leg_tripod('III', step_III, i, -speed)
            leg_tripod('IV', step_IV, i, -speed)

    elif command == 'left':
        for i in range(1,(pixel+1)):
            leg_tripod('I', step_I, i, -int(speed*turn_steady))
            leg_tripod('II', step_II, i, -int(speed*turn_steady))

            leg_tripod('III', step_III, i, speed)
            leg_tripod('IV', step_IV, i, speed)

    elif command == 'right':
        for i in range(1,(pixel+1)):
            leg_tripod('I', step_I, i, speed)
            leg_tripod('II', step_II, i, speed)

            leg_tripod('III', step_III, i, -int(speed*turn_steady))
            leg_tripod('IV', step_IV, i, -int(speed*turn_steady))


def dove_move_diagonal(step, speed, command):
    step_I  = step
    step_II = step+4
    step_III= step+4
    step_IV = step
    if step_II > 8:
        step_II = step_II - 8
    if step_III> 8:
        step_III= step_III- 8
    if step_IV > 8:
        step_IV = step_IV - 8

    if command == 'forward':
        for i in range(1,(pixel+1)):
            leg_tripod('I', step_I, i, speed)
            leg_tripod('II', step_II, i, speed)

            leg_tripod('III', step_III, i, speed)
            leg_tripod('IV', step_IV, i, speed)

    elif command == 'backward':
        for i in range(1,(pixel+1)):
            leg_tripod('I', step_I, i, -speed)
            leg_tripod('II', step_II, i, -speed)

            leg_tripod('III', step_III, i, -speed)
            leg_tripod('IV', step_IV, i, -speed)

    elif command == 'left':
        for i in range(1,(pixel+1)):
            leg_tripod('I', step_I, i, -speed)
            leg_tripod('II', step_II, i, -speed)

            leg_tripod('III', step_III, i, speed)
            leg_tripod('IV', step_IV, i, speed)

    elif command == 'right':
        for i in range(1,(pixel+1)):
            leg_tripod('I', step_I, i, speed)
            leg_tripod('II', step_II, i, speed)

            leg_tripod('III', step_III, i, -speed)
            leg_tripod('IV', step_IV, i, -speed)
'''

def robot_X(amp):
    '''
    when amp is 0, robot <body>
    when amp is 100, robot >body<
    '''
    wiggle = config.torso_w
    set_pwm(0, int(config.torso_m-wiggle+2*wiggle*amp/100))
    set_pwm(3, int(config.torso_m-wiggle+2*wiggle*amp/100))
    set_pwm(6, int(config.torso_m2+wiggle-2*wiggle*amp/100))
    set_pwm(9, int(config.torso_m2+wiggle-2*wiggle*amp/100))


def look_home():
    robot_stand(50)

def robot_stand(height):
    '''
    highest point 100
    mid point 50
    lowest point 0
    range(100,0)
    '''
    set_pwm(1, int(config.lower_leg_l + (config.lower_leg_w*2/100*height)))
    set_pwm(4, int(config.lower_leg_h - (config.lower_leg_w*2/100*height)))
    set_pwm(7, int(config.lower_leg_h - (config.lower_leg_w*2/100*height)))
    set_pwm(10, int(config.lower_leg_l + (config.lower_leg_w*2/100*height)))

def ctrl_range(raw, max_genout, min_genout):
    if raw > max_genout:
        raw_output = max_genout
    elif raw < min_genout:
        raw_output = min_genout
    else:
        raw_output = raw
    return int(raw_output)
    
def ctrl_pitch_roll(pitch, roll): #Percentage wiggle
    wiggle=config.lower_leg_w
    '''
    look up <- pitch -> look down.
    lean right <- roll -> lean left.
    default values are 0.
    range(-100, 100)
    '''
    set_pwm(1, ctrl_range((config.lower_leg_m-wiggle*pitch/100-wiggle*roll/100), config.lower_leg_h, config.lower_leg_l))
    set_pwm(4, ctrl_range((config.lower_leg_m2-wiggle*pitch/100+wiggle*roll/100), config.lower_leg_h2, config.lower_leg_l2))
    set_pwm(7, ctrl_range((config.lower_leg_m2+wiggle*pitch/100-wiggle*roll/100), config.lower_leg_h2, config.lower_leg_l2))
    set_pwm(10, ctrl_range((config.lower_leg_m+wiggle*pitch/100+wiggle*roll/100), config.lower_leg_h, config.lower_leg_l))


def ctrl_yaw(wiggle, yaw): #Percentage wiggle
    '''
    look left <- yaw -> look right
    default value is 0
    '''
    #robot_X(config.default_X)
    set_pwm(0, int(config.torso_m + wiggle*yaw/100))
    set_pwm(3, int(config.torso_m - wiggle*yaw/100))
    set_pwm(6, int(config.torso_m2 + wiggle*yaw/100))
    set_pwm(9, int(config.torso_m2 - wiggle*yaw/100))

def steady():
    global X_fix_output, Y_fix_output
    accelerometer_data = sensor.get_accel_data()
    X = accelerometer_data['x']
    X = kalman_filter_X.kalman(X)
    Y = accelerometer_data['y']
    Y = kalman_filter_Y.kalman(Y)
    X_fix_output -= X_pid.GenOut(X - X_steady)
    Y_fix_output += Y_pid.GenOut(Y - Y_steady)
    X_fix_output = ctrl_range(X_fix_output, 100, -100)
    Y_fix_output = ctrl_range(Y_fix_output, 100, -100)
    logger.debug('Accelerometer [X,Y] = %s, %s', -X_fix_output, Y_fix_output)
    ctrl_pitch_roll(-X_fix_output, Y_fix_output)

def release():
    pca.set_all_pwm(0,0)

def init_servos():
    for i in range(0,12):
        if i == 1 or i == 10:
            set_pwm(i, config.lower_leg_m)
        if i == 4 or i == 7:
            set_pwm(i, config.lower_leg_m2)
        if i == 2 or i == 11:
            set_pwm(i, config.upper_leg_m)
        if i == 5 or i == 8:
            set_pwm(i, config.upper_leg_m2)
    robot_X(config.default_X)
    
step_input = 1
move_stu = 1
if __name__ == '__main__':  
    init_servos()
    time.sleep(1)
    try:
        while 1:
            steady()
            time.sleep(0.1)
            break
            pass
        
        mpu6050Test()
    except KeyboardInterrupt:
        time.sleep(1)
        release()