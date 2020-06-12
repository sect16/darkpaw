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

import camera as cam
import config
import led
import move
import power_module as pm
import speak_dict
import switch
import ultra
from speak import speak

logger = logging.getLogger(__name__)
# Socket connection sequence. Bind socket to port, create socket, get client address/port, get server address/port.
tcp_server = None
tcp_server_socket = None
client_address = None
server_address = None
led = led.Led()
if config.CAMERA_MODULE:
    camera = cam.Camera()
kill_event = threading.Event()
ultra_event = threading.Event()
steadyMode = 0
wiggle = 100
direction_command = 'no'
turn_command = 'no'


def ap_thread():
    os.system("sudo create_ap wlan0 eth0 Wally bianbian")


def get_cpu_temp():
    """ Return CPU temperature """
    result = 0
    mypath = "/sys/class/thermal/thermal_zone0/temp"
    with open(mypath, 'r') as mytmpfile:
        for line in mytmpfile:
            result = line
    result = float(result) / 1000
    result = round(result, 1)
    return str(result)


def get_gpu_temp():
    """ Return GPU temperature as a character string"""
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


def get_swap_info():
    """ Return swap memory  usage using psutil """
    swap_cent = psutil.swap_memory()[3]
    return str(swap_cent)


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
                logger.debug('Found %s is active.', x)
                return True
    logger.debug('No threads found.')
    return False


def ultra_send_client(event):
    logger.info('Thread started')
    ultra_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Set connection value for socket
    ultra_socket.connect((client_address, config.ULTRA_PORT))
    logger.info('Connected to client address (\'%s\', %i)', client_address, config.ULTRA_PORT)
    while event.is_set():
        try:
            ultra_socket.send(str(round(ultra.checkdist(), 2)).encode())
            time.sleep(0.5)
            camera.UltraData(round(ultra.checkdist(), 2))
            time.sleep(0.2)
        except:
            logger.error('Exception: %s', traceback.format_exc())
            break
    time.sleep(0.5)
    ultra_event.clear()
    logger.info('Thread stopped')


def info_thread(event):
    logger.info('Thread started')
    info_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Set connection value for socket
    info_socket.connect((client_address, config.INFO_PORT))
    logger.info('Connected to client address (\'%s\', %i)', client_address, config.INFO_PORT)
    if config.POWER_MODULE:
        ina219 = pm.PowerModule()
    while not event.is_set():
        try:
            message = get_cpu_temp() + ' ' + get_cpu_use() + ' ' + get_ram_info()
            if config.POWER_MODULE:
                power = ina219.read_ina219()
                message += ' {0:0.2f}V'.format(power[0] + config.OFFSET_VOLTAGE) + ' {0:0.2f}mA'.format(
                    power[1] + config.OFFSET_CURRENT)
            else:
                message += ' - -'
            if config.GYRO_MODULE:
                message += ' {0:0.1f}'.format(move.sensor.get_temp() + config.OFFSET_AMBIENT)
            else:
                message += ' -'
            info_socket.send(message.encode())
            time.sleep(1)
        except BrokenPipeError:
            pass
        except:
            logger.error('Exception: %s', traceback.format_exc())
            pass
    logger.info('Thread stopped')


def connect():
    global server_address, tcp_server_socket, tcp_server, client_address
    while True:
        try:
            tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            tcp_server.bind(('', config.SERVER_PORT))
            # Start server,waiting for client
            tcp_server.listen(5)
            logger.info('Waiting for connection...')
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
    tcp_server.close()
    tcp_server_socket.close()
    move.robot_height(0)
    logger.info('Waiting for threads to finish.')
    while thread_isAlive('led_thread', 'camera_thread', 'info_thread', 'stream_thread',
                         'speak_thread', 'ultra_thread',
                         'move_thread'):
        time.sleep(1)
    logger.info('All threads terminated.')
    # move.servo_release()


def listener_thread(event):
    logger.info('Starting listener thread...')
    global camera, tcp_server_socket, steadyMode, direction_command, turn_command
    ws_G = 0
    ws_R = 0
    ws_B = 0
    audio_pid = None
    error_count = 0
    while not event.is_set():
        try:
            data = str(tcp_server_socket.recv(config.BUFFER_SIZE).decode())
        except socket.timeout:
            logger.warning('Listener socket timed out')
            data = ''
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
            tcp_server_socket.send(('Ultrasonic').encode())
            ultra_event.set()
            ultra_threading = threading.Thread(target=ultra_send_client, args=([ultra_event]), daemon=True)
            ultra_threading.setName('ultra_thread')
            ultra_threading.start()
        elif 'Ultrasonic_end' == data:
            ultra_event.clear()
            tcp_server_socket.send(('Ultrasonic_end').encode())
        elif 'stream_audio' == data:
            global server_address
            if audio_pid is None:
                logger.info('Audio streaming server starting...')
                audio_pid = subprocess.Popen([
                    'cvlc alsa://' + config.AUDIO_INPUT + ' :live-caching=50 --sout "#standard{access=http,mux=ogg,dst=' + server_address + ':' + str(
                        config.AUDIO_PORT) + '}"'],
                    shell=True, preexec_fn=os.setsid)
            else:
                logger.info('Audio streaming server already started.')
            tcp_server_socket.send('stream_audio'.encode())
        elif 'stream_audio_end' == data:
            if audio_pid is not None:
                try:
                    os.killpg(os.getpgid(audio_pid.pid), signal.SIGTERM)  # Send the signal to all the process groups
                    audio_pid = None
                except:
                    logger.error('Unable to kill audio stream.')
            tcp_server_socket.send('stream_audio_end'.encode())
        elif 'start_video' == data:
            config.VIDEO_OUT = True
            tcp_server_socket.send('start_video'.encode())
        elif 'stop_video' == data:
            config.VIDEO_OUT = False
            tcp_server_socket.send('stop_video'.encode())
        elif 'FindColor' == data:
            led.mode_set(1)
            camera.FindColor(1)
            tcp_server_socket.send('FindColor'.encode())
        elif 'WatchDog' == data:
            led.mode_set(1)
            camera.WatchDog(1)
            tcp_server_socket.send('WatchDog'.encode())
        elif 'Switch_1_on' == data:
            switch.switch(1, 1)
            tcp_server_socket.send('Switch_1_on'.encode())
        elif 'Switch_1_off' == data:
            switch.switch(1, 0)
            tcp_server_socket.send('Switch_1_off'.encode())
        elif 'Switch_2_on' == data:
            switch.switch(2, 1)
            tcp_server_socket.send('Switch_2_on'.encode())
        elif 'Switch_2_off' == data:
            switch.switch(2, 0)
            tcp_server_socket.send('Switch_2_off'.encode())
        elif 'Switch_3_on' == data:
            switch.switch(3, 1)
            tcp_server_socket.send('Switch_3_on'.encode())
        elif 'Switch_3_off' == data:
            switch.switch(3, 0)
            tcp_server_socket.send('Switch_3_off'.encode())
        elif 'disconnect' == data:
            tcp_server_socket.send('disconnect'.encode())
            return
        elif 'steady' == data:
            led.mode_set(1)
            led.color_set('blue')
            steadyMode = 1
            tcp_server_socket.send('steady'.encode())
        elif 'func_end' == data:
            led.mode_set(0)
            camera.FindColor(0)
            camera.WatchDog(0)
            steadyMode = 0
            move.robot_home()
            tcp_server_socket.send('func_end'.encode())
        elif 'forward' == data:
            direction_command = 'forward'
        elif 'backward' == data:
            direction_command = 'backward'
        elif 'DS' in data:
            direction_command = 'stand'
        elif 'left' == data:
            turn_command = 'left'
        elif 'right' == data:
            turn_command = 'right'
        elif 'leftside' == data:
            direction_command = 'c_left'
        elif 'rightside' == data:
            direction_command = 'c_right'
        elif 'TS' in data:
            turn_command = 'stand'
        elif 'headup' == data:
            move.robot_pitch_roll(-100, 0)
        elif 'headdown' == data:
            move.robot_pitch_roll(100, 0)
        elif 'headhome' == data:
            move.robot_home()
        elif 'low' == data:
            move.robot_height(0)
        elif 'high' == data:
            move.robot_height(100)
        elif 'headleft' == data:
            move.robot_yaw(config.torso_w, 100)
        elif 'headright' == data:
            move.robot_yaw(config.torso_w, -100)
        elif 'rollLeft' == data:
            move.robot_pitch_roll(0, 100)
        elif 'rollRight' == data:
            move.robot_pitch_roll(0, -100)
        elif 'btn_balance_front' == data:
            move.robot_balance('front')
        elif 'btn_balance_back' == data:
            move.robot_balance('back')
        elif 'btn_balance_left' == data:
            move.robot_balance('left')
        elif 'btn_balance_right' == data:
            move.robot_balance('right')
        elif 'btn_balance_front_left' == data:
            move.robot_balance('front_left')
        elif 'btn_balance_front_right' == data:
            move.robot_balance('front_right')
        elif 'btn_balance_center' == data:
            move.robot_balance('center')
        elif 'btn_balance_back_left' == data:
            move.robot_balance('back_left')
        elif 'btn_balance_back_right' == data:
            move.robot_balance('back_right')
        elif 'speed:' in data:
            logger.debug('Received set servo speed')
            try:
                value = int(data.split(':', 2)[1])
                if value > 0:
                    config.SPEED = value
            except:
                logger.error('Error setting servo speed: %s', value)
                logger.error('Exception: %s', traceback.format_exc())
                pass
        elif 'light:' in data:
            logger.debug('Received flash light intensity %s%', value)
            try:
                value = int(data.split(':', 2)[1])
                switch.channel_B(value)
                move.pca.set_pwm(15, 0, int(4096 / 100 * (value - 2)))
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


# Diagonal method to maintain robot balance
def move_thread(event):
    logger.info('Thread started')
    global direction_command, turn_command
    step = 0
    last_direction_command = 'no'
    last_turn_command = 'no'

    forward_backward = ["move.robot_yaw(move.torso_wiggle, 0)", "move.robot_balance(balance[0])", "move.leg_up(leg[0])",
                        "move.leg_move(leg[0], direction_command)", "move.log_down(leg[0])", "move.leg_up(leg[1])",
                        "move.leg_move(leg[1], direction_command)", "move.log_down(leg[1])",
                        "move.robot_yaw(move.torso_wiggle, 0)", "move.robot_balance(balance[1])", "move.leg_up(leg[2])",
                        "move.leg_move(leg[2], direction_command)", "move.log_down(leg[2])", "move.leg_up(leg[3])",
                        "move.leg_move(leg[3], direction_command)", "move.log_down(leg[3])"]

    crab = ["move.robot_height(60)", "move.robot_balance(balance)", "move.leg_up(leg[0])",
            "move.leg_move(leg[0], 'out')", "move.log_down(leg[0])", "move.leg_up(leg[1])",
            "move.leg_move(leg[1], 'in')", "move.log_down(leg[1], 200)", "move.balance_back()",
            "move.leg_up(leg[2])", "move.leg_move(leg[2], 'out')", "move.log_down(leg[2])", "move.leg_up(leg[3])",
            "move.leg_move(leg[3], 'in')", "move.log_down(leg[3], 200)"
            ]

    turn = ["move.robot_balance(balance[0])", "move.leg_up(leg[0])", "move.leg_move(leg[0], 'backward')",
            "move.log_down(leg[0])", "move.leg_up(leg[1])", "move.leg_move(leg[1], 'backward')",
            "move.log_down(leg[1])", "move.robot_balance(balance[1])", "move.leg_up(leg[2])",
            "move.leg_move(leg[2], 'forward')", "move.log_down(leg[2])", "move.leg_up(leg[3])",
            "move.leg_move(leg[3], 'forward')", "move.log_down(leg[3])"
            ]

    while not event.is_set():
        if not steadyMode:
            if (direction_command == 'forward' or direction_command == 'backward') and turn_command == 'no':
                # Initialize variables
                if not last_direction_command == direction_command:
                    if direction_command == 'forward':
                        leg = [2, 1, 4, 3]
                        balance = ['front_right', 'front_left']
                    elif direction_command == 'backward':
                        leg = [3, 4, 1, 2]
                        balance = ['back_left', 'back_right']
                    move.robot_height(100)
                    last_direction_command = direction_command
                exec(forward_backward[step])
                step += 1
                if step == len(forward_backward):
                    step = 0
                continue
            elif (direction_command == 'c_right' or direction_command == 'c_left') and turn_command == 'no':
                # Initialize variables
                if not last_direction_command == direction_command:
                    if direction_command == 'c_left':
                        leg = [2, 4, 1, 3]
                        balance = 'front_left'
                    elif direction_command == 'c_right':
                        leg = [4, 2, 3, 1]
                        balance = 'front_right'
                    move.torso_wiggle = 50
                    last_direction_command = direction_command
                exec(crab[step])
                step += 1
                if step == len(crab):
                    step = 0
                continue
            elif direction_command == 'no' and (turn_command == 'left' or turn_command == 'right'):
                # Initialize variables
                if not last_turn_command == turn_command:
                    if turn_command == 'left':
                        leg = [1, 2, 4, 3]
                        balance = ['back_right', 'front_left']
                    elif turn_command == 'right':
                        leg = [3, 4, 2, 1]
                        balance = ['back_left', 'front_right']
                    move.torso_wiggle = 50
                    last_turn_command = turn_command
                    move.robot_height(100)
                    continue
                exec(turn[step])
                step += 1
                if step == len(turn):
                    step = 0
                continue
            elif turn_command == 'stand' or direction_command == 'stand':
                move.robot_height(50)
                move.robot_balance('center')
                move.torso_wiggle = config.torso_w - ((config.DEFAULT_X - 50) * 2 / 100 * config.torso_w)
                turn_command = 'no'
                direction_command = 'no'
                pass
            last_direction_command = 'no'
            last_turn_command = 'no'
            time.sleep(0.5)
            step = 0
            pass
        else:
            move.robot_steady()
    logger.info('Thread stopped')


def main():
    logger.info('Starting server.')
    global kill_event
    switch.switchSetup()
    switch.set_all_switch_off()
    kill_event.clear()
    try:
        led_threading = threading.Thread(target=led.led_thread, args=[kill_event], daemon=True)
        led_threading.setName('led_thread')
        led_threading.start()
        led.color_set('blue')
    except:
        pass
    connect()
    speak(speak_dict.connect)
    threading.Thread(target=move.servo_init, args=[], daemon=True).start()

    try:
        led.mode_set(0)
        led.colorWipe([255, 255, 255])
    except:
        logger.error('Exception LED: %s', traceback.format_exc())
        pass
    try:
        if config.CAMERA_MODULE:
            global camera
            camera_thread = threading.Thread(target=camera.capture_thread, args=[kill_event], daemon=True)
            camera_thread.setName('camera_thread')
            camera_thread.start()
        info_threading = threading.Thread(target=info_thread, args=[kill_event], daemon=True)
        info_threading.setName('info_thread')
        info_threading.start()
        moving_threading = threading.Thread(target=move_thread, args=[kill_event], daemon=True)
        moving_threading.setName('move_thread')
        moving_threading.start()
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
