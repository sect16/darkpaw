import logging
import tkinter as tk

import coloredlogs

import config
import video

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

color_swt_act = config.COLOR_SWT_ACT
color_btn_act = config.COLOR_BTN_ACT
color_bg = config.COLOR_BG  # Set background color
color_text = config.COLOR_TEXT
color_btn = config.COLOR_BTN
label_bg = config.LABEL_BG


def loop():  # GUI
    global interface, root, e1, e2, label_ip_1, label_ip_2, color_btn, color_text, btn_connect, \
        label_cpu_temp, label_cpu_use, label_ram_use, color_text, var_R, var_B, var_G, btn_steady, btn_find_color, \
        btn_watchdog, btn_smooth, btn_audio, btn_quit, btn_Switch_1, btn_Switch_2, btn_Switch_3, btn_FPV
    root.title('DarkPaw')  # Main window title
    root.geometry('565x510')  # Main window size
    root.config(bg=color_bg)  # Set the background color of root window
    try:
        logo = tk.PhotoImage(file='logo.png')  # Define the picture of logo (Only supports '.png' and '.gif')
        l_logo = tk.Label(root, image=logo, bg=color_bg)  # Set a label to show the logo picture
        l_logo.place(x=60, y=7)  # Place the Label in a right position
    except:
        pass
    label_cpu_temp = tk.Label(root, width=18, text='CPU Temp:', fg=color_text, bg='#212121')
    label_cpu_use = tk.Label(root, width=18, text='CPU Usage:', fg=color_text, bg='#212121')
    label_ram_use = tk.Label(root, width=18, text='RAM Usage:', fg=color_text, bg='#212121')
    label_ip_0 = tk.Label(root, width=18, text='Status', fg=color_text, bg=color_btn)
    label_ip_1 = tk.Label(root, width=18, text='Disconnected', fg=color_text, bg='#F44336')
    label_ip_2 = tk.Label(root, width=18, text='Use default IP', fg=color_text, bg=color_btn)
    label_ip_3 = tk.Label(root, width=10, text='IP Address:', fg=color_text, bg='#000000')
    label_open_cv = tk.Label(root, width=28, text='OpenCV Status', fg=color_text, bg=color_btn)
    label_cpu_temp.place(x=400, y=15)  # Define a Label and put it in position
    label_cpu_use.place(x=400, y=45)  # Define a Label and put it in position
    label_ram_use.place(x=400, y=75)  # Define a Label and put it in position
    label_ip_0.place(x=30, y=110)  # Define a Label and put it in position
    label_ip_1.place(x=400, y=110)  # Define a Label and put it in position
    label_ip_2.place(x=400, y=145)  # Define a Label and put it in position
    label_ip_3.place(x=175, y=15)  # Define a Label and put it in position
    label_open_cv.place(x=180, y=110)  # Define a Label and put it in position

    e1 = tk.Entry(root, show=None, width=16, bg="#37474F", fg='#eceff1')
    e2 = tk.Entry(root, show=None, width=71, bg="#37474F", fg='#eceff1')
    e1.place(x=180, y=40)  # Define a Entry and put it in position
    e2.place(x=30, y=305)  # Define a Entry and put it in position

    btn_connect = tk.Button(root, width=8, height=2, text='Connect', fg=color_text, bg=color_btn,
                            command=interface.connect,
                            relief='ridge')
    btn0 = tk.Button(root, width=8, text='Forward', fg=color_text, bg=color_btn, relief='ridge')
    btn1 = tk.Button(root, width=8, text='Backward', fg=color_text, bg=color_btn, relief='ridge')
    btn2 = tk.Button(root, width=8, text='Left', fg=color_text, bg=color_btn, relief='ridge')
    btn3 = tk.Button(root, width=8, text='Right', fg=color_text, bg=color_btn, relief='ridge')
    btn_up = tk.Button(root, width=8, text='Up', fg=color_text, bg=color_btn, relief='ridge')
    btn_down = tk.Button(root, width=8, text='Down', fg=color_text, bg=color_btn, relief='ridge')
    btn_home = tk.Button(root, width=8, text='Home', fg=color_text, bg=color_btn, relief='ridge')
    btn_FPV = tk.Button(root, width=8, text='Video', fg=color_text, bg=color_btn, relief='ridge')
    btn_e2 = tk.Button(root, width=10, text='Send', fg=color_text, bg=color_btn, relief='ridge')
    btn_left_side = tk.Button(root, width=8, text='<--', fg=color_text, bg=color_btn, relief='ridge')
    btn_right_side = tk.Button(root, width=8, text='-->', fg=color_text, bg=color_btn, relief='ridge')
    btn_left = tk.Button(root, width=8, text='Left', fg=color_text, bg=color_btn, relief='ridge')
    btn_right = tk.Button(root, width=8, text='Right', fg=color_text, bg=color_btn, relief='ridge')
    btn_low = tk.Button(root, width=8, text='Low', fg=color_text, bg=color_btn, relief='ridge')
    btn_high = tk.Button(root, width=8, text='High', fg=color_text, bg=color_btn, relief='ridge')
    btn_Switch_1 = tk.Button(root, width=8, text='Port 1', fg=color_text, bg=color_btn, relief='ridge')
    btn_Switch_2 = tk.Button(root, width=8, text='Port 2', fg=color_text, bg=color_btn, relief='ridge')
    btn_Switch_3 = tk.Button(root, width=8, text='Port 3', fg=color_text, bg=color_btn, relief='ridge')

    btn_connect.place(x=315, y=15)  # Define a Button and put it in position
    btn0.place(x=100, y=195)
    btn1.place(x=100, y=230)
    btn2.place(x=30, y=230)
    btn3.place(x=170, y=230)
    btn_FPV.place(x=315, y=60)  # Define a Button and put it in position
    btn_e2.place(x=470, y=300)  # Define a Button and put it in position
    btn_up.place(x=400, y=195)
    btn_down.place(x=400, y=265)
    btn_left_side.place(x=30, y=195)
    btn_right_side.place(x=170, y=195)
    btn_home.place(x=400, y=230)
    btn_low.place(x=330, y=230)
    btn_high.place(x=470, y=230)
    btn_left.place(x=330, y=195)
    btn_right.place(x=470, y=195)
    btn_Switch_1.place(x=30, y=265)
    btn_Switch_2.place(x=100, y=265)
    btn_Switch_3.place(x=170, y=265)

    var_R = tk.StringVar()
    var_R.set(0)
    scale_R = tk.Scale(root, label=None, from_=0, to=255, orient=tk.HORIZONTAL, length=505, showvalue=1,
                       tickinterval=None, resolution=1, variable=var_R, troughcolor='#F44336', command=set_R,
                       fg=color_text, bg=color_bg, highlightthickness=0)
    scale_R.place(x=30, y=330)  # Define a Scale and put it in position

    var_G = tk.StringVar()
    var_G.set(0)

    scale_G = tk.Scale(root, label=None, from_=0, to=255, orient=tk.HORIZONTAL, length=505, showvalue=1,
                       tickinterval=None, resolution=1, variable=var_G, troughcolor='#00E676', command=set_G,
                       fg=color_text, bg=color_bg, highlightthickness=0)
    scale_G.place(x=30, y=360)  # Define a Scale and put it in position

    var_B = tk.StringVar()
    var_B.set(0)

    scale_B = tk.Scale(root, label=None, from_=0, to=255, orient=tk.HORIZONTAL, length=505, showvalue=1,
                       tickinterval=None, resolution=1, variable=var_B, troughcolor='#448AFF', command=set_B,
                       fg=color_text, bg=color_bg, highlightthickness=0)
    scale_B.place(x=30, y=390)  # Define a Scale and put it in position

    canvas_cover = tk.Canvas(root, bg=color_bg, height=30, width=510, highlightthickness=0)
    canvas_cover.place(x=30, y=420)

    btn_find_color = tk.Button(root, width=10, text='FindColor', fg=color_text, bg=color_btn, relief='ridge')
    btn_find_color.place(x=115, y=445)
    btn_find_color.bind('<ButtonPress-1>', call_find_color)

    btn_watchdog = tk.Button(root, width=10, text='WatchDog', fg=color_text, bg=color_btn, relief='ridge')
    btn_watchdog.place(x=200, y=445)
    btn_watchdog.bind('<ButtonPress-1>', call_watchdog)

    btn_audio = tk.Button(root, width=10, text='Audio On', fg=color_text, bg=color_btn, relief='ridge')
    btn_audio.place(x=370, y=445)
    btn_audio.bind('<ButtonPress-1>', call_stream_audio)

    btn_quit = tk.Button(root, width=10, text='Quit', fg=color_text, bg=color_btn, relief='ridge')
    btn_quit.place(x=455, y=445)
    btn_quit.bind('<ButtonPress-1>', interface.terminate)

    btn_steady = tk.Button(root, width=10, text='Steady', fg=color_text, bg=color_btn, relief='ridge')
    btn_steady.place(x=30, y=445)
    btn_steady.bind('<ButtonPress-1>', call_steady)

    btn_smooth = tk.Button(root, width=10, text='Smooth', fg=color_text, bg=color_btn, relief='ridge')
    btn_smooth.place(x=285, y=445)
    btn_smooth.bind('<ButtonPress-1>', call_smooth)

    btn0.bind('<ButtonPress-1>', call_forward)
    btn1.bind('<ButtonPress-1>', call_back)
    btn2.bind('<ButtonPress-1>', call_left)
    btn3.bind('<ButtonPress-1>', call_right)
    btn_up.bind('<ButtonPress-1>', call_head_up)
    btn_down.bind('<ButtonPress-1>', call_head_down)
    btn_home.bind('<ButtonPress-1>', call_head_home)
    btn_FPV.bind('<ButtonRelease-1>', video.call_fpv)
    btn_e2.bind('<ButtonRelease-1>', send_command)
    btn0.bind('<ButtonRelease-1>', call_stop)
    btn1.bind('<ButtonRelease-1>', call_stop)
    btn2.bind('<ButtonRelease-1>', call_turn_stop)
    btn3.bind('<ButtonRelease-1>', call_turn_stop)
    btn_left_side.bind('<ButtonPress-1>', call_left_side)
    btn_right_side.bind('<ButtonPress-1>', call_right_side)
    btn_Switch_1.bind('<ButtonPress-1>', call_switch_1)
    btn_Switch_2.bind('<ButtonPress-1>', call_switch_2)
    btn_Switch_3.bind('<ButtonPress-1>', call_switch_3)
    btn_low.bind('<ButtonPress-1>', call_head_low)
    btn_high.bind('<ButtonPress-1>', call_head_high)
    btn_left.bind('<ButtonPress-1>', call_head_left)
    btn_right.bind('<ButtonPress-1>', call_head_right)
    btn_left_side.bind('<ButtonRelease-1>', call_turn_stop)
    btn_right_side.bind('<ButtonRelease-1>', call_turn_stop)
    root.bind_all('<KeyPress-Return>', send_command)
    root.bind_all('<Button-1>', focus)
    bind_keys()
    root.protocol("WM_DELETE_WINDOW", lambda: interface.terminate(0))
    root.mainloop()  # Run the mainloop()


def bind_keys():
    global root
    root.bind('<KeyPress-w>', call_forward)
    root.bind('<KeyPress-s>', call_back)
    root.bind('<KeyPress-a>', call_left)
    root.bind('<KeyPress-d>', call_right)

    root.bind('<KeyPress-q>', call_left_side)
    root.bind('<KeyPress-e>', call_right_side)
    root.bind('<KeyRelease-q>', call_turn_stop)
    root.bind('<KeyRelease-e>', call_turn_stop)

    root.bind('<KeyRelease-w>', call_stop)
    root.bind('<KeyRelease-s>', call_stop)
    root.bind('<KeyRelease-a>', call_turn_stop)
    root.bind('<KeyRelease-d>', call_turn_stop)

    root.bind('<KeyPress-h>', call_head_home)
    root.bind('<KeyPress-i>', call_head_up)
    root.bind('<KeyPress-k>', call_head_down)
    root.bind('<KeyPress-x>', call_find_color)
    root.bind('<KeyPress-c>', call_watchdog)
    root.bind('<KeyPress-b>', call_stream_audio)
    root.bind('<KeyPress-j>', call_head_left)
    root.bind('<KeyPress-l>', call_head_right)
    root.bind('<KeyPress-u>', call_head_low)
    root.bind('<KeyPress-o>', call_head_high)
    root.bind('<KeyPress-z>', call_steady)
    root.bind('<KeyPress-v>', call_smooth)
    logger.debug('Bind KeyPress')


def unbind_keys():
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


def call_forward(event):  # When this function is called,client commands the car to move forward
    global move_forward_status
    if move_forward_status == 0:
        interface.send('forward')
        move_forward_status = 1


def call_back(event):  # When this function is called,client commands the car to move backward
    global move_backward_status
    if move_backward_status == 0:
        interface.send('backward')
        move_backward_status = 1


def call_stop(event):  # When this function is called,client commands the car to stop moving
    global move_forward_status, move_backward_status, move_left_status, move_right_status, yaw_left_status, yaw_right_status
    move_forward_status = 0
    move_backward_status = 0
    interface.send('DS')


def call_turn_stop(event):  # When this function is called,client commands the car to stop moving
    global move_forward_status, move_backward_status, move_left_status, move_right_status, yaw_left_status, yaw_right_status
    move_left_status = 0
    move_right_status = 0
    yaw_left_status = 0
    yaw_right_status = 0
    interface.send('TS')


def call_left(event):  # When this function is called,client commands the car to turn left
    global move_left_status
    if move_left_status == 0:
        interface.send('left')
        move_left_status = 1


def call_right(event):  # When this function is called,client commands the car to turn right
    global move_right_status
    if move_right_status == 0:
        interface.send('right')
        move_right_status = 1


def call_left_side(event):
    global yaw_left_status
    if yaw_left_status == 0:
        interface.send('leftside')
        yaw_left_status = 1


def call_right_side(event):
    global yaw_right_status
    if yaw_right_status == 0:
        interface.send('rightside')
        yaw_right_status = 1


def call_head_up(event):
    interface.send('headup')


def call_head_down(event):
    interface.send('headdown')


def call_head_left(event):
    interface.send('headleft')


def call_head_right(event):
    interface.send('headright')


def call_head_low(event):
    interface.send('low')


def call_head_high(event):
    interface.send('high')


def call_head_home(event):
    interface.send('headhome')


def call_steady(event):
    if func_mode == 0:
        interface.send('steady')
    else:
        interface.send('func_end')


def call_find_color(event):
    if func_mode == 0:
        interface.send('FindColor')
    else:
        interface.send('func_end')


def call_watchdog(event):
    if func_mode == 0:
        interface.send('WatchDog')
    else:
        interface.send('func_end')


def call_smooth(event):
    if smooth_mode == 0:
        interface.send('Smooth_on')
    else:
        interface.send('Smooth_off')


def call_switch_1(event):
    if switch_1 == 0:
        interface.send('Switch_1_on')
    else:
        interface.send('Switch_1_off')


def call_switch_2(event):
    if switch_2 == 0:
        interface.send('Switch_2_on')
    else:
        interface.send('Switch_2_off')


def call_switch_3(event):
    if switch_3 == 0:
        interface.send('Switch_3_on')
    else:
        interface.send('Switch_3_off')


def all_btn_red():
    btn_steady.config(bg='#FF6D00', fg='#000000')
    btn_find_color.config(bg='#FF6D00', fg='#000000')
    btn_watchdog.config(bg='#FF6D00', fg='#000000')


def all_btn_normal():
    global func_mode, switch_1, switch_2, switch_3, smooth_mode
    btn_find_color.config(bg=color_btn, fg=color_text)
    btn_watchdog.config(bg=color_btn, fg=color_text)
    func_mode = 0
    btn_steady.config(bg=color_btn, fg=color_text)
    switch_3 = 0
    switch_2 = 0
    switch_1 = 0
    smooth_mode = 0


def button_update(status_data):
    global switch_1, switch_2, switch_3, func_mode, btn_smooth, smooth_mode
    if 'FindColor' in status_data:
        func_mode = 1
        all_btn_red()
        btn_find_color.config(bg=color_btn_act)
    elif 'WatchDog' in status_data:
        func_mode = 1
        all_btn_red()
        btn_watchdog.config(bg=color_btn_act)
    elif 'steady' in status_data:
        func_mode = 1
        all_btn_red()
        btn_steady.config(bg=color_btn_act)
    elif 'Switch_3_on' in status_data:
        btn_Switch_3.config(bg=color_swt_act)
        switch_3 = 1
    elif 'Switch_2_on' in status_data:
        switch_2 = 1
        btn_Switch_2.config(bg=color_swt_act)
    elif 'Switch_1_on' in status_data:
        switch_1 = 1
        btn_Switch_1.config(bg=color_swt_act)
    elif 'Switch_3_off' in status_data:
        switch_3 = 0
        btn_Switch_3.config(bg=color_btn)
    elif 'Switch_2_off' in status_data:
        switch_2 = 0
        btn_Switch_2.config(bg=color_btn)
    elif 'Switch_1_off' in status_data:
        switch_1 = 0
        btn_Switch_1.config(bg=color_btn)
    elif 'Smooth_on' in status_data:
        smooth_mode = 1
        btn_smooth.config(bg=color_swt_act)
    elif 'Smooth_off' in status_data:
        smooth_mode = 0
        btn_smooth.config(bg=color_btn)
    elif 'func_end' in status_data:
        all_btn_normal()


# This method is used to get
# the name of the widget
# which currently has the focus
# by clicking Mouse Button-1
def focus(event):
    if str(root.focus_get()) == '.!entry2':
        unbind_keys()


def stat_update(cpu_temp, cpu_use, ram_use):
    label_cpu_temp.config(text='CPU Temp: %s℃' % cpu_temp)
    label_cpu_use.config(text='CPU Usage: %s' % cpu_use)
    label_ram_use.config(text='RAM Usage: %s' % ram_use)


def set_R():
    return 'wsR %s' % var_R.get()


def set_G():
    return 'wsG %s' % var_G.get()


def set_B():
    return


def send_command(event):
    global interface
    if e2.get() != '' and interface.connect_event.is_set():
        interface.send(e2.get())
        e1.focus_set()
        e2.delete(0, 'end')
    bind_keys()


def call_stream_audio(event):
    interface.send('stream_audio')


def destroy():
    root.destroy()
