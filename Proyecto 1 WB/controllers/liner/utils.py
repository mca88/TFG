from dataclasses import dataclass

def value_to_color(value):
    if(620 <= value <= 637): return "black"
    if(615 <= value <= 617): return "blue"
    if(198 <= value <= 200): return "green"
    if(179 <= value <= 183): return "gray"
    if(130 <= value <= 132): return "red"
    if(120 <= value <= 128): return "yellow"

    return ("???")

@dataclass
class States:
    yellow_line   = 1
    choose_target = 2
    move_zone     = 3
    pick_up_box   = 4
    turn_store    = 5
    move_store    = 6
    store_box     = 7