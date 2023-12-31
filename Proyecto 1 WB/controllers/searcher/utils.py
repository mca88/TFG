from dataclasses import dataclass
from random import randint

color_red    = [1,0,0]
color_blue   = [0,0,1]
color_yellow = [1,1,0]
color_cian   = [0,1,1]
color_green  = [0,1,0]

def rand_color():
    num = randint(0,100)
    if(num <= 50):
        return color_red
    else:
         return color_blue

def zone_colors(box_color):
    if(box_color == color_red): ## Para las cajas rojas
        return color_yellow
    elif(box_color == color_blue):
        return color_cian
    
def extract_list_colors(color_object):
        red = int(color_object[0])
        green = int(color_object[1])
        blue = int(color_object[2])
        return [red,green,blue]
    
@dataclass
class TargetInfo:
    id : int
    size : int
    pos_x : int
    pos_y : int