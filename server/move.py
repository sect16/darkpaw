#! /usr/bin/python
# File name   : move.py
# Description : Controlling all servos
# E-mail      : sect16@gmail.com
# Author      : Chin Pin Hon
# Date        : 29/11/2019

import logging
import threading
import time
import traceback

import Adafruit_PCA9685

import Kalman_filter
import config
import pid

logger = logging.getLogger(__name__)
if config.SERVO_MODULE:
    pca = Adafruit_PCA9685.PCA9685()
    pca.set_pwm_freq(50)

Set_Direction = 1

"""
Set PID
"""
P = 3
I = 0.1
D = 0

# Set how fast the steady mode is updated. Reduce if oscillating.
STEADY_DELAY = 0.005
# Delay interval between servos during initialization. Prevents sudden power surge.
INIT_DELAY = 0.2

"""
>>> instantiation <<<
"""
X_fix_output = 0
Y_fix_output = 0
X_steady = 0
Y_steady = 0
X_pid = pid.Pid()
X_pid.SetKp(P)
X_pid.SetKd(I)
X_pid.SetKi(D)
Y_pid = pid.Pid()
Y_pid.SetKp(P)
Y_pid.SetKd(I)
Y_pid.SetKi(D)
torso_wiggle = config.torso_w
toe_wiggle = config.upper_leg_w

if config.GYRO_MODULE:
    try:
        logger.info('Initializing MPU6050 accelerometer')
        from mpu6050 import mpu6050

        sensor = mpu6050(0x68)
    except:
        logger.error('Exception: %s', traceback.format_exc())
        pass

kalman_filter_X = Kalman_filter.Kalman_filter(0.001, 0.1)
kalman_filter_Y = Kalman_filter.Kalman_filter(0.001, 0.1)

"""
if the robot roll over when turning, decrease this value below.
"""
turn_steady = 4 / 5  # 2/3 4/5 5/6 ...
step_input = 1
move_stu = 1


def servo_thread(servo, pos):
    logger.debug('Thread started')
    if not config.SERVO_MODULE:
        logger.info('Servo module DISABLED')
        return
    if config.servo_motion[servo] == 0:
        config.servo_motion[servo] = 1
        logger.debug("Set PWM on servo [%s], position [%s])", servo, pos)
        SPEED = config.SPEED
        servo_pos = config.servo[servo]
        if servo_pos - pos < 0:
            while servo_pos < pos:
                pca.set_pwm(servo, 0, servo_pos)
                servo_pos += SPEED
        elif servo_pos - pos > 0:
            while servo_pos > pos:
                pca.set_pwm(servo, 0, servo_pos)
                servo_pos -= SPEED
        pca.set_pwm(servo, 0, pos)
        config.servo[servo] = pos
        config.servo_motion[servo] = 0
    else:
        logger.debug("Servo [%s] still in motion", servo)
    logger.debug('Thread stopped')


def set_pwm(servo, pos):
    """
    Controls an individual servo. This function also updates the config variable servo list.

    :param servo: Servo number ranging from 0 to 15.
    :param pos: Position range 100 to 500.
    :return: void
    """
    servo_threading = threading.Thread(target=servo_thread, args=([servo, pos]), daemon=True)
    servo_threading.setName('servo_thread')
    servo_threading.start()
    # if config.SERVO_MODULE:
    #     pca.set_pwm(servo, 0, pos)
    #     config.servo[servo] = pos
    return servo_threading


def set_pwm_init(servo, pos):
    """
    Controls an individual servo. This function also updates the config variable servo list.

    :param servo: Servo number ranging from 0 to 15.
    :param pos: Position range 100 to 500.
    :return: void
    """
    logger.debug("Initialize PWM on servo [%s], position [%s])", servo, pos)
    if not config.SERVO_MODULE:
        logger.info('Servo module DISABLED')
        return
    pca.set_pwm(servo, 0, pos)
    config.servo[servo] = pos


def mpu6050Test():
    while 1:
        accelerometer_data = sensor.get_accel_data()
        logger.debug('Accelerometer output (X=%f, Y=%f, Z=%f)', accelerometer_data['x'], accelerometer_data['y'],
                     accelerometer_data['x'])
        logger.debug('Accelerometer temperature: %s', sensor.get_temp())
        time.sleep(STEADY_DELAY)
        break


def robot_X(amp):
    """
    Legs are further apart when amp is 0, robot <body>
    When amp is 100, robot >body<

    Warning: Robot will loose balance if value is too high!

    :param amp: range(100,0)
    :return: void
    """
    wiggle = config.torso_w
    pos1 = int(config.torso_m - wiggle + 2 * wiggle * amp / 100)
    pos2 = int(config.torso_m - wiggle + 2 * wiggle * amp / 100)
    pos3 = int(config.torso_m2 + wiggle - 2 * wiggle * amp / 100)
    pos4 = int(config.torso_m2 + wiggle - 2 * wiggle * amp / 100)
    servo_multiplier(0, [pos1, pos2, pos3, pos4])


def robot_height(height, instant=0):
    """
    Blocking servo movement.
    Highest point 100
    Mid point 50
    lowest point 0

    :param instant: boolean is servo should move instantly or gradually
    :param height: range(100,0)
    :return: void
    """
    if not config.SERVO_MODULE or not config.servo_motion == [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]:
        return
    pos1 = int(config.lower_leg_l + (config.lower_leg_w * 2 / 100 * height))
    pos2 = int(config.lower_leg_h2 - (config.lower_leg_w * 2 / 100 * height))
    servo = 1
    if instant:
        set_pwm_init(servo, pos1)
        set_pwm_init(int(servo + 3), pos2)
        set_pwm_init(int(servo + 6), pos2)
        set_pwm_init(int(servo + 9), pos1)
    else:
        servo_multiplier(1, [pos1, pos2, pos2, pos1])


def servo_multiplier(initial_servo, pos):
    """
    A blocking function which controls 4 servos symmetrically. Servo address is calculated by adding 3 to initial
    servo address. Maximum of 4 servos will be controlled.

    :param initial_servo: first servo number
    :param pos: List of target positions
    """
    count = len(pos)
    if count > 4:
        logger.error('Function cannot handle more than 4 servos.')
        return
    SPEED = config.SPEED
    servo = []
    servo_pos = []
    for i in range(count):
        servo.append(initial_servo)
        servo_pos.append(config.servo[servo[i]])
        initial_servo += 3
        pass
    # servo = [initial_servo, initial_servo + 3, initial_servo + 6, initial_servo + 9]
    logger.debug('Controlling servo: %s', servo)
    # servo_pos = [config.servo[servo[0]], config.servo[servo[1]], config.servo[servo[2]], config.servo[servo[3]]]
    logger.debug('Getting initial position for servo: %s', servo_pos)
    for i in range(int((abs(pos[0] - config.servo[servo[0]])) / config.SPEED)):
        for x in range(count):
            if servo_pos[x] < pos[x]:
                servo_pos[x] += SPEED
            else:
                servo_pos[x] -= SPEED
        for x in range(count):
            pca.set_pwm(servo[x], 0, servo_pos[x])
    for i in range(count):
        # TO-DO May not be needed
        pca.set_pwm(servo[i], 0, servo_pos[i])
        config.servo[servo[i]] = servo_pos[i]
    logger.debug('Servo position after: %s', servo_pos)
    logger.debug('Servo position after: %s', config.servo)


def ctrl_range(input_value, max_genout, min_genout):
    """
    Normalize the input value between Max and Min.

    :param input_value: Any integer
    :param max_genout: Max value
    :param min_genout: Mix value
    :return: Returns a value between Max and Min
    """
    if input_value > max_genout:
        output_value = max_genout
    elif input_value < min_genout:
        output_value = min_genout
    else:
        output_value = input_value
    return int(output_value)


def robot_pitch_roll(pitch, roll, instant=0):  # Percentage wiggle
    """
    look up <- pitch -> look down.
    lean right <- roll -> lean left.

    default values are 0.

    :param instant: 1 = move instantly, 0 = animate movement
    :param pitch: range(-100, 100)
    :param roll: range(-100, 100)
    :return: void
    """
    logger.debug('Pitch=%s Roll=%s', pitch, roll)
    wiggle = config.lower_leg_w
    pos1 = ctrl_range((config.lower_leg_m - wiggle * pitch / 100 - wiggle * roll / 100), config.lower_leg_h,
                      config.lower_leg_l)
    pos2 = ctrl_range((config.lower_leg_m2 - wiggle * pitch / 100 + wiggle * roll / 100), config.lower_leg_h2,
                      config.lower_leg_l2)
    pos3 = ctrl_range((config.lower_leg_m2 + wiggle * pitch / 100 - wiggle * roll / 100), config.lower_leg_h2,
                      config.lower_leg_l2)
    pos4 = ctrl_range((config.lower_leg_m + wiggle * pitch / 100 + wiggle * roll / 100), config.lower_leg_h,
                      config.lower_leg_l)
    if instant:
        set_pwm_init(1, pos1)
        set_pwm_init(4, pos2)
        set_pwm_init(7, pos3)
        set_pwm_init(10, pos4)
    else:
        servo_multiplier(1, [pos1, pos2, pos3, pos4])


def robot_yaw(wiggle, yaw, instant=0):  # Percentage wiggle
    """
    look left <- yaw -> look right
    default value is 0

    Left = 100
    Right = -100

    :param instant: 1 = move instantly, 0 = animate movement
    :param wiggle: Constant servo range
    :param yaw: range (100, -100)
    :return: void
    """
    yaw = ctrl_range(yaw, 100, -100)
    logger.debug('Servo position before: %s', config.servo)
    pos1 = int(config.torso_m + wiggle * yaw / 100)
    pos2 = int(config.torso_m - wiggle * yaw / 100)
    pos3 = int(config.torso_m2 + wiggle * yaw / 100)
    pos4 = int(config.torso_m2 - wiggle * yaw / 100)
    # robot_X(config.DEFAULT_X)
    if instant:
        set_pwm_init(0, pos1)
        set_pwm_init(3, pos2)
        set_pwm_init(6, pos3)
        set_pwm_init(9, pos4)
    else:
        servo_multiplier(0, [pos1, pos2, pos3, pos4])


def robot_steady():
    global STEADY_DELAY
    """
    Reads accelerometer sensor data and send output to servos to level the robot

    :return: void
    """
    global X_fix_output, Y_fix_output
    try:
        accelerometer_data = sensor.get_accel_data()
        X = accelerometer_data['x']
        Y = accelerometer_data['y']
        logger.debug('Accelerometer raw data [X,Y] = %s, %s', X, Y)
        X = kalman_filter_X.kalman(X)
        Y = kalman_filter_Y.kalman(Y)
        logger.debug('Kalman filter output [X,Y] = %s, %s', X, Y)
        X_fix_output -= X_pid.GenOut(X - X_steady)
        Y_fix_output += Y_pid.GenOut(Y - Y_steady)
        X_fix_output = ctrl_range(X_fix_output, 100, -100)
        Y_fix_output = ctrl_range(Y_fix_output, 100, -100)
        logger.debug('Steady output = %s, %s', -X_fix_output, Y_fix_output)
        robot_pitch_roll(-X_fix_output, Y_fix_output, 1)
    except:
        logger.error('MPU6050 reading error.')
    time.sleep(STEADY_DELAY)


def servo_release():
    """
    Release all servos.
    :return: void
    """
    if not config.SERVO_MODULE:
        logger.info('Servo module DISABLED')
        return
    logger.info('Releasing servos...')
    pca.set_all_pwm(0, 0)


def servo_init():
    """
    Initialize all servos.
    A small twitch is required to command servos after release.
    :return: void
    """
    global torso_wiggle
    logger.info('Initializing all servos... ')
    wiggle = config.torso_w
    for i in range(0, 12):
        if i == 1 or i == 10:
            set_pwm_init(i, config.lower_leg_l - 2)
        if i == 4 or i == 7:
            set_pwm_init(i, config.lower_leg_h2 - 2)
        if i == 2 or i == 11:
            set_pwm_init(i, config.upper_leg_m - 2)
        if i == 5 or i == 8:
            set_pwm_init(i, config.upper_leg_m2 - 2)
        if i == 0 or i == 3:
            set_pwm_init(i, int(config.torso_m - wiggle + 2 * wiggle * (config.DEFAULT_X - 2) / 100))
        if i == 6 or i == 9:
            set_pwm_init(i, int(config.torso_m2 + wiggle - 2 * wiggle * (config.DEFAULT_X - 2) / 100))
        time.sleep(INIT_DELAY)
    for i in range(0, 12):
        if i == 1 or i == 10:
            set_pwm_init(i, config.lower_leg_l)
        if i == 4 or i == 7:
            set_pwm_init(i, config.lower_leg_h2)
        if i == 2 or i == 11:
            set_pwm_init(i, config.upper_leg_m)
        if i == 5 or i == 8:
            set_pwm_init(i, config.upper_leg_m2)
        if i == 0 or i == 3:
            set_pwm_init(i, int(config.torso_m - wiggle + 2 * wiggle * config.DEFAULT_X / 100))
        if i == 6 or i == 9:
            set_pwm_init(i, int(config.torso_m2 + wiggle - 2 * wiggle * config.DEFAULT_X / 100))
        time.sleep(INIT_DELAY)
    config.servo_init = config.servo.copy()
    logger.debug('Servo init: %s', config.servo_init)
    logger.debug('Servo status: %s', config.servo)
    logger.debug('Going to default height.')
    robot_height(config.height)


def robot_home():
    """
    Set robot into home position
    :return: void
    """
    logger.info('Servos to home position...')
    robot_X(config.DEFAULT_X)
    robot_pitch_roll(0, 0)
    robot_height(config.height)


def robot_balance(balance):
    logger.debug('Check servo for motion: %s', config.servo_motion)
    logger.debug('Servo status: %s', config.servo)
    if config.servo_motion == [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]:
        if balance == 'back':
            balance_center('side')
            balance_back()
        elif balance == 'front':
            balance_center('side')
            balance_front()
        elif balance == 'left':
            balance_center('y')
            balance_left()
        elif balance == 'right':
            balance_center('y')
            balance_right()
        elif balance == 'front_left':
            balance_front()
            balance_left()
        elif balance == 'front_right':
            balance_front()
            balance_right()
        elif balance == 'back_left':
            balance_back()
            balance_left()
        elif balance == 'back_right':
            balance_back()
            balance_right()
        else:
            balance_all()


def balance_center(direction):
    if direction == 'side':
        if config.servo[2] != config.servo_init[2]:
            pos1 = config.servo_init[2]
            pos2 = config.servo_init[5]
            pos3 = config.servo_init[8]
            pos4 = config.servo_init[11]
            servo_multiplier(2, [pos1, pos2, pos3, pos4])
    if direction == 'y':
        if config.servo[0] != config.servo_init[0]:
            pos1 = config.servo_init[0]
            pos2 = config.servo_init[3]
            pos3 = config.servo_init[6]
            pos4 = config.servo_init[9]
            servo_multiplier(0, [pos1, pos2, pos3, pos4])

def balance_all():
    balance_center('side')
    balance_center('y')


def balance_back():
    global torso_wiggle
    pos1 = config.servo_init[0] + torso_wiggle
    pos2 = config.servo_init[3] - torso_wiggle
    pos3 = config.servo_init[6] - torso_wiggle
    pos4 = config.servo_init[9] + torso_wiggle
    servo_multiplier(0, [pos1, pos2, pos3, pos4])


def balance_front():
    global torso_wiggle
    pos1 = config.servo_init[0] - torso_wiggle
    pos2 = config.servo_init[3] + torso_wiggle
    pos3 = config.servo_init[6] + torso_wiggle
    pos4 = config.servo_init[9] - torso_wiggle
    servo_multiplier(0, [pos1, pos2, pos3, pos4])


def balance_right():
    global toe_wiggle
    pos1 = config.servo_init[2] - toe_wiggle
    pos2 = config.servo_init[5] + toe_wiggle
    pos3 = config.servo_init[8] - toe_wiggle
    pos4 = config.servo_init[11] + toe_wiggle
    servo_multiplier(2, [pos1, pos2, pos3, pos4])


def balance_left():
    global toe_wiggle
    pos1 = config.servo_init[2] + toe_wiggle
    pos2 = config.servo_init[5] - toe_wiggle
    pos3 = config.servo_init[8] + toe_wiggle
    pos4 = config.servo_init[11] - toe_wiggle
    servo_multiplier(2, [pos1, pos2, pos3, pos4])


def move_direction(direction):
    if direction == 'forward':
        leg_up(2)
        pass


def leg_up(id):
    if id == 1:
        servo_multiplier(1, [int(config.lower_leg_l)])
    if id == 2:
        servo_multiplier(4, [int(config.lower_leg_h2)])
    if id == 3:
        servo_multiplier(7, [int(config.lower_leg_h)])
    if id == 4:
        servo_multiplier(10, [int(config.lower_leg_l2)])


def leg_down_forward(id):
    if id == 1:
        set_pwm(0, int(config.servo_init[0] + config.torso_w))
        set_pwm(1, int(config.lower_leg_h))
    if id == 2:
        # DOWN IN
        set_pwm(3, int(config.servo_init[3] - config.torso_w))
        set_pwm(4, int(config.lower_leg_l2))
    if id == 3:
        set_pwm(6, int(config.servo_init[6] - config.torso_w))
        set_pwm(7, int(config.lower_leg_l))
    if id == 4:
        set_pwm(9, int(config.servo_init[9] + config.torso_w))
        set_pwm(10, int(config.lower_leg_h2))


def leg_down_backward(id):
    if id == 1:
        set_pwm(0, int(config.servo_init[0] - config.torso_w))
        set_pwm(1, int(config.lower_leg_h))
    if id == 2:
        # DOWN IN
        set_pwm(3, int(config.servo_init[3] + config.torso_w))
        set_pwm(4, int(config.lower_leg_l2))
    if id == 3:
        set_pwm(6, int(config.servo_init[6] + config.torso_w))
        set_pwm(7, int(config.lower_leg_l))
    if id == 4:
        set_pwm(9, int(config.servo_init[9] - config.torso_w))
        set_pwm(10, int(config.lower_leg_h2))


def leg_down_in(id):
    if id == 1:
        set_pwm(2, int(config.servo_init[2] + config.upper_leg_w))
        set_pwm(1, int(config.lower_leg_h))
    if id == 2:
        # DOWN IN
        set_pwm(5, int(config.servo_init[5] - config.upper_leg_w))
        set_pwm(4, int(config.lower_leg_l2))
    if id == 3:
        set_pwm(8, int(config.servo_init[8] - config.upper_leg_w))
        set_pwm(7, int(config.lower_leg_l))
    if id == 4:
        set_pwm(11, int(config.servo_init[11] + config.upper_leg_w))
        set_pwm(10, int(config.lower_leg_h2))


def leg_down_out(id):
    if id == 1:
        set_pwm(2, int(config.servo_init[2] - config.upper_leg_w))
        set_pwm(1, int(config.lower_leg_h))
    if id == 2:
        # DOWN IN
        set_pwm(5, int(config.servo_init[5] + config.upper_leg_w))
        set_pwm(4, int(config.lower_leg_l2))
    if id == 3:
        set_pwm(8, int(config.servo_init[8] + config.upper_leg_w))
        set_pwm(7, int(config.lower_leg_l))
    if id == 4:
        set_pwm(11, int(config.servo_init[11] - config.upper_leg_w))
        set_pwm(10, int(config.lower_leg_h2))


if __name__ == '__main__':
    log_level = logging.DEBUG
    if len(logging.getLogger().handlers) == 0:
        # Initialize the root logger only if it hasn't been done yet by a
        # parent module.
        logging.basicConfig(
            format='%(asctime)s %(levelname)7s %(thread)5d --- [%(threadName)16s] %(funcName)-20s: %(message)s')
        logger = logging.getLogger(__name__)
        logger.setLevel(log_level)
        # logger.propagate = False
    servo_init()
    robot_balance('left')
    time.sleep(0.5)
    robot_balance('right')
    time.sleep(0.5)
    robot_balance('center')
    time.sleep(0.5)
    robot_balance('front')

    leg_up(2)
    '''
    try:
        if sys.argv.__len__() > 1 and sys.argv[1] == 'test':
            while 1:
                time.sleep(STEADY_DELAY)
                mpu6050Test()
        else:
            logger.info("Starting move...")
            servo_init()
            while 1:
                robot_steady()
                time.sleep(STEADY_DELAY)
                # break
        mpu6050Test()

    except KeyboardInterrupt:
        servo_release()
    '''
