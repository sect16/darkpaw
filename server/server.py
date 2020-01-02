#!/usr/bin/env/python
# File name   : server.py
# Description : main programe for DarkPaw
# E-mail      : sect16@gmail.com
# Author      : Chin Pin Hon
# Date        : 29/11/2019

import os
import FPV
import socket
import sys
import time
import threading
import move
import argparse
from rpi_ws281x import *
import psutil
import switch
import traceback
import LED
import speak_dict
import config
import subprocess
import coloredlogs, logging

# Create a logger object.
logger = logging.getLogger(__name__)

# By default the install() function installs a handler on the root logger,
# this means that log messages from your code and log messages from the
# libraries that you use will all show up on the terminal.
# coloredlogs.install(level='DEBUG')
coloredlogs.install(level='DEBUG',
                    fmt='%(asctime)s.%(msecs)03d %(levelname)7s %(thread)5d --- [%(threadName)16s] %(funcName)-39s: %(message)s', logger=logger)
# logger.basicConfig(level=logger.DEBUG, format='%(asctime)s) %(levelname)7s %(thread)5d --- [%(threadName)16s] %(funcName)-39s: %(message)s')
# %clr(%d{${LOG_DATEFORMAT_PATTERN:HH:mm:ss.SSS}}){faint} %clr(${LOG_LEVEL_PATTERN:%5p}) %clr(${PID: }){magenta} %clr(---){faint} %clr([%16.16t]){faint} %clr(%-40.40logger{39}){cyan} %clr(:){faint} %m%n${LOG_EXCEPTION_CONVERSION_WORD:%wEx}"
logger.debug('Starting python...')
'''
Initiation number of steps, don't have to change it.
'''
step_set = 1
'''
Initiation commands
'''
direction_command = 'no'
turn_command = 'no'
# pwm = Adafruit_PCA9685.PCA9685()
# pwm.set_pwm_freq(50)
LED = LED.LED()
smoothMode = 0
steadyMode = 0
addr = None
tcpCliSock = None
HOST = None
PORT = 10223  # Define port serial
BUFFER = 1024  # Define buffer size
SPEED = 150
ADDR = (HOST, PORT)
wiggle = 100
kill_event = threading.Event()
server_address = ''
stream_audio_started = 0


def breath_led():
    LED.breath(255)


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


def move_thread(i, event):
    logger.debug('Thread started')
    global step_set
    stand_stu = 1
    while not event.is_set():
        if not steadyMode:
            if direction_command == 'forward' and turn_command == 'no':
                stand_stu = 0
                move.dove_move_tripod(step_set, wiggle, 'forward')
                step_set += 1
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
                    move.robot_stand(config.lower_leg_m)
                    step_set = 1
                    stand_stu = 1
                else:
                    time.sleep(0.01)
                    pass
            pass
        else:
            pass
            move.robot_X(50)
            move.steady()
            logger.debug('steady')
            time.sleep(0.2)
    logger.debug('Thread stopped')


def info_send_client_thread(arg, event):
    logger.debug('Thread started')
    SERVER_IP = addr[0]
    SERVER_PORT = 2256  # Define port serial
    SERVER_ADDR = (SERVER_IP, SERVER_PORT)
    Info_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Set connection value for socket
    Info_Socket.connect(SERVER_ADDR)
    logger.debug('Server address %s', SERVER_ADDR)
    while not event.is_set():
        try:
            Info_Socket.send((get_cpu_temp() + ' ' + get_cpu_use() + ' ' + get_ram_info()).encode())
            time.sleep(1)
        except:
            logger.error('Exception: %s', traceback.format_exc())
            pass
    logger.debug('Thread stopped')


def FPV_thread(arg, event):
    logger.debug('Thread started')
    global fpv
    fpv = FPV.FPV()
    fpv.fpv_capture_thread(addr[0], event)
    logger.debug('Thread stopped')


def run():
    global direction_command, turn_command, smoothMode, steadyMode
    # Define a thread for FPV and OpenCV
    moving_threading = threading.Thread(target=move_thread, args=(0, kill_event), daemon=True)
    # 'True' means it is a front thread,it would close when the mainloop() closes
    moving_threading.setDaemon(True)
    # Thread starts
    moving_threading.start()
    # Define a thread for FPV and OpenCV
    info_threading = threading.Thread(target=info_send_client_thread, args=(0, kill_event), daemon=True)
    # 'True' means it is a front thread,it would close when the mainloop() closes
    info_threading.setDaemon(True)
    # Thread starts
    info_threading.start()
    ws_R = 0
    ws_G = 0
    ws_B = 0
    run = True
    while run:
        #data = ''
        data = str(tcpCliSock.recv(BUFFER).decode())
        logger.debug('Received data on tcp socket: %s', data)
        if not data:
            run = False
            raise Exception
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
            move.robot_stand(0)
        elif 'high' == data:
            move.robot_stand(100)
        elif 'headleft' == data:
            move.ctrl_yaw(config.torso_w, 100)
        elif 'headright' == data:
            move.ctrl_yaw(config.torso_w, -100)
        elif 'wsR' in data:
            try:
                set_R = data.split()
                ws_R = int(set_R[1])
                LED.colorWipe(Color(ws_R, ws_G, ws_B))
            except:
                logger.error('Exception: %s', traceback.format_exc())
                pass
        elif 'wsG' in data:
            try:
                set_G = data.split()
                ws_G = int(set_G[1])
                LED.colorWipe(Color(ws_R, ws_G, ws_B))
            except:
                logger.error('Exception: %s', traceback.format_exc())
                pass
        elif 'wsB' in data:
            try:
                set_B = data.split()
                ws_B = int(set_B[1])
                LED.colorWipe(Color(ws_R,ws_G,ws_B))
            except:
                logger.error('Exception: %s', traceback.format_exc())
                pass
        elif 'FindColor' in data:
            LED.breath_status_set(1)
            fpv.FindColor(1)
            tcpCliSock.send('FindColor'.encode())
        elif 'WatchDog' in data:
            LED.breath_status_set(1)
            fpv.WatchDog(1)
            tcpCliSock.send('WatchDog'.encode())
        elif 'steady' in data:
            LED.breath_status_set(1)
            LED.breath_color_set('blue')
            steadyMode = 1
            tcpCliSock.send('steady'.encode())
        elif 'func_end' in data:
            LED.breath_status_set(0)
            fpv.FindColor(0)
            fpv.WatchDog(0)
            steadyMode = 0
            move.init_servos()
            tcpCliSock.send('func_end'.encode())

        elif 'Smooth_on' in data:
            smoothMode = 1
            tcpCliSock.send('Smooth_on'.encode())
        elif 'Smooth_off' in data:
            smoothMode = 0
            tcpCliSock.send('Smooth_off'.encode())

        elif 'Switch_1_on' in data:
            switch.switch(1, 1)
            tcpCliSock.send('Switch_1_on'.encode())
        elif 'Switch_1_off' in data:
            switch.switch(1, 0)
            tcpCliSock.send('Switch_1_off'.encode())
        elif 'Switch_2_on' in data:
            switch.switch(2, 1)
            tcpCliSock.send('Switch_2_on'.encode())
        elif 'Switch_2_off' in data:
            switch.switch(2, 0)
            tcpCliSock.send('Switch_2_off'.encode())
        elif 'Switch_3_on' in data:
            switch.switch(3, 1)
            tcpCliSock.send('Switch_3_on'.encode())
        elif 'Switch_3_off' in data:
            switch.switch(3, 0)
            tcpCliSock.send('Switch_3_off'.encode())
        elif 'disconnect' in data:
            tcpCliSock.send('disconnect'.encode())
            speak(speak_dict.disconnect)
        elif 'stream_audio' in data:
            global server_address, stream_audio_started
            if stream_audio_started == 0:
                logger.info('Audio streaming server starting...')
                subprocess.Popen([str('cvlc -vvv alsa://hw:1,0 :live-caching=50 --sout "#standard{access=http,mux=ogg,dst=' + server_address + ':3030}"')], shell = True)
                stream_audio_started = 1
            else:
                logger.info('Audio streaming server already started.')
            tcpCliSock.send('stream_audio'.encode())
        else:
            logger.info('Speaking command received')
            speak(data)
            pass


def speak(text):
    global SPEED
    os.system(str('espeak-ng "%s" -s %d' % (text, SPEED)))


# if __name__ == '__main__':
def main():
    global kill_event
    switch.switchSetup()
    switch.set_all_switch_off()
    kill_event.clear()
    HOST = ''
    PORT = 10223  # Define port serial
    BUFSIZ = 1024  # Define buffer size
    ADDR = (HOST, PORT)

    try:
        led_threading=threading.Thread(target=breath_led)         #Define a thread for LED breathing
        led_threading.setDaemon(True)                             #'True' means it is a front thread,it would close when the mainloop() closes
        led_threading.start()                                     #Thread starts
        LED.breath_color_set('blue')
    except:
        logger.debug('Use "sudo pip3 install rpi_ws281x" to install WS_281x package')
        pass

    while 1:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("1.1.1.1", 80))
            global server_address
            server_address = s.getsockname()[0]
            s.close()
            logger.debug('Server listening on: %s:%s', server_address, PORT)
        except:
            logger.warning('No network connection, starting local AP. %s', traceback.format_exc())
            # Define a thread for data receiving
            ap_threading = threading.Thread(target=ap_thread)
            # 'True' means it is a front thread,it would close when the mainloop() closes
            ap_threading.setDaemon(True)
            # Thread starts
            ap_threading.start()

            LED.colorWipe(Color(0,16,50))
            time.sleep(1)
            LED.colorWipe(Color(0,16,100))
            time.sleep(1)
            LED.colorWipe(Color(0,16,150))
            time.sleep(1)
            LED.colorWipe(Color(0,16,200))
            time.sleep(1)
            LED.colorWipe(Color(0,16,255))
            time.sleep(1)
            LED.colorWipe(Color(35,255,35))

        try:
            global tcpCliSock
            global addr
            tcp_ser_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_ser_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            tcp_ser_sock.bind(ADDR)
            # Start server,waiting for client
            tcp_ser_sock.listen(5)
            logger.debug('Waiting for connection...')
            tcpCliSock, addr = tcp_ser_sock.accept()
            logger.debug('Connected from %s', addr)
            speak(speak_dict.connect)
            move.init_servos()
            time.sleep(1)
            for x in range(99):
                move.robot_stand(x+1)
            fps_threading = threading.Thread(target=FPV_thread, args=(0, kill_event), daemon=True)  # Define a thread for FPV and OpenCV
            fps_threading.setDaemon(True)  # 'True' means it is a front thread,it would close when the mainloop() closes
            fps_threading.start()  # Thread starts
            break
        except:
            logger.error('Exception while waiting for connection: %s', traceback.format_exc())
            kill_event.set()
            LED.colorWipe(Color(0,0,0))
            pass

    try:
        LED.breath_status_set(0)
        LED.colorWipe(Color(64,128,255))
    except:
        logger.error('Exception LED breath: %s', traceback.format_exc())
        pass

    try:
        run()
    except:
        logger.debug('Last servo positions: %s', config.servo)
        logger.error('Run exception, terminate and restart main(). %s', traceback.format_exc())
        kill_event.set()
        LED.colorWipe(Color(0,0,0))
        # 150 - 500
        current_pos = int((config.servo[1]-config.lower_leg_l)/(config.lower_leg_w*2)*100)
        for x in range (current_pos):
            move.robot_stand(current_pos-x)
        move.release()
        switch.switch(1, 0)
        switch.switch(2, 0)
        switch.switch(3, 0)
        time.sleep(2)
        tcp_ser_sock.close()
        tcpCliSock.close()
        main()


main()
