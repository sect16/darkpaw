import logging
import threading
import time
import traceback
from socket import *

import coloredlogs

# Create a logger object.
import config
import gui

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG',
                    fmt='%(asctime)s.%(msecs)03d %(levelname)7s %(thread)5d --- [%(threadName)16s] %(funcName)-39s: %(message)s')
INFO_PORT = 2256  # Define port serial
SERVER_PORT = 10223  # Define port serial
BUFFER_SIZE = 1024
color_text = config.COLOR_TEXT
color_btn = config.COLOR_BTN
label_bg = config.LABEL_BG
fpv_event = threading.Event()
connect_event = threading.Event()
cpu_temp = 0
cpu_use = 0
ram_use = 0


def replace_num(initial, new_num):  # Call this function to replace data in '.txt' file
    newline = ""
    str_num = str(new_num)
    with open("ip.txt", "r") as f:
        for line in f.readlines():
            if line.find(initial) == 0:
                line = initial + "%s" % str_num
            newline += line
    with open("ip.txt", "w") as f:
        f.writelines(newline)  # Call this function to replace data in '.txt' file


def num_import(initial):  # Call this function to import data from '.txt' file
    with open("ip.txt") as f:
        for line in f.readlines():
            if line.find(initial) == 0:
                r = line
    begin = len(list(initial))
    return r[begin:]


def status_receive_thread(event):
    logger.debug('Thread started')
    global funcMode, tcp_client_socket, BUFFER_SIZE
    while event.is_set():
        try:
            status_data = (tcp_client_socket.recv(BUFFER_SIZE)).decode()
            logger.info('Received status info: %s' % (status_data,))
            gui.button_update(status_data)
            time.sleep(0.5)
        except:
            disconnect()
            logger.error('Thread exception: %s', traceback.format_exc())
    logger.debug('Thread stopped')


def stat_receive_thread(event):
    logger.debug('Thread started')
    global cpu_temp, cpu_use, ram_use, connect_event, INFO_PORT
    addr = ('', INFO_PORT)
    info_sock = socket(AF_INET, SOCK_STREAM)
    info_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    info_sock.bind(addr)
    info_sock.listen(5)  # Start server,waiting for client
    info_sock, addr = info_sock.accept()
    logger.info('Info port connected')
    while event.is_set():
        try:
            info_data = str(info_sock.recv(BUFFER_SIZE).decode())
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
    global connect_event, tcp_client_socket, BUFFER_SIZE, SERVER_PORT
    if str(gui.btn_connect['state']) == 'normal':
        gui.btn_connect['state'] = 'disabled'
    if not connect_event.is_set():
        logger.info('Connecting to server')
        ip_address = gui.e1.get()  # Get the IP address from Entry
        if ip_address == '':  # If no input IP address in Entry,import a default IP
            ip_address = num_import('IP:')
            gui.label_ip_1.config(text='Connecting')
            gui.label_ip_1.config(bg='#FF8F00')
            gui.label_ip_2.config(text='Default: %s' % ip_address)
            pass
        server_ip = ip_address
        addr = (server_ip, SERVER_PORT)
        tcp_client_socket = socket(AF_INET, SOCK_STREAM)  # Set connection value for socket
        try:
            for i in range(1, 6):  # Try 5 times if disconnected
                if not connect_event.is_set():
                    logger.info("Connecting to server @ %s:%d..." % (server_ip, SERVER_PORT))
                    tcp_client_socket.connect(addr)  # Connection with the server
                    logger.info("Connected successfully")
                    gui.label_ip_2.config(text='IP: %s' % ip_address)
                    gui.label_ip_1.config(text='Connected')
                    gui.label_ip_1.config(bg='#558B2F')
                    replace_num('IP:', ip_address)
                    gui.e1.config(state='disabled')
                    gui.btn_connect.config(state='normal')
                    gui.btn_connect.config(text='Disconnect')
                    connect_event.set()  # Set to start threads
                    status_threading = threading.Thread(target=status_receive_thread, args=([connect_event]),
                                                        daemon=True)
                    status_threading.start()
                    info_threading = threading.Thread(target=stat_receive_thread, args=([connect_event]), daemon=True)
                    info_threading.start()
                    break
                else:
                    logger.error("Cannot connect to server")
                    gui.label_ip_1.config(text='Try %d/5 time(s)' % i)
                    gui.label_ip_1.config(bg='#EF6C00')
                    logger.info('Try %d/5 time(s)' % i)
                    time.sleep(1)
                    continue
        except:
            logger.error('Unable to connect: %s', traceback.format_exc())
        if not connect_event.is_set():
            gui.label_ip_1.config(text='Disconnected')
            gui.label_ip_1.config(bg=label_bg)
            gui.btn_connect.config(state='normal')
    elif connect_event.is_set():
        disconnect()


def disconnect():
    logger.info('Disconnecting from server')
    fpv_event.clear()  # Clear to kill threads
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
    gui.btn_connect.config(text='Connect', fg=color_text, bg=color_btn)
    gui.btn_connect.config(state='normal')
    gui.label_ip_1.config(text='Disconnected', fg=color_text, bg=label_bg)
    gui.all_btn_normal()


def terminate(event):
    disconnect()
    time.sleep(0.5)
    gui.destroy()


def send(value):
    tcp_client_socket.send(value.encode())
