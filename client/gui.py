#!/usr/bin/env/python
# E-mail      : sect16@gmail.com
# Author      : Chin Pin Hon
# Date        : 14.01.2020

"""
GUI layout definition
"""

import tkinter as tk
import traceback

import logging
import time

import config
import video
from common import send, connect, terminate, ultra_event, start_ultra, connect_event, config_import

logger = logging.getLogger(__name__)
root = tk.Tk()  # Define a window named root
keyDict = dict()
# Flags
move_forward_status = 0
move_backward_status = 0
move_left_status = 0
move_right_status = 0
func_mode = 0
switch_1 = 0
switch_2 = 0
switch_3 = 0
yaw_left_status = 0
yaw_right_status = 0
ultrasonic_mode = 0
led_sleep = 0
light_value = 0
speed_value = 0
var_pitch = 0
var_yaw = 0
var_height = 0

COLOR_SWT_ACT = config.COLOR_SWT_ACT
COLOR_BTN_ACT = config.COLOR_BTN_ACT
COLOR_BG = config.COLOR_BG  # Set background color
COLOR_TEXT = config.COLOR_TEXT
COLOR_TEXT_LABEL = config.COLOR_TEXT_LABEL
COLOR_BTN = config.COLOR_BTN
COLOR_BTN_RED = config.COLOR_BTN_RED


def loop():  # GUI
    """
    Main GUI layout
    """
    global root, entry_ip, entry_text, entry_speed, entry_lights, label_ip_1, COLOR_BTN, COLOR_TEXT, btn_connect, label_ambient, \
        label_cpu_temp, label_cpu_use, label_ram_use, COLOR_TEXT, var_R, var_B, var_G, btn_steady, btn_find_color, \
        btn_watchdog, btn_audio, btn_quit, btn_Switch_1, btn_Switch_2, btn_Switch_3, btn_video, \
        btn_ultra, btn_find_line, canvas_ultra, var_R, var_G, var_B, label_voltage, label_current, var_pitch, var_yaw, var_height
    root.geometry('565x510')  # Main window size
    root.config(bg=COLOR_BG)  # Set the background color of root window
    try:
        logo = tk.PhotoImage(file='logo.png')  # Define the picture of logo (Only supports '.png' and '.gif')
        l_logo = tk.Label(root, image=logo, bg=COLOR_BG)  # Set a label to show the logo picture
        l_logo.place(x=60, y=7)  # Place the Label in a right position
    except:
        pass
    root.title(config.TITLE)  # Main window title
    label_cpu_temp = tk.Label(root, width=18, text='CPU Temp:', fg=COLOR_TEXT, bg='#212121')
    label_cpu_use = tk.Label(root, width=18, text='CPU Usage:', fg=COLOR_TEXT, bg='#212121')
    label_ram_use = tk.Label(root, width=18, text='RAM Usage:', fg=COLOR_TEXT, bg='#212121')
    label_voltage = tk.Label(root, width=18, text='Voltage:', fg=COLOR_TEXT, bg='#212121')
    label_current = tk.Label(root, width=18, text='Current:', fg=COLOR_TEXT, bg='#212121')
    label_ambient = tk.Label(root, width=18, text='Ambient:', fg=COLOR_TEXT, bg='#212121')
    label_ip_1 = tk.Label(root, width=18, text='Disconnected', fg=COLOR_TEXT, bg='#F44336')
    label_ip_2 = tk.Label(root, width=10, text='IP Address:', fg=COLOR_TEXT_LABEL, bg=COLOR_BG)
    label_cpu_temp.place(x=400, y=15)  # Define a Label and put it in position
    label_cpu_use.place(x=400, y=45)  # Define a Label and put it in position
    label_ram_use.place(x=400, y=75)  # Define a Label and put it in position
    if config.POWER_MODULE:
        label_voltage.place(x=250, y=45)  # Define a Label and put it in position
        label_current.place(x=250, y=75)  # Define a Label and put it in position
    label_ip_1.place(x=400, y=110)  # Define a Label and put it in position
    label_ip_2.place(x=400, y=145)  # Define a Label and put it in position

    entry_ip = tk.Entry(root, show=None, width=10, bg='#FFFFFF', fg='#000000', disabledbackground=config.COLOR_GREY,
                        state='normal')
    entry_text = tk.Entry(root, show=None, width=71, bg='#FFFFFF', fg='#000000', disabledbackground=config.COLOR_GREY,
                          state='disabled')
    entry_ip.place(x=470, y=145)  # Define a Entry and put it in position
    entry_text.place(x=30, y=305)  # Define a Entry and put it in position

    btn_connect = tk.Button(root, width=8, height=1, text='Connect', fg=COLOR_TEXT, bg=COLOR_BTN, command=connect,
                            relief='ridge')
    btn_forward = tk.Button(root, width=8, text='Forward', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_backward = tk.Button(root, width=8, text='Backward', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_left = tk.Button(root, width=8, text='Left', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_right = tk.Button(root, width=8, text='Right', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_look_up = tk.Button(root, width=8, text='Up', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_look_down = tk.Button(root, width=8, text='Down', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_look_home = tk.Button(root, width=8, text='Home', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_video = tk.Button(root, width=8, text='Video', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_entry_text = tk.Button(root, width=8, text='Send', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_roll_left = tk.Button(root, width=8, text='Roll L', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_roll_right = tk.Button(root, width=8, text='Roll R', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')

    btn_connect.place(x=320, y=110)  # Define a Button and put it in position
    btn_forward.place(x=100, y=195)
    btn_backward.place(x=100, y=230)
    btn_left.place(x=30, y=230)
    btn_right.place(x=170, y=230)
    if config.CAMERA_MODULE:
        btn_video.place(x=320, y=140)  # Define a Button and put it in position
    btn_entry_text.place(x=470, y=300)  # Define a Button and put it in position

    var_R = tk.StringVar()
    var_R.set(0)
    scale_R = tk.Scale(root, label=None, from_=0, to=255, orient=tk.HORIZONTAL, length=505, showvalue=1,
                       tickinterval=None, resolution=1, variable=var_R, troughcolor='#F44336',
                       command=lambda _: send_led('wsR', var_R.get()),
                       fg=COLOR_TEXT, bg=COLOR_BG, highlightthickness=0, width=15)
    scale_R.place(x=30, y=330)  # Define a Scale and put it in position

    var_G = tk.StringVar()
    var_G.set(0)

    scale_G = tk.Scale(root, label=None, from_=0, to=255, orient=tk.HORIZONTAL, length=505, showvalue=1,
                       tickinterval=None, resolution=1, variable=var_G, troughcolor='#00E676',
                       command=lambda _: send_led('wsG', var_G.get()),
                       fg=COLOR_TEXT, bg=COLOR_BG, highlightthickness=0, width=15)
    scale_G.place(x=30, y=370)  # Define a Scale and put it in position

    var_B = tk.StringVar()
    var_B.set(0)

    scale_B = tk.Scale(root, label=None, from_=0, to=255, orient=tk.HORIZONTAL, length=505, showvalue=1,
                       tickinterval=None, resolution=1, variable=var_B, troughcolor='#448AFF',
                       command=lambda _: send_led('wsB', var_B.get()),
                       fg=COLOR_TEXT, bg=COLOR_BG, highlightthickness=0, width=15)
    scale_B.place(x=30, y=410)  # Define a Scale and put it in position

    # Camera scale
    var_pitch = tk.StringVar()
    var_pitch.set(0)
    scale_pitch = tk.Scale(root, label=None, from_=100, to=-100, orient=tk.VERTICAL, length=80, showvalue=1,
                           tickinterval=None, resolution=1, variable=var_pitch, troughcolor='#FFFFFF',
                           command=lambda _: send('move_head_pitch' + ':' + str(var_pitch.get())),
                           fg=COLOR_TEXT, bg=COLOR_BG, highlightthickness=0, width=15)

    var_yaw = tk.StringVar()
    var_yaw.set(0)
    scale_yaw = tk.Scale(root, label=None, from_=100, to=-100, orient=tk.HORIZONTAL, length=80, showvalue=1,
                         tickinterval=None, resolution=1, variable=var_yaw, troughcolor='#FFFFFF',
                         command=lambda _: send('move_head_yaw' + ':' + str(var_yaw.get())),
                         fg=COLOR_TEXT, bg=COLOR_BG, highlightthickness=0, width=15)

    var_height = tk.StringVar()
    var_height.set(50)
    scale_height = tk.Scale(root, label=None, from_=100, to=0, orient=tk.VERTICAL, length=80, showvalue=1,
                            tickinterval=None, resolution=1, variable=var_height, troughcolor='#FFFFFF',
                            command=lambda _: send('move_height' + ':' + str(var_height.get())),
                            fg=COLOR_TEXT, bg=COLOR_BG, highlightthickness=0, width=15)

    canvas_ultra = tk.Canvas(root, bg='#FFFFFF', height=23, width=280, highlightthickness=0)
    canvas_ultra.create_text((90, 11), text='Ultrasonic OFF', fill='#000000')

    if config.CAMERA_MODULE:
        btn_find_color = tk.Button(root, width=10, text='FindColor', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
        btn_find_color.place(x=115, y=465)
        btn_find_color.bind('<ButtonPress-1>', call_find_color)

    if config.CAMERA_MODULE:
        btn_watchdog = tk.Button(root, width=10, text='WatchDog', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
        btn_watchdog.place(x=200, y=465)
        btn_watchdog.bind('<ButtonPress-1>', call_watchdog)

    btn_audio = tk.Button(root, width=10, text='Audio On', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_audio.place(x=370, y=465)
    btn_audio.bind('<ButtonPress-1>', call_audio)

    btn_quit = tk.Button(root, width=10, text='Quit', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_quit.place(x=455, y=465)
    btn_quit.bind('<ButtonPress-1>', terminate)

    btn_forward.bind('<ButtonPress-1>', call_forward)
    btn_backward.bind('<ButtonPress-1>', call_back)
    btn_left.bind('<ButtonPress-1>', call_left)
    btn_right.bind('<ButtonPress-1>', call_right)
    btn_look_up.bind('<ButtonPress-1>', lambda _: send('move_head_up'))
    btn_look_down.bind('<ButtonPress-1>', lambda _: send('move_head_down'))
    btn_look_home.bind('<ButtonPress-1>', lambda _: send('move_head_home'))
    btn_video.bind('<ButtonRelease-1>', lambda _: video.call_video(entry_ip.get()))
    btn_entry_text.bind('<ButtonRelease-1>', send_command)
    btn_forward.bind('<ButtonRelease-1>', call_stop)
    btn_backward.bind('<ButtonRelease-1>', call_stop)
    btn_left.bind('<ButtonRelease-1>', call_turn_stop)
    btn_right.bind('<ButtonRelease-1>', call_turn_stop)
    root.bind_all('<KeyPress-Return>', send_command)
    root.bind_all('<Button-1>', focus)

    # Darkpaw specific GUI
    btn_left_side = tk.Button(root, width=8, text='<--', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_right_side = tk.Button(root, width=8, text='-->', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_look_left = tk.Button(root, width=8, text='Left', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_look_right = tk.Button(root, width=8, text='Right', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_low = tk.Button(root, width=8, text='Low', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_high = tk.Button(root, width=8, text='High', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_Switch_1 = tk.Button(root, width=8, text='Port 1', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_Switch_2 = tk.Button(root, width=8, text='Port 2', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_Switch_3 = tk.Button(root, width=8, text='Port 3', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_left_side.bind('<ButtonPress-1>', call_left_side)
    btn_right_side.bind('<ButtonPress-1>', call_right_side)
    btn_Switch_1.bind('<ButtonPress-1>', call_switch_1)
    btn_Switch_2.bind('<ButtonPress-1>', call_switch_2)
    btn_Switch_3.bind('<ButtonPress-1>', call_switch_3)
    btn_low.bind('<ButtonPress-1>', lambda _: send('move_low'))
    btn_high.bind('<ButtonPress-1>', lambda _: send('move_high'))
    btn_look_left.bind('<ButtonPress-1>', lambda _: send('move_head_left'))
    btn_look_right.bind('<ButtonPress-1>', lambda _: send('move_head_right'))
    btn_left_side.bind('<ButtonRelease-1>', call_stop)
    btn_right_side.bind('<ButtonRelease-1>', call_stop)
    btn_steady = tk.Button(root, width=10, text='Steady', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_steady.bind('<ButtonPress-1>', call_steady)
    btn_find_line = tk.Button(root, width=10, text='FindLine', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_ultra = tk.Button(root, width=10, text='Ultrasonic', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_find_line.bind('<ButtonPress-1>', call_find_line)
    btn_ultra.bind('<ButtonPress-1>', call_ultra)
    btn_roll_left.bind('<ButtonPress-1>', lambda _: send('move_roll_left'))
    btn_roll_right.bind('<ButtonPress-1>', lambda _: send('move_roll_right'))

    # Import last scale parameters
    try:
        ip = str(config_import('IP:'))
        entry_ip.insert(0, ip)
    except:
        logger.warning('Exception reading IP address from file: %s', traceback.format_exc())
        pass
    try:
        var_R.set(int(config_import('SCALE_R:')))
        var_G.set(int(config_import('SCALE_G:')))
        var_B.set(int(config_import('SCALE_B:')))
    except:
        logger.warning('Exception reading LED values from file: %s', traceback.format_exc())
        pass

    # Speed_set entry
    var = 0
    entry_speed = tk.Spinbox(root, width=3, from_=1.0, to=10.0, command=set_speed)
    try:
        entry_speed.place(x=70, y=110)
        entry_speed.delete(0, "end")
        entry_speed.insert(0, config_import('SPEED:'))
    except:
        ", "
        logger.error('Speed parameter read exception: %s', traceback.format_exc())
        pass
    label_speed = tk.Label(root, width=5, text='Speed:', fg=COLOR_TEXT_LABEL, bg=COLOR_BG)
    label_speed.place(x=30, y=110)

    # Flash light entry
    entry_lights = tk.Spinbox(root, width=3, from_=0.0, to=100.0, command=set_light, increment=5)
    label_lights = tk.Label(root, width=5, text='Lights:', fg=COLOR_TEXT_LABEL, bg=COLOR_BG)
    btn_gait = tk.Button(root, width=10, text='Gait', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_gait.bind('<ButtonPress-1>', lambda _: send('gait:'))

    # Darkpaw balance controls
    btn_balance_left = tk.Button(root, width=3, text='', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_balance_right = tk.Button(root, width=3, text='', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_balance_center = tk.Button(root, width=3, text='', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_balance_front = tk.Button(root, width=3, text='', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_balance_back = tk.Button(root, width=3, text='', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_balance_front_left = tk.Button(root, width=3, text='', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_balance_front_right = tk.Button(root, width=3, text='', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_balance_back_left = tk.Button(root, width=3, text='', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_balance_back_right = tk.Button(root, width=3, text='', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')

    btn_balance_left.bind('<ButtonPress-1>', lambda _: send('balance_left'))
    btn_balance_right.bind('<ButtonPress-1>', lambda _: send('balance_right'))
    btn_balance_center.bind('<ButtonPress-1>', lambda _: send('balance_center'))
    btn_balance_front.bind('<ButtonPress-1>', lambda _: send('balance_front'))
    btn_balance_back.bind('<ButtonPress-1>', lambda _: send('balance_back'))
    btn_balance_front_left.bind('<ButtonPress-1>', lambda _: send('balance_front_left'))
    btn_balance_front_right.bind('<ButtonPress-1>', lambda _: send('balance_front_right'))
    btn_balance_back_left.bind('<ButtonPress-1>', lambda _: send('balance_back_left'))
    btn_balance_back_right.bind('<ButtonPress-1>', lambda _: send('balance_back_right'))

    stat_update('-', '-', '-', '-', '-', '-')
    # Read custom gui from config
    for x in config.guiTuple:
        eval(x)
    bind_keys()
    root.protocol("WM_DELETE_WINDOW", lambda: terminate(0))
    root.mainloop()  # Run the mainloop()


def bind_keys():
    """
    Function to read config into global variable keydict and assign keyboard key bindings. Does not read key
    binding configuration if variable is already initialized.
    """
    global root, keydict
    # Read key binding configuration file
    initial = 0
    ptr = 1
    if len(keyDict) == 0:
        logger.info('Key bindings not initialized. Reading key binding configuration file.')
        try:
            with open("key_binding.txt", "r") as f:
                for line in f:
                    if line.find('<Start key binding definition>') == 0:
                        initial = ptr
                    elif line.find('<EOF>') == 0:
                        break
                    if initial > 0:
                        thisList = line.replace(" ", "").replace("\n", "").split(',', 2)
                        if len(thisList) == 2:
                            keyDict[thisList[0]] = thisList[1]
                    ptr += 1
        except:
            logger.error('Error reading configuration file: %s', traceback.format_exc())
            terminate()
    for x, y in keyDict.items():
        logger.debug('Got record: ' + x + ',' + y)
        if y.find('call') == -1:
            eval('root.bind(\'<' + x + '>\', lambda _: send(\'' + y + '\'))')
        else:
            eval('root.bind(\'<' + x + '>\', ' + y + ')')


def unbind_keys():
    """
    Function to remove keyboard key bindings. It reads current key bindings in global variable and unbinds all keys.
    keydict variable must be initialized before calling this function.
    """
    global root, keyDict
    if len(keyDict) != 0:
        for x in keyDict.items():
            root.unbind('<' + x[0] + '>')
        logger.debug('Unbind keyboard binding')
    else:
        logger.error('Key binding dict not yet initialized')


def call_forward(event):
    """
    When this function is called, client commands the robot to move forward
    """
    global move_forward_status
    if move_forward_status == 0:
        send('forward')
        move_forward_status = 1


def call_back(event):
    """
    When this function is called, client commands the robot to move backwards
    :param event: Tkinter event
    """
    global move_backward_status
    if move_backward_status == 0:
        send('backward')
        move_backward_status = 1


def call_stop(event):
    """
    When this function is called, client commands the robot to stop moving
    :param event: Tkinter event
    """
    global move_forward_status, move_backward_status, move_left_status, move_right_status, yaw_left_status, yaw_right_status
    move_forward_status = 0
    move_backward_status = 0
    yaw_left_status = 0
    yaw_right_status = 0
    send('direction_stop')


def call_turn_stop(event):
    """
    When this function is called, client commands the robot to stop moving
    :param event: Tkinter event
    """
    global move_forward_status, move_backward_status, move_left_status, move_right_status, yaw_left_status, yaw_right_status
    move_left_status = 0
    move_right_status = 0
    yaw_left_status = 0
    yaw_right_status = 0
    send('turn_stop')


def call_left(event):
    """
    When this function is called, client commands the robot to turn left
    :param event: Tkinter event
    """
    global move_left_status
    if move_left_status == 0:
        send('left')
        move_left_status = 1


def call_right(event):
    """
    When this function is called, client commands the robot to turn right
    :param event: Tkinter event
    """
    global move_right_status
    if move_right_status == 0:
        send('right')
        move_right_status = 1


def call_left_side(event):
    global yaw_left_status
    if yaw_left_status == 0:
        send('move_left_side')
        yaw_left_status = 1


def call_right_side(event):
    global yaw_right_status
    if yaw_right_status == 0:
        send('move_right_side')
        yaw_right_status = 1


def call_find_color(event):
    if func_mode == 0:
        send('FindColor')
    else:
        send('func_end')


def call_watchdog(event):
    if func_mode == 0:
        send('WatchDog')
    else:
        send('func_end')


def call_switch_1(event):
    if switch_1 == 0:
        send('Switch_1_on')
    else:
        send('Switch_1_off')


def call_switch_2(event):
    if switch_2 == 0:
        send('Switch_2_on')
    else:
        send('Switch_2_off')


def call_switch_3(event):
    if switch_3 == 0:
        send('Switch_3_on')
    else:
        send('Switch_3_off')


def call_steady(event):
    if func_mode == 0:
        send('steady')
    else:
        send('func_end')


def call_ultra(event):
    global ultrasonic_mode
    if ultrasonic_mode == 0:
        send('Ultrasonic')
    else:
        ultra_event.clear()
        send('Ultrasonic_end')


def call_find_line(event):
    if func_mode == 0:
        send('FindLine')
    else:
        send('func_end')


def call_audio(event):
    global btn_audio
    if btn_audio.cget("bg") == config.COLOR_BTN:
        send('stream_audio')
    else:
        send('stream_audio_end')


def all_btn_red():
    """
    Returns all special function buttons to red state
    """
    btn_find_color.config(bg=COLOR_BTN_RED, fg='#000000')
    btn_watchdog.config(bg=COLOR_BTN_RED, fg='#000000')
    try:
        btn_steady.config(bg=COLOR_BTN_RED, fg='#000000')
    except NameError:
        pass


def all_btn_normal():
    """
    Returns all function buttons to normal state
    """
    global func_mode, btn_steady
    btn_find_color.config(bg=COLOR_BTN, fg=COLOR_TEXT)
    btn_watchdog.config(bg=COLOR_BTN, fg=COLOR_TEXT)
    func_mode = 0
    try:
        btn_steady.config(bg=COLOR_BTN, fg=COLOR_TEXT)
    except NameError:
        pass


def button_update(status_data):
    """
    This function is called to update the GUI according to data received from robot.
    :param status_data: String data received from robot
    """
    global btn_find_color, btn_watchdog, btn_steady, btn_ultra, btn_Switch_1, btn_Switch_2, btn_Switch_3, \
        btn_audio, btn_quit, btn_video, btn_find_line, func_mode, ultrasonic_mode, switch_1, switch_2, switch_3
    try:
        if 'FindColor' == status_data:
            func_mode = 1
            all_btn_red()
            btn_find_color.config(bg=COLOR_BTN_ACT)
        elif 'WatchDog' == status_data:
            func_mode = 1
            all_btn_red()
            btn_watchdog.config(bg=COLOR_BTN_ACT)
        elif 'steady' == status_data:
            func_mode = 1
            all_btn_red()
            btn_steady.config(bg=COLOR_BTN_ACT)
        elif 'Ultrasonic' == status_data:
            btn_ultra.config(bg=COLOR_BTN_ACT)
            start_ultra()
            try:
                btn_ultra.config(bg=COLOR_BTN_RED)
            except NameError:
                pass
        elif 'Ultrasonic_end' == status_data and config.ULTRA_SENSOR:
            ultra_event.clear()
            ultrasonic_mode = 0
            try:
                btn_ultra.config(bg=COLOR_BTN)
            except NameError:
                pass
        elif 'Switch_1_on' == status_data:
            switch_1 = 1
            btn_Switch_1.config(bg=COLOR_SWT_ACT)
        elif 'Switch_2_on' == status_data:
            switch_2 = 1
            btn_Switch_2.config(bg=COLOR_SWT_ACT)
        elif 'Switch_3_on' == status_data:
            btn_Switch_3.config(bg=COLOR_SWT_ACT)
            switch_3 = 1
        elif 'Switch_1_off' == status_data:
            switch_1 = 0
            btn_Switch_1.config(bg=COLOR_BTN)
        elif 'Switch_2_off' == status_data:
            switch_2 = 0
            btn_Switch_2.config(bg=COLOR_BTN)
        elif 'Switch_3_off' == status_data:
            switch_3 = 0
            btn_Switch_3.config(bg=COLOR_BTN)
        elif 'func_end' == status_data:
            all_btn_normal()
        elif 'stream_audio' == status_data:
            btn_audio.config(bg=COLOR_SWT_ACT)
        elif 'stream_audio_end' == status_data:
            btn_audio.config(bg=COLOR_BTN)
        elif 'start_video' == status_data:
            pass
        elif 'stop_video' == status_data:
            pass
        elif 'disconnect' == status_data:
            pass
        else:
            logger.warning('Unknown button status update: %s' % status_data)
    except:
        logger.error('Button status update exception: %s', traceback.format_exc())


def focus(event):
    """
    This method is used to get
    the name of the widget
    which currently has the focus
    by clicking Mouse Button-1
    :param event: Tkinter event
    """
    if str(root.focus_get()) == '.!entry2':
        unbind_keys()


def stat_update(cpu_temp, cpu_use, ram_use, voltage, current, ambient):
    """
    This function updates the GUI label from statistical data received from robot.
    :param cpu_temp: CPU Temperature value
    :param cpu_use: CPU usage value
    :param ram_use: RAM usage value
    :param voltage: Bus voltage value (V)
    :param current: Bus current value (mA)
    """
    label_cpu_temp.config(text='CPU Temp: %s℃' % cpu_temp)
    label_cpu_use.config(text='CPU Usage: %s' % cpu_use)
    label_ram_use.config(text='RAM Usage: %s' % ram_use)
    label_voltage.config(text='Voltage: %s' % voltage)
    label_current.config(text='Current: %s' % current)
    label_ambient.config(text='Ambient: %s℃' % ambient)


def send_led(index, value):
    global led_sleep
    if led_sleep == 0:
        led_sleep = value
        send(index + ' %s ' % led_sleep)
        time.sleep(0.2)
        led_sleep = 0
    else:
        pass


def send_command(event):
    """
    This function sends TTS string to robot when connection is established.
    :param event: Not used
    """
    if entry_text.get() != '' and connect_event.is_set():
        if not config.DEBUG_MODE:
            send('espeak:' + entry_text.get())
        else:
            send(entry_text.get())
        entry_ip.focus_set()
        entry_text.delete(0, 'end')
    elif not connect_event.is_set():
        logger.warning('Unable to send, not connected')
    else:
        pass
    bind_keys()


def connect_init(ip_address):
    label_ip_1.config(text='Connected')
    label_ip_1.config(bg='#558B2F')
    entry_text.config(state='normal')
    btn_connect.config(state='normal')
    btn_connect.config(text='Disconnect')
    time.sleep(0.5)
    # Send initial values
    send(' wsR ' + var_R.get())
    time.sleep(0.5)
    send(' wsG ' + var_G.get())
    time.sleep(0.5)
    send(' wsB ' + var_B.get())
    time.sleep(0.5)
    set_speed(True)
    time.sleep(0.5)
    set_light(True)


def set_speed(force=False):
    """
    This method reads the entry input and sends a message to the server.
    It does not send if value was unchanged.
    Writes new value to global variable.
    """
    global entry_speed, speed_value
    set_value = entry_speed.get()
    if force or (not set_value == '' and speed_value != set_value):
        send(' speed:' + set_value)
        speed_value = set_value
    entry_ip.focus_set()


def set_light(force=False):
    """
    This method reads the entry input and sends a message to the server.
    It does not send if value was unchanged.
    Writes new value to global variable.
    """
    global entry_lights, light_value
    set_value = entry_lights.get()
    if force or light_value != set_value:
        send('light:' + set_value)
        light_value = set_value
    entry_ip.focus_set()
