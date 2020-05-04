#!/usr/bin/env/python
# E-mail      : sect16@gmail.com
# Author      : Chin Pin Hon
# Date        : 14.01.2020

"""
Functions for starting threads
"""

import logging
import threading
import time
import traceback
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


def config_export(initial, new_num):
    """
    This function to replace data in 'config.txt' file
    :param initial:
    :param new_num:
    """
    logger.debug('Writing configuration to file: ' + initial + new_num)
    ptr = 0
    str_num = str(new_num)
    contents = []
    exist = 0
    with open("config.txt", "r") as f:
        for line in f.readlines():
            if line.find(initial) >= 0:
                exist = 1
                contents.append(initial + str_num)
            elif line != '\n':
                contents.append(line.strip('\n'))
    with open("config.txt", "w") as f:
        if exist == 0:
            contents.append(initial + str_num)
        for newline in contents:
            f.writelines(newline + '\n')  # Call this function to replace data in '.txt' file


def config_import(label):
    """
    This function imports IP address data from 'config.txt' file
    :param label: Label of value to be imported.
    :return: IP value in config.txt file.
    """
    f = open("config.txt", "r")
    for line in f:
        if line.find(label) == 0:
            this_list = line.replace(" ", "").replace("\n", "").split(':', 2)
            return this_list[1]


def status_client_thread(event):
    """
    TCP client thread
    :param event: Clear event flag to terminate thread
    """
    logger.debug('Thread started')
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
    logger.debug('Thread stopped')


def stat_server_thread(event):
    """
    Statistics server thread
    :param event: Clear event flag to terminate thread
    """
    logger.debug('Thread started')
    global cpu_temp, cpu_use, ram_use, connect_event
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
            info_data = str(stat_sock.recv(config.BUFFER_SIZE).decode())
            info_get = info_data.split()
            if info_get.__len__() == 3:
                cpu_temp, cpu_use, ram_use = info_get
                logger.debug('cpu_tem:%s, cpu_use:%s, ram_use:%s' % (cpu_temp, cpu_use, ram_use))
                gui.stat_update(cpu_temp, cpu_use, ram_use)
                retries = 0
            elif retries >= 10:
                logger.error('Maximum retires reached (%d), disconnecting', retries)
                disconnect()
            else:
                logger.warning('Invalid info_data received from server: "%s"', info_data)
                gui.stat_update('-', '-', '-')
                retries = retries + 1
        except:
            logger.error('Connection error, disconnecting')
            disconnect()
            logger.error('Thread exception: %s', traceback.format_exc())
    logger.debug('Thread stopped')


def connect():  # Call this function to connect with the server
    """
    Initialize and begin connection
    """
    global connect_event, tcp_client_socket
    if str(gui.btn_connect['state']) == 'normal':
        gui.btn_connect['state'] = 'disabled'
    if not connect_event.is_set():
        # logger.info('Connecting to server')
        ip_address = gui.e1.get()  # Get the IP address from Entry
        gui.label_ip_1.config(bg='#FF8F00')
        gui.e1.config(state='disabled')
        if ip_address == '':  # If no input IP address in Entry,import a default IP
            try:
                ip_address = str(config_import('IP:'))
                gui.label_ip_2.config(text='Default: %s' % ip_address)
            except:
                logger.error('Error setting IP')
                pass
        gui.label_ip_1.config(text='Connecting')
        gui.label_ip_1.config(bg='#FF8F00')
        server_ip = ip_address
        addr = (server_ip, config.SERVER_PORT)
        tcp_client_socket = socket(AF_INET, SOCK_STREAM)  # Set connection value for socket
        try:
            logger.info("Connecting to server @ %s:%d..." % (server_ip, config.SERVER_PORT))
            tcp_client_socket.connect(addr)  # Connection with the server
            logger.info("Connected successfully")
            gui.label_ip_2.config(text='IP: %s' % ip_address)
            gui.label_ip_1.config(text='Connected')
            gui.label_ip_1.config(bg='#558B2F')
            config_export('IP:', ip_address)
            gui.e2.config(state='normal')
            gui.btn_connect.config(state='normal')
            gui.btn_connect.config(text='Disconnect')
            connect_event.set()  # Set to start threads
            status_threading = threading.Thread(target=status_client_thread, args=([connect_event]),
                                                daemon=True)
            status_threading.start()
            info_threading = threading.Thread(target=stat_server_thread, args=([connect_event]), daemon=True)
            info_threading.start()
        except:
            logger.error('Unable to connect: %s', traceback.format_exc())
        if not connect_event.is_set():
            gui.label_ip_1.config(text='Disconnected')
            gui.label_ip_1.config(bg=config.LABEL_BG)
            gui.btn_connect.config(state='normal')
            gui.e1.config(state='normal')
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
    # Export scale values to file
    config_export('SCALE_R:', gui.var_R.get())
    config_export('SCALE_B:', gui.var_G.get())
    config_export('SCALE_G:', gui.var_B.get())
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
    gui.e1.config(state='normal')
    gui.e2.config(state='disabled')
    gui.btn_audio.config(bg=config.COLOR_BTN)


def terminate(event=None):
    """
    Close GUI application.
    :param event: Tkinter event
    """
    logger.info('Exiting application...')
    disconnect()
    time.sleep(0.5)
    gui.root.destroy()


def send(value):
    """
    Sends command or text over the tcp client socket.
    :param value: command or text
    """
    if not connect_event.is_set():
        logger.warning('Unable to send command, no connection.')
    elif connect_event.is_set():
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
    if gui.ultrasonic_mode == 0 and not ultra_event.is_set() and config.ULTRA_SENSOR is not None:
        import ultra
        ultra_event.set()
        ultra_threading = threading.Thread(target=ultra.ultra_server_thread, args=([ultra_event]), daemon=True)
        ultra_threading.start()
