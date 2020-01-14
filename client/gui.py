#!/usr/bin/env/python
# E-mail      : sect16@gmail.com
# Author      : Chin Pin Hon
# Date        : 14.01.2020

"""
GUI layout definition
"""

import logging
import time
import tkinter as tk
import traceback

import coloredlogs

import config
import video
from functions import send, connect, terminate, ultra_event, start_ultra, connect_event

root = tk.Tk()  # Define a window named root
# Create a logger object.
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG',
                    fmt='%(asctime)s.%(msecs)03d %(levelname)7s %(thread)5d --- [%(threadName)16s] %(funcName)-39s: %(message)s')
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
smooth_mode = 0
sport_mode_on = 0
ultrasonic_mode = 0

COLOR_SWT_ACT = config.COLOR_SWT_ACT
COLOR_BTN_ACT = config.COLOR_BTN_ACT
COLOR_BG = config.COLOR_BG  # Set background color
COLOR_TEXT = config.COLOR_TEXT
COLOR_BTN = config.COLOR_BTN
label_bg = config.COLOR_BTN
COLOR_BTN_RED = config.COLOR_BTN_RED


def loop():  # GUI
    """
    Main GUI layout
    """
    global root, e1, e2, label_ip_1, label_ip_2, COLOR_BTN, COLOR_TEXT, btn_connect, \
        label_cpu_temp, label_cpu_use, label_ram_use, COLOR_TEXT, var_R, var_B, var_G, btn_steady, btn_find_color, \
        btn_watchdog, btn_smooth, btn_audio, btn_quit, btn_Switch_1, btn_Switch_2, btn_Switch_3, btn_FPV, \
        btn_ultra, btn_find_line, btn_sport, canvas_ultra
    root.geometry('565x510')  # Main window size
    root.config(bg=COLOR_BG)  # Set the background color of root window
    try:
        logo = tk.PhotoImage(file='logo.png')  # Define the picture of logo (Only supports '.png' and '.gif')
        l_logo = tk.Label(root, image=logo, bg=COLOR_BG)  # Set a label to show the logo picture
        l_logo.place(x=60, y=7)  # Place the Label in a right position
    except:
        pass
    label_cpu_temp = tk.Label(root, width=18, text='CPU Temp:', fg=COLOR_TEXT, bg='#212121')
    label_cpu_use = tk.Label(root, width=18, text='CPU Usage:', fg=COLOR_TEXT, bg='#212121')
    label_ram_use = tk.Label(root, width=18, text='RAM Usage:', fg=COLOR_TEXT, bg='#212121')
    label_ip_0 = tk.Label(root, width=18, text='Status', fg=COLOR_TEXT, bg=COLOR_BTN)
    label_ip_1 = tk.Label(root, width=18, text='Disconnected', fg=COLOR_TEXT, bg='#F44336')
    label_ip_2 = tk.Label(root, width=18, text='Use default IP', fg=COLOR_TEXT, bg=COLOR_BTN)
    label_ip_3 = tk.Label(root, width=10, text='IP Address:', fg=COLOR_TEXT, bg='#000000')
    label_open_cv = tk.Label(root, width=28, text='OpenCV Status', fg=COLOR_TEXT, bg=COLOR_BTN)
    label_cpu_temp.place(x=400, y=15)  # Define a Label and put it in position
    label_cpu_use.place(x=400, y=45)  # Define a Label and put it in position
    label_ram_use.place(x=400, y=75)  # Define a Label and put it in position
    label_ip_0.place(x=30, y=110)  # Define a Label and put it in position
    label_ip_1.place(x=400, y=110)  # Define a Label and put it in position
    label_ip_2.place(x=400, y=145)  # Define a Label and put it in position
    label_ip_3.place(x=175, y=15)  # Define a Label and put it in position
    label_open_cv.place(x=180, y=110)  # Define a Label and put it in position

    e1 = tk.Entry(root, show=None, width=16, bg='#FFFFFF', fg='#000000', disabledbackground=config.COLOR_GREY,
                  state='normal')
    e2 = tk.Entry(root, show=None, width=71, bg='#FFFFFF', fg='#000000', disabledbackground=config.COLOR_GREY,
                  state='disabled')
    e1.place(x=180, y=40)  # Define a Entry and put it in position
    e2.place(x=30, y=305)  # Define a Entry and put it in position

    btn_connect = tk.Button(root, width=8, height=2, text='Connect', fg=COLOR_TEXT, bg=COLOR_BTN,
                            command=connect,
                            relief='ridge')
    btn0 = tk.Button(root, width=8, text='Forward', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn1 = tk.Button(root, width=8, text='Backward', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn2 = tk.Button(root, width=8, text='Left', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn3 = tk.Button(root, width=8, text='Right', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_up = tk.Button(root, width=8, text='Up', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_down = tk.Button(root, width=8, text='Down', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_home = tk.Button(root, width=8, text='Home', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_FPV = tk.Button(root, width=8, text='Video', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_e2 = tk.Button(root, width=10, text='Send', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')

    btn_connect.place(x=315, y=15)  # Define a Button and put it in position
    btn0.place(x=100, y=195)
    btn1.place(x=100, y=230)
    btn2.place(x=30, y=230)
    btn3.place(x=170, y=230)
    btn_FPV.place(x=315, y=60)  # Define a Button and put it in position
    btn_e2.place(x=470, y=300)  # Define a Button and put it in position
    btn_up.place(x=400, y=195)
    btn_down.place(x=400, y=265)
    btn_home.place(x=400, y=230)

    var_R = tk.StringVar()
    var_R.set(0)
    scale_R = tk.Scale(root, label=None, from_=0, to=255, orient=tk.HORIZONTAL, length=505, showvalue=1,
                       tickinterval=None, resolution=1, variable=var_R, troughcolor='#F44336', command=set_R,
                       fg=COLOR_TEXT, bg=COLOR_BG, highlightthickness=0, width=15)
    scale_R.place(x=30, y=330)  # Define a Scale and put it in position

    var_G = tk.StringVar()
    var_G.set(0)

    scale_G = tk.Scale(root, label=None, from_=0, to=255, orient=tk.HORIZONTAL, length=505, showvalue=1,
                       tickinterval=None, resolution=1, variable=var_G, troughcolor='#00E676', command=set_G,
                       fg=COLOR_TEXT, bg=COLOR_BG, highlightthickness=0, width=15)
    scale_G.place(x=30, y=370)  # Define a Scale and put it in position

    var_B = tk.StringVar()
    var_B.set(0)

    scale_B = tk.Scale(root, label=None, from_=0, to=255, orient=tk.HORIZONTAL, length=505, showvalue=1,
                       tickinterval=None, resolution=1, variable=var_B, troughcolor='#448AFF', command=set_B,
                       fg=COLOR_TEXT, bg=COLOR_BG, highlightthickness=0, width=15)
    scale_B.place(x=30, y=410)  # Define a Scale and put it in position

    canvas_ultra = tk.Canvas(root, bg='#FFFFFF', height=23, width=352, highlightthickness=0)
    canvas_ultra.create_text((90, 11), text='Ultrasonic OFF', fill='#000000')
    # Canvas testing
    # canvas_ultra.place(x=30, y=145)
    # canvas_rec = canvas_ultra.create_rectangle(0, 0, (352 - int(float(0.75) * 352 / 3)), 30, fill='#448AFF', width=0)
    # canvas_text = canvas_ultra.create_text((90, 11), text='Ultrasonic Output: %sm' % 0.75, fill=COLOR_TEXT)

    btn_find_color = tk.Button(root, width=10, text='FindColor', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_find_color.place(x=115, y=465)
    btn_find_color.bind('<ButtonPress-1>', call_find_color)

    btn_watchdog = tk.Button(root, width=10, text='WatchDog', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_watchdog.place(x=200, y=465)
    btn_watchdog.bind('<ButtonPress-1>', call_watchdog)

    btn_audio = tk.Button(root, width=10, text='Audio On', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_audio.place(x=370, y=465)
    btn_audio.bind('<ButtonPress-1>', lambda _: send('stream_audio'))

    btn_quit = tk.Button(root, width=10, text='Quit', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_quit.place(x=455, y=465)
    btn_quit.bind('<ButtonPress-1>', terminate)

    btn0.bind('<ButtonPress-1>', call_forward)
    btn1.bind('<ButtonPress-1>', call_back)
    btn2.bind('<ButtonPress-1>', call_left)
    btn3.bind('<ButtonPress-1>', call_right)
    btn_up.bind('<ButtonPress-1>', lambda _: send('headup'))
    btn_down.bind('<ButtonPress-1>', lambda _: send('headdown'))
    btn_home.bind('<ButtonPress-1>', lambda _: send('headhome'))
    btn_FPV.bind('<ButtonRelease-1>', video.call_fpv)
    btn_e2.bind('<ButtonRelease-1>', send_command)
    btn0.bind('<ButtonRelease-1>', call_stop)
    btn1.bind('<ButtonRelease-1>', call_stop)
    btn2.bind('<ButtonRelease-1>', call_turn_stop)
    btn3.bind('<ButtonRelease-1>', call_turn_stop)
    root.bind_all('<KeyPress-Return>', send_command)
    root.bind_all('<Button-1>', focus)

    # Darkpaw specific GUI
    btn_left_side = tk.Button(root, width=8, text='<--', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_right_side = tk.Button(root, width=8, text='-->', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_left = tk.Button(root, width=8, text='Left', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_right = tk.Button(root, width=8, text='Right', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
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
    btn_low.bind('<ButtonPress-1>', lambda _: send('low'))
    btn_high.bind('<ButtonPress-1>', lambda _: send('high'))
    btn_left.bind('<ButtonPress-1>', lambda _: send('headleft'))
    btn_right.bind('<ButtonPress-1>', lambda _: send('headright'))
    btn_left_side.bind('<ButtonRelease-1>', call_turn_stop)
    btn_right_side.bind('<ButtonRelease-1>', call_turn_stop)
    btn_steady = tk.Button(root, width=10, text='Steady', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_steady.bind('<ButtonPress-1>', call_steady)
    btn_smooth = tk.Button(root, width=10, text='Smooth', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_smooth.bind('<ButtonPress-1>', call_smooth)

    btn_sport = tk.Button(root, width=8, text='GT', bg='#F44336', fg='#FFFFFF', relief='ridge')
    btn_find_line = tk.Button(root, width=10, text='FindLine', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_ultra = tk.Button(root, width=10, text='Ultrasonic', fg=COLOR_TEXT, bg=COLOR_BTN, relief='ridge')
    btn_find_line.bind('<ButtonPress-1>', call_find_line)
    btn_ultra.bind('<ButtonPress-1>', call_ultra)
    btn_sport.bind('<ButtonPress-1>', call_sport_mode)

    exec(open("custom.py").read())

    bind_keys()
    root.protocol("WM_DELETE_WINDOW", lambda: terminate(0))
    root.mainloop()  # Run the mainloop()


def bind_keys():
    """
    Function to assign keyboard key bindings
    """
    global root
    exec(open("key_bind.py").read())
    logger.debug('Bind KeyPress')


def unbind_keys():
    """
    Function to remove keyboard key bindings
    """
    global root
    root.unbind('<KeyPress-w>')
    root.unbind('<KeyPress-s>')
    root.unbind('<KeyPress-a>')
    root.unbind('<KeyPress-d>')
    root.unbind('<KeyRelease-w>')
    root.unbind('<KeyRelease-s>')
    root.unbind('<KeyRelease-a>')
    root.unbind('<KeyRelease-d>')
    root.unbind('<KeyPress-i>')
    root.unbind('<KeyPress-k>')
    root.unbind('<KeyPress-h>')
    root.unbind('<KeyPress-z>')
    root.unbind('<KeyPress-x>')
    root.unbind('<KeyPress-c>')
    root.unbind('<KeyPress-v>')
    root.unbind('<KeyPress-b>')
    root.unbind('<KeyPress-q>')
    root.unbind('<KeyPress-e>')
    root.unbind('<KeyRelease-q>')
    root.unbind('<KeyRelease-e>')
    root.unbind('<KeyPress-j>')
    root.unbind('<KeyPress-l>')
    root.unbind('<KeyPress-u>')
    root.unbind('<KeyPress-o>')
    logger.debug('Unbind KeyPress')


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
    send('DS')


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
    send('TS')


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
        send('leftside')
        yaw_left_status = 1


def call_right_side(event):
    global yaw_right_status
    if yaw_right_status == 0:
        send('rightside')
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


def call_smooth(event):
    if smooth_mode == 0:
        send('Smooth_on')
    else:
        send('Smooth_off')


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


def call_sport_mode(event):
    global sport_mode_on
    if sport_mode_on:
        send('SportModeOff')
    else:
        send('SportModeOn')


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
    global func_mode, smooth_mode, btn_steady
    btn_find_color.config(bg=COLOR_BTN, fg=COLOR_TEXT)
    btn_watchdog.config(bg=COLOR_BTN, fg=COLOR_TEXT)
    func_mode = 0
    smooth_mode = 0
    try:
        btn_steady.config(bg=COLOR_BTN, fg=COLOR_TEXT)
    except NameError:
        pass


def button_update(status_data):
    """
    This function is called to update the GUI according to data received from robot.
    :param status_data: String data received from robot
    """
    global root, e1, e2, label_ip_1, label_ip_2, COLOR_BTN, COLOR_TEXT, btn_connect, \
        label_cpu_temp, label_cpu_use, label_ram_use, COLOR_TEXT, var_R, var_B, var_G, btn_steady, btn_find_color, \
        btn_watchdog, btn_smooth, btn_audio, btn_quit, btn_Switch_1, btn_Switch_2, btn_Switch_3, btn_FPV, \
        btn_ultra, btn_find_line, btn_sport, func_mode, switch_1, switch_2, switch_3, smooth_mode, ultrasonic_mode
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
                btn_ultra.config(bg=COLOR_BTN_RED, fg='#000000')
            except NameError:
                pass
        elif 'Ultrasonic_end' == status_data and config.ULTRA_SENSOR is not None:
            pass
        elif 'Switch_3_on' == status_data:
            btn_Switch_3.config(bg=COLOR_SWT_ACT)
            switch_3 = 1
        elif 'Switch_2_on' == status_data:
            switch_2 = 1
            btn_Switch_2.config(bg=COLOR_SWT_ACT)
        elif 'Switch_1_on' == status_data:
            switch_1 = 1
            btn_Switch_1.config(bg=COLOR_SWT_ACT)
        elif 'Switch_3_off' == status_data:
            switch_3 = 0
            btn_Switch_3.config(bg=COLOR_BTN)
        elif 'Switch_2_off' == status_data:
            switch_2 = 0
            btn_Switch_2.config(bg=COLOR_BTN)
        elif 'Switch_1_off' == status_data:
            switch_1 = 0
            btn_Switch_1.config(bg=COLOR_BTN)
        elif 'Smooth_on' == status_data:
            smooth_mode = 1
            btn_smooth.config(bg=COLOR_SWT_ACT)
        elif 'Smooth_off' == status_data:
            smooth_mode = 0
            btn_smooth.config(bg=COLOR_BTN)
        elif 'func_end' == status_data:
            all_btn_normal()
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


def stat_update(cpu_temp, cpu_use, ram_use):
    """
    This function updates the GUI label from statistical data received from robot.
    :param cpu_temp: CPU Temperature value
    :param cpu_use: CPU usage value
    :param ram_use: RAM usage value
    """
    label_cpu_temp.config(text='CPU Temp: %s℃' % cpu_temp)
    label_cpu_use.config(text='CPU Usage: %s' % cpu_use)
    label_ram_use.config(text='RAM Usage: %s' % ram_use)


def set_R(event):
    time.sleep(0.03)
    send('wsR %s' % var_R.get())


def set_G(event):
    time.sleep(0.03)
    send('wsG %s' % var_G.get())


def set_B(event):
    time.sleep(0.03)
    send('wsB %s' % var_B.get())


def send_command(event):
    """
    This function sends TTS string to robot when connection is established. Nothing is sent is connection off.
    :param event:
    """
    if e2.get() != '' and connect_event.is_set():
        send(e2.get())
        e1.focus_set()
        e2.delete(0, 'end')
    else:
        logger.warning('Unable to send, not connected')
    bind_keys()