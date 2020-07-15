# E-mail      : sect16@gmail.com
# Author      : Chin Pin Hon
# Date        : 14.01.2020

import traceback

import logging
from socket import *

import config
import gui
from common import ultra_event

logger = logging.getLogger(__name__)


def ultra_server_thread(event):
    """
    Creates a TCP server and listen on port.
    :param event: Event flag to signal termination.
    """
    logger.info('Thread started')
    ultra_addr = ('', config.ULTRA_PORT)
    ultra_sock = socket(AF_INET, SOCK_STREAM)
    ultra_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    ultra_sock.bind(ultra_addr)
    ultra_sock.listen(5)  # Start server, waiting for client
    gui.ultrasonic_mode = 1
    ultra_sock, addr = ultra_sock.accept()
    logger.info('Ultrasonic port connected')
    gui.canvas_ultra.create_rectangle(0, 0, 280, 30, fill='#FFFFFF', width=0)
    while event.is_set():
        try:
            config.ultra_data = str(ultra_sock.recv(config.BUFFER_SIZE).decode()).split()[0]
            if config.ultra_data != '':
                config.ultra_data = float(config.ultra_data)
                if float(config.ultra_data) < 3:
                    logger.debug('Ultrasonic data received (%s)', config.ultra_data)
                    try:
                        gui.canvas_ultra.delete(canvas_text)
                        gui.canvas_ultra.delete(canvas_rec)
                    except:
                        pass
                    canvas_rec = gui.canvas_ultra.create_rectangle(0, 0,
                                                                   (280 - int(float(config.ultra_data) * 280 / 3)), 30,
                                                                   fill='#448AFF', width=0)
                    canvas_text = gui.canvas_ultra.create_text((90, 11),
                                                               text='Ultrasonic Output: %sm' % config.ultra_data,
                                                               fill='BLACK')
        except:
            logger.error('Ultrasonic exception: %s', traceback.format_exc())
            ultra_event.clear()
            pass
    gui.canvas_ultra.create_rectangle(0, 0, 280, 30, fill='#FFFFFF', width=0)
    gui.canvas_ultra.create_text((90, 11), text='Ultrasonic OFF', fill='#000000')
    gui.ultrasonic_mode = 0
    logger.info('Thread stopped')
