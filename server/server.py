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
direction_command = 'no'
turn_command = 'no'
led = led.Led()
if config.CAMERA_MODULE:
    camera = cam.Camera()
ultrasonicMode = 0
addr = None
tcp_server_socket = None
tcp_server = None
HOST = ''
ADDR = (HOST, config.SERVER_PORT)
kill_event = threading.Event()
ultra_event = threading.Event()
server_address = ''
stream_audio_started = 0
audio_pid = None
steadyMode = 0
wiggle = 100


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


def info_get():
    global cpu_t, cpu_u, gpu_t, ram_info
    while 1:
        cpu_t = get_cpu_temp()
        cpu_u = get_cpu_use()
        ram_info = get_ram_info()
        time.sleep(3)


def ultra_send_client(event):
    global ultra_event
    logger.info('Starting ultrasonic thread.')
    ultra_IP = addr[0]
    ultra_ADDR = (ultra_IP, config.ULTRA_PORT)
    ultra_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Set connection value for socket
    ultra_Socket.connect(ultra_ADDR)
    logger.debug(ultra_ADDR)
    while event.is_set() and ultrasonicMode:
        try:
            ultra_Socket.send(str(round(ultra.checkdist(), 2)).encode())
            time.sleep(0.5)
            camera.UltraData(round(ultra.checkdist(), 2))
            time.sleep(0.2)
        except:
            logger.error('Exception: %s', traceback.format_exc())
            break
    time.sleep(0.5)
    ultra_event.clear()


def info_thread(event):
    logger.debug('Thread started')
    SERVER_IP = addr[0]
    SERVER_ADDR = (SERVER_IP, config.INFO_PORT)
    Info_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Set connection value for socket
    Info_Socket.connect(SERVER_ADDR)
    logger.info('Server address %s', SERVER_ADDR)
    ina219 = pm.PowerModule()
    while not event.is_set():
        try:
            if config.POWER_MODULE:
                power = ina219.read_ina219()
                Info_Socket.send((get_cpu_temp() + ' ' + get_cpu_use() + ' ' + get_ram_info() + ' {0:0.2f}V'.format(
                    power[0]) + ' {0:0.2f}mA'.format(power[1])).encode())
            else:
                Info_Socket.send((get_cpu_temp() + ' ' + get_cpu_use() + ' ' + get_ram_info() + ' - -').encode())
            pass
            time.sleep(1)
        except BrokenPipeError:
            pass
        except:
            logger.error('Exception: %s', traceback.format_exc())
            pass
    logger.debug('Thread stopped')


def move_thread(event):
    logger.debug('Thread started')
    global step_set
    center = 1
    step = 1
    # move.robot_height(50)
    while not event.is_set():
        if not steadyMode:
            if direction_command == 'forward' and turn_command == 'no':
                if center == 1:
                    move.robot_balance('forward')
                move.move_direction('forward')
                if step_set == 9:
                    step_set = 1
                continue
            elif direction_command == 'backward' and turn_command == 'no':
                stand_stu = 0
                move.dove_move_tripod(step_set, wiggle, 'backward')
                step_set += 1
                if step_set == 9:
                    step_set = 1
                continue
            else:
                pass
            if turn_command != 'no':
                stand_stu = 0
                move.dove_move_diagonal(step_set, wiggle, turn_command)
                step_set += 1
                if step_set == 9:
                    step_set = 1
                continue
            else:
                pass
            if turn_command == 'no' and direction_command == 'stand':
                if stand_stu == 0:
                    move.robot_height(config.lower_leg_m)
                    step_set = 1
                    stand_stu = 1
                else:
                    time.sleep(0.01)
                    pass
            time.sleep(0.5)
            pass
        else:
            move.robot_steady()
    logger.debug('Thread stopped')


def run():
    global kill_event
    logger.info('Starting info and move threads...')
    info_threading = threading.Thread(target=info_thread, args=[kill_event], daemon=True)
    info_threading.setName('info_thread')
    info_threading.start()
    moving_threading = threading.Thread(target=move_thread, args=[kill_event], daemon=True)
    moving_threading.setName('move_thread')
    moving_threading.start()
    listener_thread(kill_event)


def main():
    logger.info('Starting server...')
    global kill_event, ADDR
    switch.switchSetup()
    switch.set_all_switch_off()
    kill_event.clear()
    try:
        led_threading = threading.Thread(target=led.led_thread, args=[kill_event],
                                         daemon=True)  # Define a thread for LED breatheing
        led_threading.setName('led_thread')
        led_threading.start()  # Thread starts
        led.color_set('blue')
    except:
        pass
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("1.1.1.1", 80))
            global server_address
            server_address = s.getsockname()[0]
            s.close()
            logger.info('Server listening on: %s:%s', server_address, config.SERVER_PORT)
        except:
            logger.warning('No network connection, starting local AP. %s', traceback.format_exc())
            ap_threading = threading.Thread(target=ap_thread, daemon=True)
            ap_threading.setName('ap_thread')
            ap_threading.start()
            led.colorWipe([0, 16, 50])
            time.sleep(1)
            led.colorWipe([0, 16, 100])
            time.sleep(1)
            led.colorWipe([0, 16, 150])
            time.sleep(1)
            led.colorWipe([0, 16, 200])
            time.sleep(1)
            led.colorWipe([0, 16, 255])
            time.sleep(1)
            led.colorWipe([35, 255, 35])
        try:
            global tcp_server_socket, tcp_server
            global addr
            tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            tcp_server.bind(ADDR)
            # Start server,waiting for client
            tcp_server.listen(5)
            logger.info('Waiting for connection...')
            led.color_set('cyan')
            led.mode_set(1)
            tcp_server_socket, addr = tcp_server.accept()
            logger.info('Connected from %s', addr)
            speak(speak_dict.connect)
            threading.Thread(target=move.servo_init, args=[], daemon=True).start()
            # move.servo_init()
            # move.robot_height(50)
            if config.CAMERA_MODULE:
                global camera
                camera_thread = threading.Thread(target=camera.capture_thread, args=[kill_event],
                                                 daemon=True)  # Define a thread for FPV and OpenCV
                camera_thread.setName('camera_thread')
                camera_thread.start()  # Thread starts
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

    try:
        led.mode_set(0)
        led.colorWipe([255, 255, 255])
    except:
        logger.error('Exception LED breathe: %s', traceback.format_exc())
        pass

    try:
        run()
    except:
        logger.error('Run exception: %s', traceback.format_exc())
        disconnect()


def disconnect():
    logger.info('Disconnecting and termination threads.')
    speak(speak_dict.disconnect)
    global tcp_server_socket, tcp_server, kill_event
    kill_event.set()
    led.colorWipe([0, 0, 0])
    move.robot_height(0)
    # move.servo_release()
    switch.switch(1, 0)
    switch.switch(2, 0)
    switch.switch(3, 0)
    time.sleep(0.5)
    tcp_server.close()
    tcp_server_socket.close()


def listener_thread(event):
    logger.info('Starting main listener thread...')
    global direction_command, turn_command, steadyMode, ultrasonicMode, camera, audio_pid
    ws_G = 0
    ws_R = 0
    ws_B = 0
    while not event.is_set():
        data = str(tcp_server_socket.recv(config.BUFFER_SIZE).decode())
        logger.debug('Received data on tcp socket: %s', data)
        if not data:
            continue
        elif 'wsR' in data:
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
            ultrasonicMode = 1
            tcp_server_socket.send(('Ultrasonic').encode())
            ultra_event.set()
            ultra_threading = threading.Thread(target=ultra_send_client, args=([ultra_event]), daemon=True)
            ultra_threading.setName('ultra_thread')
            ultra_threading.start()  # Thread starts

        elif 'Ultrasonic_end' == data:
            ultrasonicMode = 0
            ultra_event.clear()
            tcp_server_socket.send(('Ultrasonic_end').encode())
        elif 'stream_audio' == data:
            global server_address, stream_audio_started
            if stream_audio_started == 0:
                logger.info('Audio streaming server starting...')
                audio_pid = subprocess.Popen([
                    'cvlc alsa://hw:1,0 :live-caching=50 --sout "#standard{access=http,mux=ogg,dst=' + server_address + ':' + str(
                        config.AUDIO_PORT) + '}"'],
                    shell=True, preexec_fn=os.setsid)
                # p = subprocess.Popen(['/usr/bin/cvlc','-vvv', 'alsa://hw:1,0', ':live-caching=50', '--sout', '\"#standard{access=http,mux=ogg,dst=\'', server_address, '\':3030}\"'], shell=False)
                stream_audio_started = 1
            else:
                logger.info('Audio streaming server already started.')
            tcp_server_socket.send('stream_audio'.encode())
        elif 'stream_audio_end' == data:
            if audio_pid is not None:
                os.killpg(os.getpgid(audio_pid.pid), signal.SIGTERM)  # Send the signal to all the process groups
            stream_audio_started = 0
            tcp_server_socket.send('stream_audio_end'.encode())
        elif 'start_video' == data:
            config.VIDEO_OUT = 1
            tcp_server_socket.send('start_video'.encode())
        elif 'stop_video' == data:
            config.VIDEO_OUT = 0
            tcp_server_socket.send('stop_video'.encode())
        elif 'FindColor' == data:
            led.mode_set(1)
            camera.FindColor(1)
            tcp_server_socket.send('FindColor'.encode())
        elif 'WatchDog' == data:
            led.mode_set(1)
            camera.WatchDog(1)
            tcp_server_socket.send('WatchDog'.encode())
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
            turn_command = 'c_left'
        elif 'rightside' == data:
            turn_command = 'c_right'
        elif 'TS' in data:
            turn_command = 'no'
        elif 'headup' == data:
            move.ctrl_pitch_roll(-100, 0)
        elif 'headdown' == data:
            move.ctrl_pitch_roll(100, 0)
        elif 'headhome' == data:
            move.ctrl_pitch_roll(0, 0)
            move.ctrl_yaw(config.torso_w, 0)
        elif 'low' == data:
            move.robot_height(0)
        elif 'high' == data:
            move.robot_height(100)
        elif 'headleft' == data:
            move.ctrl_yaw(config.torso_w, 100)
        elif 'headright' == data:
            move.ctrl_yaw(config.torso_w, -100)

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
            disconnect()
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
            logger.debug('Received set servo resolution')
            try:
                config.resolution = int(data.split(':', 2)[1])
            except:
                logger.error('Error setting servo resolution: %s', data[0])
                pass
        else:
            logger.info('Speaking command received')
            speak(data)
            pass


if __name__ == "__main__":
    try:
        while True:
            main()
    except KeyboardInterrupt:
        pass
