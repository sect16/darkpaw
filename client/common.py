#!/usr/bin/env/python
# E-mail      : sect16@gmail.com
# Author      : Chin Pin Hon
# Date        : 14.01.2020

import traceback

import logging
import threading
import time
from socket import *

import config
import gui

logger = logging.getLogger(__name__)
fpv_event = threading.Event()
connect_event = threading.Event()
ultra_event = threading.Event()
cpu_temp = 0
cpu_use = 0
ram_use = 0
voltage = 0
current = 0
ambient = 0


def config_export(label, new_num):
    """
    This function to replace data in 'config.txt' file
    :param label:
    :param new_num:
    """
    logger.info('Writing configuration to file: ' + label + new_num)
    ptr = 0
    str_num = str(new_num)
    contents = []
    exist = 0
    try:
        with open("config.txt", "r") as f:
            for line in f.readlines():
                if line.find(label) >= 0:
                    exist = 1
                    contents.append(label + str_num)
                elif line != '\n':
                    contents.append(line.strip('\n'))
    except:
        logger.warning('Unable to read config.txt file.')
        pass
    with open("config.txt", "w") as f:
        if exist == 0:
            contents.append(label + str_num)
        for newline in contents:
            f.writelines(newline + '\n')  # Call this function to replace data in '.txt' file


def config_import(label):
    """
    This function imports data from 'config.txt' file
    :param label: Label of value to be imported.
    :return: IP value in config.txt file.
    """
    with open("config.txt", "r") as f:
        for line in f:
            if line.find(label) == 0:
                return line.replace(" ", "").replace("\n", "").split(':', 2)[1]
    logger.warning('Unable to read value label \"%s\" from configuration file.', label)


def status_client_thread(event):
    """
    TCP client thread
    :param event: Clear event flag to terminate thread
    """
    logger.info('Thread started')
    global tcp_client_socket
    while event.is_set():
        try:
            status_data = (tcp_client_socket.recv(config.BUFFER_SIZE)).decode()
            logger.info('Received status info: %s' % (status_data,))
            gui.button_update(status_data)
            time.sleep(0.5)
        except:
            logger.error('Thread exception: %s', traceback.format_exc())
            disconnect()
    logger.info('Thread stopped')


def info_thread(event):
    """
    Statistics server thread
    :param event: Clear event flag to terminate thread
    """
    logger.info('Thread started')
    global cpu_temp, cpu_use, ram_use, voltage, current, connect_event
    addr = ('', config.INFO_PORT)
    stat_sock = socket(AF_INET, SOCK_STREAM)
    stat_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    stat_sock.bind(addr)
    stat_sock.listen(5)  # Start server,waiting for client
    stat_sock, addr = stat_sock.accept()
    logger.info('Info port connected')
    retries = 0
    while event.is_set():
        try:
            message = str(stat_sock.recv(config.BUFFER_SIZE).decode())
            data = message.split()
            if data.__len__() == 6:
                cpu_temp, cpu_use, ram_use, voltage, current, ambient = data
                logger.debug('cpu_tem:%s, cpu_use:%s, ram_use:%s, voltage:%s, current:%s, ambient:%s' % (
                    cpu_temp, cpu_use, ram_use, voltage, current, ambient))
                gui.stat_update(cpu_temp, cpu_use, ram_use, voltage, current, ambient)
                retries = 0
            elif retries >= config.MAX_INFO_RETRY:
                logger.error('Maximum retires reached (%d), disconnecting', retries)
                disconnect()
            else:
                logger.warning('Invalid info_data received from server: "%s"', message)
                gui.stat_update('-', '-', '-', '-', '-', '-')
                retries = retries + 1
        except:
            logger.error('Connection error, disconnecting')
            disconnect()
            logger.error('Thread exception: %s', traceback.format_exc())
    logger.info('Thread stopped')


def ip_check(ip_address):
    try:
        list_n = str(ip_address).split('.')
        count = 0
        for n in list_n:
            if 255 > int(n) >= 0:
                count += 1
        if count == 4:
            return True
    except:
        logger.error('Unable to validate IP address: %s', traceback.format_exc())
        pass
    logger.error('Invalid IP address input: %s', ip_address)
    gui.label_ip_1.config(text='Invalid IP Address!')
    return False


def connect():  # Call this function to connect with the server
    """
    Initialize and begin connection
    """
    global connect_event, tcp_client_socket
    ip_address = gui.entry_ip.get()  # Get the IP address from Entry
    if not connect_event.is_set() and ip_check(ip_address):
        gui.btn_connect['state'] = 'disabled'
        gui.label_ip_1.config(bg='#FF8F00')
        gui.entry_ip.config(state='disabled')
        gui.label_ip_1.config(text='Connecting')
        gui.label_ip_1.config(bg='#FF8F00')
        tcp_client_socket = socket(AF_INET, SOCK_STREAM)  # Set connection value for socket
        addr = (ip_address, config.SERVER_PORT)
        try:
            logger.info("Connecting to server @ %s:%d..." % (ip_address, config.SERVER_PORT))
            tcp_client_socket.connect(addr)  # Connection with the server
            logger.info("Connected successfully")
            config_export('IP:', ip_address)
            connect_event.set()  # Set to start threads
            status_threading = threading.Thread(target=status_client_thread, args=([connect_event]),
                                                daemon=True)
            status_threading.setName('status_thread')
            status_threading.start()
            info_threading = threading.Thread(target=info_thread, args=([connect_event]), daemon=True)
            info_threading.setName('stat_thread')
            info_threading.start()
            keepalive_threading = threading.Thread(target=keepalive_thread, args=([connect_event]), daemon=True)
            keepalive_threading.setName('keepalive_thread')
            keepalive_threading.start()
            gui.connect_init(ip_address)
        except:
            logger.error('Unable to connect: %s', traceback.format_exc())
        if not connect_event.is_set():
            gui.label_ip_1.config(text='Disconnected')
            gui.label_ip_1.config(bg=config.LABEL_BG)
            gui.btn_connect.config(state='normal')
            gui.entry_ip.config(state='normal')
    elif connect_event.is_set():
        disconnect()


def disconnect():
    """
    Function to flag threads to stop and closes socket.
    """
    logger.info('Disconnecting from server')
    fpv_event.clear()  # Clear to kill threads
    ultra_event.clear()
    time.sleep(0.5)
    if connect_event.is_set():
        try:
            send('disconnect')
        except:
            logger.error('Unable to send disconnect to server, quit anyway')
        connect_event.clear()
        time.sleep(1)
        tcp_client_socket.close()  # Close socket or it may not connect with the server again
    else:
        connect_event.clear()
    gui.btn_connect.config(text='Connect', fg=config.COLOR_TEXT, bg=config.COLOR_BTN)
    gui.btn_connect.config(state='normal')
    gui.label_ip_1.config(text='Disconnected', fg=config.COLOR_TEXT, bg=config.LABEL_BG)
    gui.all_btn_normal()
    gui.unbind_keys()
    gui.entry_ip.config(state='normal')
    gui.entry_text.config(state='disabled')
    gui.btn_video.config(bg=config.COLOR_BTN)
    gui.btn_video['state'] = 'normal'
    gui.btn_audio.config(bg=config.COLOR_BTN)
    gui.stat_update('-', '-', '-', '-', '-', '-')


def terminate(event=None):
    """
    Close GUI application.
    :param event: Tkinter event
    """
    logger.info('Exiting application...')
    disconnect()
    # Export scale values to file
    config_export('SCALE_R:', gui.var_R.get())
    config_export('SCALE_B:', gui.var_G.get())
    config_export('SCALE_G:', gui.var_B.get())
    config_export('SPEED:', gui.entry_speed.get())
    time.sleep(0.5)
    gui.root.destroy()


def send(value):
    """
    Sends command or text over the tcp client socket. Ignores robot movement commands if in function mode.
    :param value: command
    """
    if not connect_event.is_set():
        logger.error('Unable to send command, not connected.')
    elif connect_event.is_set():
        if 'espeak' not in value and gui.func_mode == 1 and ('move_' in value or 'balance_' in value):
            logger.warning('Unable to send command when robot in function mode!')
            return
        else:
            logger.info('Sending data: %s', value)
            tcp_client_socket.send(value.encode())
    else:
        logger.warning('Unable to send command, unknown connection status.')


def start_ultra():
    """
    Checks for ultrasonic status and starts thread is not yet started.
    Does not start if thread is existing not yet stopped.
    """
    global ultra_event
    if gui.ultrasonic_mode == 0 and not ultra_event.is_set() and config.ULTRA_SENSOR:
        import ultra
        ultra_event.set()
        ultra_threading = threading.Thread(target=ultra.ultra_server_thread, args=([ultra_event]), daemon=True)
        ultra_threading.setName('ultra_thread')
        ultra_threading.start()


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


def keepalive_thread(event):
    logger.info('Thread started')
    while event.is_set():
        time.sleep(config.KEEPALIVE_INTERVAL)
        logger.debug('Sending keepalive message')
        send('|ACK|')
    logger.info('Thread stopped')
