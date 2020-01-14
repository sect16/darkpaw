# E-mail      : sect16@gmail.com
# Author      : Chin Pin Hon
# Date        : 14.01.2020

"""
This file contains robot specific key binding config.

It is meant to be executed in line and not imported.
"""

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

root.bind('<KeyPress-h>', lambda _: functions.send('headhome'))
root.bind('<KeyPress-i>', lambda _: functions.send('headup'))
root.bind('<KeyPress-k>', lambda _: functions.send('headdown'))
root.bind('<KeyPress-x>', call_find_color)
root.bind('<KeyPress-c>', call_watchdog)

root.bind('<KeyPress-b>', lambda _: functions.send('stream_audio'))
root.bind('<KeyPress-j>', lambda _: functions.send('headleft'))
root.bind('<KeyPress-l>', lambda _: functions.send('headright'))
root.bind('<KeyPress-u>', lambda _: functions.send('low'))
root.bind('<KeyPress-o>', lambda _: functions.send('high'))

root.bind('<KeyPress-z>', call_steady)
root.bind('<KeyPress-v>', call_smooth)
