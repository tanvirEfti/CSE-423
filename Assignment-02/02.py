from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time


w,h = 500, 500 #screen
speed = 2

points = 0
stop = True #for game over
pause_symbol = False
isfrozen = False

#arrow box
arrow = {
        'x': 0,
        'y': 460,
        'width': 40,
        'height': 40
    }

#cross box
cross = {
    'x': 460,
    'y': 460,
    "width": 40,
    "height": 40
}

#play button box
play = {
    "x": 220,
    "y": 460,
    "width": 40,
    "height": 40
}

#pause button box
pause = {
    "x": 240,
    "y": 460,
    "width": 20,
    "height": 40
}

# catcher at first, pos will update with left or right arrow key
catcher_pos = 0
catcher_color = (1, 1, 1) 
catcher_info = [{
    "base": {"x1": 20, "y1": 5, "x2": 100, "y2": 5},
    "left": {"x1": 0, "y1": 20, "x2": 20 , "y2": 5},
    "right": {"x1": 100 , "y1": 5, "x2": 120 , "y2": 20},
    "above": {"x1": 0, "y1": 20, "x2": 120 , "y2": 20}
}, catcher_color]

#  diamond position at first
diamond_x = 75
diamond_color = (1, 0, 0)
diamond_position = [{"edge1": {"x": diamond_x, "y": 450 }, #right
            "edge2": {"x": diamond_x-20, "y":450}, #left
            "edge3": {"x": diamond_x-10, "y": 468}, #top
            "edge4": {"x": diamond_x-10, "y": 432}},  #bottom
            diamond_color] 




def init():
    glLineWidth(1.5)
    glClearColor(0, 0, 0, 1)  # Set background color to black
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, w, 0, h, 0, 1) 
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def draw_pixel(x, y, color=(1, 1, 1)):
    glColor3f(*color)
    glPointSize(2.5)
    glBegin(GL_POINTS)
    glVertex2f(x,y)
    glEnd()

def convert_coordinate(x,y): #for mouse listener conversion 
    global w, h
    a = x 
    b = h-y
    return (a,b)

def find_zone(dx, dy):
    if abs(dx) >= abs(dy):  
        if dx >= 0 and dy >= 0:
            return 0
        elif dx <= 0 and dy >= 0:
            return 3
        elif dx <= 0 and dy <= 0:
            return 4
        else:
            return 7
    else:  
        if dx >= 0 and dy >= 0:
            return 1
        elif dx <= 0 and dy <= 0:
            return 5
        elif dx <= 0 and dy >= 0:
            return 2
        else:
            return 6

def converting_for_zone0(x, y, zone):
    if zone == 0:
        return x, y
    elif zone == 1:
        return y, x
    elif zone == 2:
        return y, -x
    elif zone == 3:
        return -x, y
    elif zone == 4:
        return -x, -y
    elif zone == 5:
        return -y, -x
    elif zone == 6:
        return -y, x
    elif zone == 7:
        return x, -y

def returning_to_main_coords(x, y, zone):
    if zone == 0:
        return x, y
    elif zone == 1:
        return y, x
    elif zone == 2:
        return -y, x
    elif zone == 3:
        return -x, y
    elif zone == 4:
        return -x, -y
    elif zone == 5:
        return -y, -x
    elif zone == 6:
        return y, -x
    elif zone == 7:
        return x, -y

def draw_line(x1, y1, x2, y2, color=(1, 1, 1)):
    dx = x2 - x1
    dy = y2 - y1
    
    zone = find_zone(dx, dy)
    x1, y1 = converting_for_zone0(x1, y1, zone)
    x2, y2 = converting_for_zone0(x2, y2, zone)
    
    dx = x2 - x1
    dy = y2 - y1
    d = 2 * dy - dx
    east = 2 * dy
    north_east = 2 * (dy - dx)
    
    glColor3f(*color)
    glPointSize(1.2)
    glBegin(GL_POINTS)
    
    while x1 <= x2:
        real_x, real_y = returning_to_main_coords(x1, y1, zone)
        glVertex2f(real_x, real_y)
        
        if d > 0:
            d += north_east
            y1 += 1
            x1 += 1
        else:
            d += east
            x1 += 1
    
    glEnd()

def draw_arrow():
    draw_line(0, 475, 20, 495, (0, 0, 1)) #upper part
    draw_line(0, 475, 20, 455, (0, 0, 1)) #lower part
    draw_line(0, 475, 40, 475, (0, 0, 1)) #straightline

def draw_cross():
    draw_line(460, 460, 495, 495, (1, 0, 0)) #left
    draw_line(460, 495, 495, 460, (1, 0, 0)) #right

def draw_play_pause():
    global pause_symbol  
    if pause_symbol and isfrozen:
        draw_line(245, 453, 245, 496, (0, 1, 0)) #left line
        draw_line(245, 496, 272, 475, (0, 1, 0)) #up to down
        draw_line(245, 453, 272, 475, (0, 1, 0)) #down to up
    else:
        draw_line(245, 453, 245, 496, (1, 1, 0)) #left
        draw_line(268, 453, 268, 496, (1, 1, 0)) #right

def catcher():
    global catcher_info, catcher_pos

    catcher_info[0]["base"]["x1"] = 20 + catcher_pos
    catcher_info[0]["base"]["x2"] = 100 + catcher_pos
    catcher_info[0]["left"]["x1"] = catcher_pos
    catcher_info[0]["left"]["x2"] = 20 + catcher_pos
    catcher_info[0]["right"]["x1"] = 100 + catcher_pos
    catcher_info[0]["right"]["x2"] = 120 + catcher_pos
    catcher_info[0]["above"]["x1"] = catcher_pos
    catcher_info[0]["above"]["x2"] = 120 + catcher_pos

    draw_line(catcher_info[0]["base"]["x1"], catcher_info[0]["base"]["y1"], catcher_info[0]["base"]["x2"], catcher_info[0]["base"]["y2"], catcher_info[1]) #base
    draw_line(catcher_info[0]["left"]["x1"], catcher_info[0]["left"]["y1"], catcher_info[0]["left"]["x2"], catcher_info[0]["left"]["y2"], catcher_info[1]) #left diagonal
    draw_line(catcher_info[0]["right"]["x1"], catcher_info[0]["right"]["y1"], catcher_info[0]["right"]["x2"], catcher_info[0]["right"]["y2"], catcher_info[1]) #Right diagonal
    draw_line(catcher_info[0]["above"]["x1"], catcher_info[0]["above"]["y1"], catcher_info[0]["above"]["x2"], catcher_info[0]["above"]["y2"], catcher_info[1]) #above    

def diamond():
    global diamond_position
    draw_line(diamond_position[0]["edge1"]["x"], diamond_position[0]["edge1"]["y"], diamond_position[0]["edge4"]["x"], diamond_position[0]["edge4"]["y"], diamond_position[1])
    draw_line(diamond_position[0]["edge1"]["x"], diamond_position[0]["edge1"]["y"], diamond_position[0]["edge3"]["x"], diamond_position[0]["edge3"]["y"], diamond_position[1])
    draw_line(diamond_position[0]["edge2"]["x"], diamond_position[0]["edge2"]["y"], diamond_position[0]["edge4"]["x"], diamond_position[0]["edge4"]["y"], diamond_position[1])
    draw_line(diamond_position[0]["edge2"]["x"], diamond_position[0]["edge2"]["y"], diamond_position[0]["edge3"]["x"], diamond_position[0]["edge3"]["y"], diamond_position[1])

def specialKeyListener(key, x, y):
    global catcher_info, catcher_pos, stop, isfrozen

    if key==GLUT_KEY_RIGHT:
        if catcher_info[0]["right"]["x2"] and catcher_info[0]["above"]["x2"] < 490 and stop and isfrozen == False: # the right part and the bove part can not cross the width value so 490
            catcher_pos += 20
        else:
            pass
    elif key==GLUT_KEY_LEFT:
        if catcher_pos > 0 and stop and isfrozen == False:
            catcher_pos -= 20
        else:
            pass
    glutPostRedisplay()

def has_collided(diamond, catcher): 
    return (diamond['x'] < catcher['x'] + catcher['width'] and
            diamond['x'] + diamond['width'] > catcher['x'] and
            diamond['y'] < catcher['y'] + catcher['height'] and
            diamond['y'] + diamond['height'] > catcher['y'])

def mouseListener(button, state, x, y):
    global arrow, cross, play, pause, pause_symbol, diamond_position, catcher_info, diamond_x, diamond_color, stop, speed, points, catcher_pos, isfrozen
    
    if button==GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            adj_x, adj_y = convert_coordinate(x, y)	
            
            #restarting game
            if adj_x >= arrow["x"] and adj_x <= arrow["x"] + arrow["width"] and adj_y >= arrow["y"] and adj_y <= arrow["y"] + arrow["height"]:
                print("Starting Over")

                
                diamond_x = random.randint(20, 457)

                diamond_x = 75
                diamond_color = (1, 0, 0)
                diamond_position = [{"edge1": {"x": diamond_x, "y": 450 }, #right_edge
                        "edge2": {"x": diamond_x-20, "y":450}, #left_edge
                        "edge3": {"x": diamond_x-10, "y": 468}, #top_edge
                        "edge4": {"x": diamond_x-10, "y": 432}},  #bottom_edge
                        diamond_color] 

                catcher_pos = 0
                catcher_color = (1, 1, 1) 
                catcher_info = [{
                    "base": {"x1": 20, "y1": 5, "x2": 100, "y2": 5},
                    "left": {"x1": 0, "y1": 20, "x2": 20 , "y2": 5},
                    "right": {"x1": 100 , "y1": 5, "x2": 120 , "y2": 20},
                    "above": {"x1": 0, "y1": 20, "x2": 120 , "y2": 20}
                    }, catcher_color]
                points = 0
                speed = 4
                stop = True
                isfrozen = False #restarts the catcher again if pressed arrow

            # cross 
            elif adj_x >= cross["x"] and adj_x <= cross["x"] + cross["width"] and adj_y >= cross["y"] and adj_y <= cross["y"] + cross["height"]:
                print("GoodBye")
                glutLeaveMainLoop() 

            # play-pause 
            if pause_symbol: #checking True or not
                if adj_x >= play["x"] and adj_x <= play["x"] + play["width"] and adj_y >= play["y"] and adj_y <= play["y"] + play["height"]:
                    print("Game Started Again")
                    pause_symbol = False
                    isfrozen = False  
            elif adj_x >= pause["x"] and adj_x <= pause["x"] + pause["width"] and adj_y >= pause["y"] and adj_y <= pause["y"] + pause["height"]:
                print("Paused the game")
                pause_symbol = True
                isfrozen = True

def animate():
    global diamond_position, diamond_color, diamond_x, stop, speed, points, isfrozen, arrow, cross, play
    if stop and isfrozen != True:    
            catcher_box = {
            'x': catcher_info[0]["base"]["x1"],
            'y': catcher_info[0]["base"]["y1"],
            'width': catcher_info[0]["above"]["x2"] - catcher_info[0]["above"]["x1"],
            'height': catcher_info[0]["above"]["y2"] - catcher_info[0]["base"]["y1"]
            }
            #creating the current catcher and diamond postion dictionary to check if they are colliding or not

            diamond_box = {
            'x': diamond_position[0]["edge1"]["x"],
            'y': diamond_position[0]["edge4"]["y"],
            'width': abs(diamond_position[0]["edge1"]["x"] - diamond_position[0]["edge2"]["x"]),
            'height': abs(diamond_position[0]["edge3"]["y"] - diamond_position[0]["edge4"]["y"])
            }

            # if collides then new diamond will appear from the top with random position
            if has_collided(diamond_box, catcher_box):
                diamond_x = random.randint(20, 500) 
                if diamond_x <= arrow['x'] + arrow["width"]:
                    diamond_x = 65
                elif diamond_x >= cross['x']:
                    diamond_x = cross['x'] - 25    
                elif diamond_x >= pause['x'] and diamond_x <= pause['x'] + pause['width']:
                    if pause['x'] <= diamond_x <= (pause['x'] + pause['x'] +pause["width"])//2:
                        diamond_x = pause['x'] - pause['width'] - 30  
                    else:
                        diamond_x = pause['x'] + pause['width'] + 30 
                diamond_color = (random.uniform(0.23, 1), random.uniform(0.23, 1), random.uniform(0.23, 1))
                diamond_position = [{"edge1": {"x": diamond_x, "y": 450 }, #right
                                    "edge2": {"x": diamond_x-20, "y":450}, #left
                                    "edge3": {"x": diamond_x-10, "y": 468}, #top
                                    "edge4": {"x": diamond_x-10, "y": 432}},  #bottom
                                    diamond_color]

                diamond_box = {
                    'x': diamond_position[0]["edge1"]["x"],
                    'y': diamond_position[0]["edge4"]["y"],
                    'width': abs(diamond_position[0]["edge1"]["x"] - diamond_position[0]["edge2"]["x"]),
                    'height': abs(diamond_position[0]["edge3"]["y"] - diamond_position[0]["edge4"]["y"])
                    }
                speed+=0.36
                points += 1
                print(points)
                
            else:
                for i in diamond_position[0]:    # changing each edges y to move down
                    diamond_position[0][i]["y"] -= speed
                    if diamond_position[0][i]["y"] < catcher_info[0]["base"]["y1"]:
                        if diamond_position[0][i]["y"] < 0:
                            print("Game Over")
                            print("Your Score: ", points)
                            stop = False
                            catcher_info[1] = (1,0,0)  
                            diamond_position[1] = (0, 0, 0)
    

    glutPostRedisplay()
    time.sleep(0.01) # to slow the processiong and giving computer rest between the frames
   

def iterate():
    glViewport(0, 0, 500, 500)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, 500, 0.0, 500, 0.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    iterate()  
    draw_arrow()
    draw_cross()
    draw_play_pause()
    catcher()
    diamond()
    glutSwapBuffers()


glutInit()
glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
glutInitWindowSize(500, 500)
glutInitWindowPosition(550, 150)
window = glutCreateWindow(b"GAME")
init()  
glutDisplayFunc(display)
glutSpecialFunc(specialKeyListener)
glutMouseFunc(mouseListener)  
glutIdleFunc(animate)  
glutMainLoop()