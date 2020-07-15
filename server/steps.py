move_list = [
    "move.robot_yaw(0)", "move.robot_balance(balance[0])", "move.leg_up(leg[0])",
    "move.leg_move(leg[0], direction_command)", "move.leg_down(leg[0])", "move.leg_up(leg[1])",
    "move.leg_move(leg[1], direction_command)", "move.leg_down(leg[1])",
    "move.robot_yaw(0)", "move.robot_balance(balance[1])", "move.leg_up(leg[2])",
    "move.leg_move(leg[2], direction_command)", "move.leg_down(leg[2])", "move.leg_up(leg[3])",
    "move.leg_move(leg[3], direction_command)", "move.leg_down(leg[3])"
]

crab_list = [
    "move.robot_height(60)",
    "move.robot_balance(balance)",
    "move.leg_up(leg[1])",
    "move.leg_move(leg[1], 'in')",
    "move.leg_down(leg[1], 240)",
    "move.leg_up(leg[0])",
    "move.leg_move(leg[0], 'out')",
    "move.leg_down(leg[0])",
    "move.robot_balance('back', 'torso')",
    "move.leg_up(leg[3])",
    "move.leg_move(leg[3], 'in')",
    "move.leg_down(leg[3], 240)",
    "move.leg_up(leg[2])",
    "move.leg_move(leg[2], 'out')",
    "move.leg_down(leg[2])"
]

turn_list = [
    "move.robot_balance(balance[0])", "move.leg_up(leg[0])", "move.leg_move(leg[0], 'backward')",
    "move.leg_down(leg[0])", "move.leg_up(leg[1])", "move.leg_move(leg[1], 'backward')",
    "move.leg_down(leg[1])", "move.robot_balance(balance[1])", "move.leg_up(leg[2])",
    "move.leg_move(leg[2], 'forward')", "move.leg_down(leg[2])", "move.leg_up(leg[3])",
    "move.leg_move(leg[3], 'forward')", "move.leg_down(leg[3])"
]
