#!/usr/bin/env/python
# File name   : server.py
# E-mail      : sect16@gmail.com
# Author      : Chin Pin Hon
# Date        : 29/11/2019

import logging
import os
import signal
import socket
import subprocess
import sys
import threading
import time
import traceback

import psutil

import Gamepad
import camera as cam
import config
import led
import move
import power_module as pm
import speak_dict
import steps
import switch
import ultra
from speak import speak

logger = logging.getLogger(__name__)
# Socket connection sequence. Bind socket to port, create socket, get client address/port, get server address/port.
client_address = None
server_address = None
led = led.Led()
if config.CAMERA_MODULE:
    camera = cam.Camera()
kill_event = threading.Event()
ultra_event = threading.Event()
steadyMode = 0
direction_command = 'no'
turn_command = 'no'
gait = 'stable'
ws_G = 0
ws_R = 0
ws_B = 0
led_status = False
audio_pid = None
power = None

last_hat_x = 0
last_hat_y = 0
last_left_x = 0
last_left_y = 0
last_right_x = 0
last_right_y = 0
last_lt = 0
last_rt = 0
last_lb = 0
last_rb = 0


def ap_thread():
    os.system("sudo create_ap wlan0 eth0 Wally bianbian")


def get_cpu_temp():
    """ Return CPU temperature """
    result = 0
    path = "/sys/class/thermal/thermal_zone0/temp"
    with open(path, 'r') as tmp_file:
        for line in tmp_file:
            result = line
    result = float(result) / 1000
    result = round(result, 1)
    return str(result)


def get_soc_temp():
    """ Returns the temperature of the SoC as measured by the on-board temperature sensor."""
    res = os.popen('/opt/vc/bin/vcgencmd measure_temp').readline()
    return res.replace("temp=", "")


def get_cpu_use():
    """ Return CPU usage using psutil"""
    cpu_cent = psutil.cpu_percent()
    return str(cpu_cent)


def get_ram_info():
    """ Return RAM usage using psutil """
    ram_cent = psutil.virtual_memory()[2]
    return str(ram_cent)


def thread_isAlive(*args):
    """
    This function searches for the thread name defined using threading.Thread.setName() function.
    :param args: Name of the thread. Can be multiple.
    :return: Returns a boolean indicating if any of the threads was found.
    """
    logger.debug('Checking for existence of threads: %s', args)
    for thread_name in args:
        logger.debug('Looking for thread: ' + thread_name)
        lst = threading.enumerate()
        for x in lst:
            if x.name == thread_name:
                logger.info('%s is active.', x)
                return True
    logger.info('No thread found.')
    return False


def ultra_send_client(event):
    """
    This function is intended to be run as a thread. It sends ultrasonic sensor reading to the client and
    camera function.
    """
    REFRESH_RATE = 0.5
    logger.info('Thread started')
    ultra_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Set connection value for socket
    ultra_socket.connect((client_address, config.ULTRA_PORT))
    logger.info('Connected to client address (\'%s\', %i)', client_address, config.ULTRA_PORT)
    while event.is_set():
        try:
            ultra_socket.send(str(' ' + round(ultra.checkdist(), 2)).encode())
            if config.CAMERA_MODULE:
                camera.UltraData(round(ultra.checkdist(), 2))
            time.sleep(REFRESH_RATE)
        except:
            logger.error('Exception: %s', traceback.format_exc())
            break
    ultra_event.clear()
    logger.info('Thread stopped')


def info_thread(event):
    """
    This function is intended to be run as a thread. It sends robot statistics to the client server each second. It
    also implements a reconnect procedure in case the connection is dropped or an exception occurs.
    :param event: Terminates when event is set.
    """
    global power, client_address
    SOCKET_TIMEOUT = 5
    SOCKET_RETRY = 5
    connected = False
    logger.info('Thread started')
    while not event.is_set():
        if not connected:
            try:
                info_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Set connection value for socket
                info_socket.settimeout(SOCKET_TIMEOUT)
                info_socket.connect((client_address, config.INFO_PORT))
                logger.info('Connected to client address (\'%s\', %i)', client_address, config.INFO_PORT)
                connected = True
            except:
                logger.error('Exception: %s', traceback.format_exc())
                logger.error('Unable to connect to client info socket')
                connected = False
                time.sleep(SOCKET_RETRY)
                pass
        elif connected:
            time.sleep(config.INA219_POLLING)
            try:
                message = ' ' + get_cpu_temp() + ' ' + get_cpu_use() + ' ' + get_ram_info()
                if config.POWER_MODULE:
                    message += ' {0:0.2f}V'.format(power[0]) + ' {0:0.2f}mA'.format(
                        power[1])
                else:
                    message += ' - -'
                if config.GYRO_MODULE:
                    message += ' {0:0.1f}'.format(move.sensor.get_temp() + config.OFFSET_AMBIENT)
                else:
                    message += ' -'
                logger.debug('Info message content = ' + message)
                info_socket.send(message.encode())
            except BrokenPipeError:
                pass
            except TimeoutError:
                pass
            except:
                logger.error('Exception: %s', traceback.format_exc())
                try:
                    info_socket.close()
                except:
                    logger.error('Exception: %s', traceback.format_exc())
                    pass
                connected = False
                time.sleep(SOCKET_RETRY)
                pass
    logger.info('Thread stopped')


def connect():
    """
    This function starts the main robot listener and waits for the client to connect.
    """
    global server_address, tcp_server_socket, tcp_server, client_address
    while True:
        try:
            tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            tcp_server.bind(('', config.SERVER_PORT))
            # Start server,waiting for client
            tcp_server.listen(5)
            logger.info('Waiting for client connection...')
            led.color_set('cyan')
            led.mode_set(1)
            tcp_server_socket, client_address = tcp_server.accept()
            server_address = tcp_server_socket.getsockname()[0]
            # Timeout in seconds
            tcp_server_socket.settimeout(config.LISTENER_TIMEOUT)
            logger.info('Connected from %s', client_address)
            client_address = client_address[0]
            break
        except KeyboardInterrupt:
            logger.error('Exception while waiting for connection: %s', traceback.format_exc())
            kill_event.set()
            led.colorWipe([0, 0, 0])
            sys.exit()
            pass
        except:
            logger.error('Exception while waiting for connection: %s', traceback.format_exc())
            kill_event.set()
            led.colorWipe([0, 0, 0])
            pass


def disconnect():
    """
    This function shutdown all threads and performs cleanup function ensuring all thread has exited gracefully.
    It is meant to be blocking and not threaded to ensure all threads has been terminated before continuing.
    """
    global tcp_server_socket, tcp_server, kill_event
    logger.info('Disconnecting and termination threads.')
    speak(speak_dict.disconnect)
    kill_event.set()
    led.colorWipe([0, 0, 0])
    switch.set_all_switch_off()
    switch.destroy()
    time.sleep(0.5)
    # tcp_server.close()
    tcp_server_socket.close()
    move.robot_height(0)
    logger.info('Waiting for threads to finish.')
    while thread_isAlive('led_thread', 'camera_thread', 'info_thread', 'stream_thread',
                         'speak_thread', 'ultra_thread', 'ina219_thread',
                         'move_thread'):
        time.sleep(1)
    # move.servo_release()


def listener_thread(event):
    """
    This in the main listener thread loop which receives all commands from the client.
    :param event: Terminates when event is set.
    """
    logger.info('Starting listener thread...')
    global tcp_server_socket
    error_count = 0
    data = ''
    while not event.is_set():
        try:
            data = str(tcp_server_socket.recv(config.BUFFER_SIZE).decode())
        except socket.timeout:
            logger.warning('Listener socket timed out: ' + traceback.format_exc())
            data = ''
        except socket.error:
            logger.warning('Connection exception: ' + traceback.format_exc())
        if error_count >= config.LISTENER_MAX_ERROR:
            logger.error('Maximum listener error count reached, terminating thread.')
            return
        if not data:
            error_count += 1
            logger.warning('NULL message or no KEEPALIVE message received, error count: %s/%s', error_count,
                           config.LISTENER_MAX_ERROR)
            continue
        elif '|ACK|' in data:
            logger.debug('ACK message received')
            continue
        else:
            logger.info('Received data on tcp socket: %s', data)
            error_count = 0
            for message in data.split(';'):
                if message.__len__() != 0:
                    message_processor(message)


def message_processor(data):
    """
    This functions interprets the received client message and calls the relevant functions.
    :param data: client message
    :return: void
    """
    global camera, steadyMode, direction_command, turn_command, gait, ws_G, ws_R, ws_B, audio_pid, kill_event
    if 'wsR' in data:
        try:
            set_R = data.split()
            ws_R = int(set_R[1])
            led.colorWipe([ws_G, ws_R, ws_B])
        except:
            logger.error('Exception: %s', traceback.format_exc())
            pass
    elif 'wsG' in data:
        try:
            set_G = data.split()
            ws_G = int(set_G[1])
            led.colorWipe([ws_G, ws_R, ws_B])
        except:
            logger.error('Exception: %s', traceback.format_exc())
            pass
    elif 'wsB' in data:
        try:
            set_B = data.split()
            ws_B = int(set_B[1])
            led.colorWipe([ws_G, ws_R, ws_B])
        except:
            logger.error('Exception: %s', traceback.format_exc())
            pass
    elif 'Ultrasonic' == data:
        if config.ULTRA_MODULE:
            tcp_server_socket.send(' Ultrasonic'.encode())
            ultra_event.set()
            ultra_threading = threading.Thread(target=ultra_send_client, args=([ultra_event]), daemon=True)
            ultra_threading.setName('ultra_thread')
            ultra_threading.start()
    elif 'Ultrasonic_end' == data:
        ultra_event.clear()
        tcp_server_socket.send(' Ultrasonic_end'.encode())
    elif 'stream_audio' == data:
        global server_address
        if audio_pid is None:
            logger.info('Audio streaming server starting...')
            audio_pid = subprocess.Popen([
                'cvlc alsa://' + config.AUDIO_INPUT + ' :live-caching=50 --sout "#standard{access=http,mux=ogg,dst='
                + str(server_address) + ':' + str(config.AUDIO_PORT) + '}"'], shell=True, preexec_fn=os.setsid)
        else:
            logger.info('Audio streaming server already started.')
        tcp_server_socket.send(' stream_audio'.encode())
    elif 'stream_audio_end' == data:
        if audio_pid is not None:
            try:
                os.killpg(os.getpgid(audio_pid.pid), signal.SIGTERM)  # Send the signal to all the process groups
                audio_pid = None
            except:
                logger.error('Unable to kill audio stream.')
        tcp_server_socket.send(' stream_audio_end'.encode())
    elif 'start_video' == data:
        config.VIDEO_OUT = True
        tcp_server_socket.send(' start_video'.encode())
    elif 'stop_video' == data:
        config.VIDEO_OUT = False
        tcp_server_socket.send(' stop_video'.encode())
    elif 'FindColor' == data:
        led.mode_set(1)
        camera.FindColor(1)
        tcp_server_socket.send(' FindColor'.encode())
    elif 'WatchDog' == data:
        led.mode_set(1)
        camera.WatchDog(1)
        tcp_server_socket.send(' WatchDog'.encode())
    elif 'Switch_1_on' == data:
        switch.switch(1, 1)
        tcp_server_socket.send(' Switch_1_on'.encode())
    elif 'Switch_1_off' == data:
        switch.switch(1, 0)
        tcp_server_socket.send(' Switch_1_off'.encode())
    elif 'Switch_2_on' == data:
        switch.switch(2, 1)
        tcp_server_socket.send(' Switch_2_on'.encode())
    elif 'Switch_2_off' == data:
        switch.switch(2, 0)
        tcp_server_socket.send(' Switch_2_off'.encode())
    elif 'Switch_3_on' == data:
        switch.switch(3, 1)
        tcp_server_socket.send(' Switch_3_on'.encode())
    elif 'Switch_3_off' == data:
        switch.switch(3, 0)
        tcp_server_socket.send(' Switch_3_off'.encode())
    elif 'disconnect' == data:
        tcp_server_socket.send(' disconnect'.encode())
        kill_event.set()
    elif 'steady' == data:
        led.mode_set(1)
        led.color_set('blue')
        steadyMode = 1
        tcp_server_socket.send(' steady'.encode())
    elif 'func_end' == data:
        led.mode_set(0)
        camera.FindColor(0)
        camera.WatchDog(0)
        steadyMode = 0
        move.robot_home()
        tcp_server_socket.send(' func_end'.encode())
    elif 'forward' == data:
        direction_command = 'forward'
    elif 'backward' == data:
        direction_command = 'backward'
    elif 'direction_stop' in data:
        direction_command = 'stop'
    elif 'left' == data:
        turn_command = 'left'
    elif 'right' == data:
        turn_command = 'right'
    elif 'move_left_side' == data:
        direction_command = 'c_left'
    elif 'move_right_side' == data:
        direction_command = 'c_right'
    elif 'turn_stop' in data:
        turn_command = 'stop'
    elif 'balance_' in data or 'move_' in data:
        # Ignore balance commands when robot servos not initialized and idle.
        if not len(config.servo_init) == 12 or not direction_command == 'no' or not turn_command == 'no':
            logger.warning('Ignoring command, robot not idle! direction_command: %s turn_command: %s',
                           direction_command, turn_command)
            return
        elif 'move_head_up' == data:
            move.robot_pitch_roll(-100, 0)
        elif 'move_head_down' == data:
            move.robot_pitch_roll(100, 0)
        elif 'move_head_home' == data:
            move.robot_home()
        elif 'move_low' == data:
            move.robot_height(0)
        elif 'move_high' == data:
            move.robot_height(100)
        elif 'move_head_left' == data:
            move.robot_yaw(100)
        elif 'move_head_right' == data:
            move.robot_yaw(-100)
        elif 'move_roll_left' == data:
            move.robot_pitch_roll(0, 100)
        elif 'move_roll_right' == data:
            move.robot_pitch_roll(0, -100)
        elif 'balance_front' == data:
            move.robot_balance('front')
        elif 'balance_back' == data:
            move.robot_balance('back')
        elif 'balance_left' == data:
            move.robot_balance('left')
        elif 'balance_right' == data:
            move.robot_balance('right')
        elif 'balance_front_left' == data:
            move.robot_balance('front_left')
        elif 'balance_front_right' == data:
            move.robot_balance('front_right')
        elif 'balance_center' == data:
            move.robot_balance('center')
        elif 'balance_back_left' == data:
            move.robot_balance('back_left')
        elif 'balance_back_right' == data:
            move.robot_balance('back_right')
        elif 'move_head_pitch' in data:
            logger.debug('Received set head pitch')
            try:
                value = int(data.split(':', 2)[1])
                move.robot_pitch_roll(int(value * -1), 0)
            except:
                logger.error('Error setting head pitch: %s\n%s', data, traceback.format_exc())
                pass
        elif 'move_head_yaw' in data:
            logger.debug('Received set head pitch')
            try:
                value = int(data.split(':', 2)[1])
                move.robot_yaw(int(value))
            except:
                logger.error('Error setting head yaw: %s\n%s', data, traceback.format_exc())
                pass
        elif 'move_height' in data:
            logger.debug('Received set height')
            try:
                value = int(data.split(':', 2)[1])
                move.robot_height(int(value))
            except:
                logger.error('Error setting head yaw: %s\n%s', data, traceback.format_exc())
                pass
    elif 'speed:' in data:
        logger.debug('Received set servo speed')
        try:
            value = int(data.split(':', 2)[1])
            if value > 0:
                config.SPEED = value
        except:
            logger.error('Error setting servo speed: %s\n%s', data, traceback.format_exc())
            pass
    elif 'gait:' in data:
        if gait == 'stable':
            logger.info('Gait changed to trot')
            speak(speak_dict.name + ' will run')
            gait = 'trot'
        else:
            logger.info('Gait changed to stable')
            speak(speak_dict.name + ' will walk')
            gait = 'stable'
        pass
    elif 'light:' in data:
        # logger.debug('Received flash light intensity %s', data)
        try:
            value = int(data.split(':', 2)[1])
            # The PCA9685 IC is used to generate a stable PWM signal to the L298P IC in order to control
            # flash light LED brightness.
            move.pca.set_pwm(15, 0, int(4096 / 100 * (value - 2)))
            switch.channel_B(value)
        except:
            logger.error('Exception: %s', traceback.format_exc())
            pass
    elif 'espeak:' in data:
        logger.info('Speaking command received')
        value = str(data.split(':', 2)[1])
        speak(value)
        pass
    else:
        logger.warning('Unknown message received!')


def ina219_thread(event):
    """
    This thread read INA219 power statistics each second and stores them in a global variable. It also monitors the
    voltage for overload, low and critical voltages. It reads voltage threshold from the global configuration.
    VOLTAGE_CHECK_SECS defines the frequency in seconds to check for low and critical battery voltages. Over voltage
    is checked each time sensor is read. Default sensor reading is every 1 second.
    VOLTAGE_OVERLOAD defines the maximum input voltage.
    VOLTAGE_WARN battery low voltage threshold.
    VOLTAGE_SHUTDOWN battery critical voltage threshold. Shutdown is initiated when triggered.
    INA219_POLL sensor read rate.
    :param event: Terminates when event is set.
    :return: void
    """
    global power
    logger.info('Thread started')
    ina219 = pm.PowerModule()
    interval = config.VOLTAGE_CHECK_SECS
    INA219_POLL = config.INA219_POLLING
    while not event.is_set():
        time.sleep(INA219_POLL)
        interval += INA219_POLL
        try:
            power = ina219.read_ina219()
        except:
            pass
        if power[0] > config.VOLTAGE_OVERLOAD:
            logger.critical(
                'Maximum input voltage exceeded by {0:0.2f} volts, reduce immediately to prevent damage!'.format(
                    float(power[0] - config.VOLTAGE_OVERLOAD)))
            speak('Maximum input voltage exceeded by {0:0.2f} volts, reduce immediately to prevent damage!'.format(
                float(power[0] - config.VOLTAGE_OVERLOAD)))
            pass
        elif interval >= config.VOLTAGE_CHECK_SECS:
            interval = 0
            if power[0] < config.VOLTAGE_WARN:
                speak('Battery voltage is {0:0.2f} volts, please recharge!'.format(power[0]))
                logger.warning('Battery voltage low (%s), please recharge!', power[0])
            elif power[0] < config.VOLTAGE_SHUTDOWN:
                speak('Battery voltage is {0:0.2f} volts, battery critical, shutting down now!'.format(power[0]))
                time.sleep(3)
                logger.critical('Battery voltage critical (%s), shutting down!', power[0])
                command = "/usr/bin/sudo /sbin/shutdown now"
                import subprocess
                subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    logger.info('Thread stopped')


def move_thread(event):
    """
    This thread manages which servos to move at each step.
    :param event: Terminates when event is set.
    :return: void
    """
    logger.info('Thread started')
    global direction_command, turn_command
    last_direction_command = 'stop'
    last_turn_command = 'stop'
    step = 0
    while not event.is_set():
        if not steadyMode:
            if (direction_command == 'forward' or direction_command == 'backward') and turn_command == 'no':
                if gait == 'stable':
                    last_direction_command, last_turn_command, step = forward(last_direction_command, last_turn_command,
                                                                              step)
                elif gait == 'trot':
                    pass
                continue
            elif (direction_command == 'c_right' or direction_command == 'c_left') and turn_command == 'no':
                if gait == 'stable':
                    last_direction_command, last_turn_command, step = crab(last_direction_command, last_turn_command,
                                                                           step)
                elif gait == 'trot':
                    pass
                continue
            elif direction_command == 'no' and (turn_command == 'left' or turn_command == 'right'):
                if gait == 'stable':
                    last_direction_command, last_turn_command, step = turn(last_direction_command, last_turn_command,
                                                                           step)
                elif gait == 'trot':
                    pass
                continue
            elif turn_command == 'stop' or direction_command == 'stop':
                move.robot_height(50)
                move.robot_balance('center')
                # Reset changed torso wiggle
                move.torso_wiggle = config.torso_w - ((config.DEFAULT_X - 50) * 2 / 100 * config.torso_w)
                direction_command = 'no'
                turn_command = 'no'
                last_direction_command = 'no'
                last_turn_command = 'no'
                pass

            time.sleep(0.5)
            step = 0
            pass
        else:
            move.robot_steady()
    logger.info('Thread stopped')


def forward(last_direction_command, last_turn_command, step):
    global direction_command, turn_command
    # Initialize variables
    if direction_command == 'forward':
        leg = [2, 1, 4, 3]
        balance = ['front_right', 'front_left']
    elif direction_command == 'backward':
        leg = [3, 4, 1, 2]
        balance = ['back_left', 'back_right']
    if not last_direction_command == direction_command:
        move.robot_height(100)
        last_direction_command = direction_command
    logger.debug('Execute step: %s', steps.move_list[step])
    exec(steps.move_list[step])
    logger.debug('Finished step: %s', steps.move_list[step])
    step += 1
    if step == len(steps.move_list):
        step = 0
    return last_direction_command, last_turn_command, step


def crab(last_direction_command, last_turn_command, step):
    global direction_command, turn_command
    # Initialize variables
    if direction_command == 'c_left':
        leg = [2, 4, 1, 3]
        balance = 'front_left'
    elif direction_command == 'c_right':
        leg = [4, 2, 3, 1]
        balance = 'front_right'
    if not last_direction_command == direction_command:
        move.torso_wiggle = 50
        last_direction_command = direction_command
    exec(steps.crab_list[step])
    step += 1
    if step == len(steps.crab_list):
        step = 0
    return last_direction_command, last_turn_command, step


def turn(last_direction_command, last_turn_command, step):
    global direction_command, turn_command
    # Initialize variables
    if turn_command == 'left':
        leg = [1, 2, 4, 3]
        balance = ['back_right', 'front_left']
    elif turn_command == 'right':
        leg = [3, 4, 2, 1]
        balance = ['back_left', 'front_right']
    if not last_turn_command == turn_command:
        move.torso_wiggle = 50
        last_turn_command = turn_command
        move.robot_height(100)
    else:
        exec(steps.turn_list[step])
        step += 1
        if step == len(steps.turn_list):
            step = 0
    return last_direction_command, last_turn_command, step


def toggle_led():
    """
    Function toggles the front LED light on/off.
    :return:
    """
    global led_status
    if not led_status:
        move.pca.set_pwm(15, 0, int(4096 / 100 * (config.led - 2)))
        switch.channel_B(config.led)
        led_status = True
    else:
        switch.channel_B(0)
        led_status = False


def on_axis_moved(gamepad):
    global turn_command, direction_command, last_hat_x, last_hat_y, last_left_x, last_left_y, last_right_x, last_right_y, last_lt, last_rt, last_lb, last_rb
    hat_x = gamepad.axis('HAT-X')
    hat_y = gamepad.axis('HAT-Y')
    left_x = gamepad.axis('LEFT-X')
    left_y = gamepad.axis('LEFT-Y')
    right_x = gamepad.axis('RIGHT-X')
    right_y = gamepad.axis('RIGHT-Y')
    lt = gamepad.axis('LT')
    rt = gamepad.axis('RT')
    lb = gamepad.isPressed('LB')
    rb = gamepad.isPressed('RB')
    if right_x + right_y == 0 and not (last_hat_x == hat_x and last_hat_y == hat_y and last_lb == lb and last_rb == rb):
        last_hat_x = hat_x
        last_hat_y = hat_y
        last_lb = lb
        last_rb = rb
        if turn_command == 'no' and direction_command == 'no':
            # logger.debug('Axis HAT-X, HAT-Y moved to %s, %s', hat_x, hat_y)
            if hat_x < -0.9:
                logger.debug('Robot move left received')
                turn_command = 'left'
            elif hat_x > 0.9:
                logger.debug('Robot move right received')
                turn_command = 'right'
            elif hat_y < -0.9:
                logger.debug('Robot move forward received')
                direction_command = 'forward'
            elif hat_y > 0.9:
                logger.debug('Robot move backward received')
                direction_command = 'backward'
            elif lb:
                direction_command = 'c_left'
                pass
            elif rb:
                direction_command = 'c_right'
                pass
    if hat_x + hat_y == 0 and not (last_right_x == right_x and last_right_y == right_y):
        last_right_x = right_x
        last_right_y = right_y
        logger.debug('Axis RIGHT-X, RIGHT-Y moved to %s, %s', right_x, right_y)
        move.robot_yaw(int(-right_x * 100))
        move.robot_pitch_roll(int(-right_y * 100), 0)
        pass
    if (abs(hat_x) < 0.9 and abs(hat_y) < 0.9) and not (lb or rb):
        if (not turn_command == 'stop' and not turn_command == 'no') or (
                not direction_command == 'stop' and not direction_command == 'no'):
            logger.debug('Controller stop triggered')
            turn_command = 'stop'
            direction_command = 'stop'
    if not (last_lt == lt and last_rt == rt):
        last_lt = lt
        last_rt = rt
        logger.debug('Axis LT, RT moved to %s, %s', lt, rt)
        height = 50 + -int((lt + 1) * 25) + int((rt + 1) * 25)
        move.robot_height(height)
    if hat_x + hat_y == 0 and not (last_left_x == left_x and last_left_y == left_y):
        last_left_x = left_x
        last_left_y = left_y
        logger.debug('Axis LEFT-X, LEFT-Y moved to %s, %s', left_x, left_y)
        if left_x == 0 and left_y == 0:
            move.robot_balance('center')
        elif left_x < -0.8 and left_y < -0.8:
            move.robot_balance('left_front')
        elif left_x > 0.8 and left_y > 0.8:
            move.robot_balance('right_back')
        elif left_x < -0.8 and left_y > 0.8:
            move.robot_balance('left_back')
        elif left_x > 0.8 and left_y < -0.8:
            move.robot_balance('right_front')
        elif left_x == -1:
            move.robot_balance('left')
        elif left_x == 1:
            move.robot_balance('right')
        elif left_y == 1:
            move.robot_balance('back')
        elif left_y == -1:
            move.robot_balance('front')
        pass


def joystick_thread(event):
    """
    Start listener for joystick connection.
    :param event: Terminates when event is set.
    """
    logger.info('Thread started')
    while not event.is_set():
        gamepad = None
        # Wait for a connection
        try:
            logger.info('Waiting for Xbox360 joystick to be connected...')
            while not Gamepad.available():
                time.sleep(1.0)
                if event.is_set():
                    logger.info('Thread stopped')
                    return
            gamepadType = Gamepad.Xbox360
            gamepad = gamepadType()
            # Start the background updating
            gamepad.startBackgroundUpdates()
            # Register the callback functions
            gamepad.addButtonReleasedHandler('A', toggle_led)
            logger.info('Xbox360 joystick connected')
            config.SPEED = 5
            while not event.is_set() and gamepad.isConnected():
                on_axis_moved(gamepad)
                time.sleep(config.CONTROLLER_POLL)
        except:
            logger.error('Exception Xbox360 joystick: ', traceback.format_exc())
        finally:
            # Ensure the background thread is always terminated when we are done
            if gamepad is not None:
                gamepad.disconnect()
    logger.info('Thread stopped')


def main():
    logger.info('Starting server.')
    global kill_event
    switch.switchSetup()
    switch.set_all_switch_off()
    kill_event.clear()
    if config.POWER_MODULE:
        ina219_threading = threading.Thread(target=ina219_thread, args=[kill_event], daemon=True)
        ina219_threading.setName('ina219_thread')
        ina219_threading.start()
    # led_threading = threading.Thread(target=led.led_thread, args=[kill_event], daemon=True)
    # led_threading.setName('led_thread')
    # led_threading.start()
    move.servo_init()
    moving_threading = threading.Thread(target=move_thread, args=[kill_event], daemon=True)
    moving_threading.setName('move_thread')
    moving_threading.start()
    joystick_threading = threading.Thread(target=joystick_thread, args=[kill_event], daemon=True)
    joystick_threading.setName('joystick_thread')
    joystick_threading.start()
    connect()
    speak(speak_dict.connect)
    try:
        if config.CAMERA_MODULE:
            global camera
            camera_thread = threading.Thread(target=camera.capture_thread, args=[kill_event], daemon=True)
            camera_thread.setName('camera_thread')
            camera_thread.start()
        info_threading = threading.Thread(target=info_thread, args=[kill_event], daemon=True)
        info_threading.setName('info_thread')
        info_threading.start()
        listener_thread(kill_event)
    except:
        logger.error('Exception: %s', traceback.format_exc())
    disconnect()


if __name__ == "__main__":
    try:
        while True:
            main()
    except KeyboardInterrupt:
        pass
