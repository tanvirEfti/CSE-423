##Task-01
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random


bg_r, bg_g, bg_b = 0.0, 0.0, 0.0
drops = 100 
raindrops = []
drop={}
for i in range(drops):
    drop = {
        "x": random.uniform(-1000, 1000),  "y": random.uniform(-650, 650)    
    }
    raindrops.append(drop)
rain_speed = 5  
wind_shift = 0   



def iterate():
    glViewport(0, 0, 1000, 650)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, 1000, 0.0, 650, 0.0, 1.0)
    glMatrixMode (GL_MODELVIEW)
    glLoadIdentity()
    glClearColor(bg_r, bg_g, bg_b, 1.0)
    
    

def KeyboardListener(key, x, y):
    global bg_r, bg_g, bg_b
    if key == b'n':  
        if bg_r >= 0.0:
            bg_r -= 0.05  
            bg_g -= 0.05
            bg_b -= 0.05
            print("Night")
        else:
            print("Already Night !")
            
    if key == b'm':  
        if bg_r < 1.0:
            bg_r += 0.05  
            bg_g += 0.05
            bg_b += 0.05
            print("Morning")
        else:
            print("Already Morning !")
    glutPostRedisplay() 
  
def specialKeyListener(key, x, y):
    global wind_shift, rain_speed

    if key == GLUT_KEY_LEFT:
        if wind_shift > 0:  
            wind_shift = 0
            rain_speed = 5
        else:
            wind_shift -= 1  
            rain_speed = min(rain_speed + 0.5, 5)  #max speed 5

    elif key == GLUT_KEY_RIGHT:
        if wind_shift < 0:  
            wind_shift = 0
            rain_speed = 5
        else:
            wind_shift += 1  
            rain_speed = min(rain_speed + 0.5, 5) #max speed 5

    glutPostRedisplay()




def drawRain():
    global raindrops, wind_shift, rain_speed

    glColor3f(0.2, 0.2, 0.8)  
    glLineWidth(2.6)
    glBegin(GL_LINES)

    for i in raindrops:
        i["y"] -= rain_speed  
        i["x"] += wind_shift  

       
        if i["y"] < 0:
            i["y"] = random.uniform(650,-650)  
            i["x"] = random.uniform(-1000, 1000)  

        glVertex2f(i["x"], i["y"])
        glVertex2f(i["x"] + wind_shift, i["y"] - 40)  

    glEnd()
    glutPostRedisplay()




def drawing():
    #ground
    glColor3f(0.6, 0.3, 0.0)
    glBegin(GL_TRIANGLES)
    
    glVertex2f(0,0)
    glVertex2f(1000,0)
    glVertex2f(0,500)
    
    glVertex2f(0,500)
    glVertex2f(1000,500)
    glVertex2f(1000,0)
    
    glEnd()
    
    #bush-line
    glColor3f(0, 1, 0)
    glLineWidth(3)
    glBegin(GL_LINES)
    
    glVertex2f(0,350)
    glVertex2f(1000,350)
    glEnd()
    
    #bush-Trinagle
    glBegin(GL_TRIANGLES)
    glColor3f(0.0, 1.0, 0.0)
    glVertex2f(0, 350)
    glColor3f(0.6, 0.3, 0.0)  
    glVertex2f(25, 465) 
    glColor3f(0.0, 1.0, 0.0) 
    glVertex2f(50, 350)  

    glColor3f(0.0, 1.0, 0.0)
    glVertex2f(50, 350)
    glColor3f(0.6, 0.3, 0.0)    
    glVertex2f(75, 465)
    glColor3f(0.0, 1.0, 0.0)  
    glVertex2f(100, 350)  
    
    glColor3f(0.0, 1.0, 0.0)
    glVertex2f(100, 350)
    glColor3f(0.6, 0.3, 0.0)    
    glVertex2f(125, 465)  
    glColor3f(0.0, 1.0, 0.0)
    glVertex2f(150, 350)  

    glColor3f(0.0, 1.0, 0.0)
    glVertex2f(150, 350)
    glColor3f(0.6, 0.3, 0.0)    
    glVertex2f(175, 465)
    glColor3f(0.0, 1.0, 0.0)  
    glVertex2f(200, 350)  

    glColor3f(0.0, 1.0, 0.0)
    glVertex2f(200, 350)
    glColor3f(0.6, 0.3, 0.0)    
    glVertex2f(225, 465) 
    glColor3f(0.0, 1.0, 0.0) 
    glVertex2f(250, 350)  

    glColor3f(0.0, 1.0, 0.0)
    glVertex2f(250, 350)
    glColor3f(0.6, 0.3, 0.0)      
    glVertex2f(275, 465)  
    glColor3f(0.0, 1.0, 0.0)
    glVertex2f(300, 350)  

    glColor3f(0.0, 1.0, 0.0)
    glVertex2f(300, 350)
    glColor3f(0.6, 0.3, 0.0)      
    glVertex2f(325, 465)  
    glColor3f(0.0, 1.0, 0.0)
    glVertex2f(350, 350)  

    glColor3f(0.0, 1.0, 0.0)
    glVertex2f(350, 350)
    glColor3f(0.6, 0.3, 0.0)      
    glVertex2f(375, 465)  
    glColor3f(0.0, 1.0, 0.0)
    glVertex2f(400, 350)  
    
    glColor3f(0.0, 1.0, 0.0)
    glVertex2f(400, 350)
    glColor3f(0.6, 0.3, 0.0)      
    glVertex2f(425, 465) 
    glColor3f(0.0, 1.0, 0.0) 
    glVertex2f(450, 350)  

    glColor3f(0.0, 1.0, 0.0)
    glVertex2f(450, 350)
    glColor3f(0.6, 0.3, 0.0)      
    glVertex2f(475, 465)  
    glColor3f(0.0, 1.0, 0.0)
    glVertex2f(500, 350)  

    glColor3f(0.0, 1.0, 0.0)
    glVertex2f(500, 350)
    glColor3f(0.6, 0.3, 0.0)      
    glVertex2f(525, 465)  
    glColor3f(0.0, 1.0, 0.0)
    glVertex2f(550, 350)  

    glColor3f(0.0, 1.0, 0.0)
    glVertex2f(550, 350)
    glColor3f(0.6, 0.3, 0.0)      
    glVertex2f(575, 465)  
    glColor3f(0.0, 1.0, 0.0)
    glVertex2f(600, 350)  

    glColor3f(0.0, 1.0, 0.0)
    glVertex2f(600, 350)
    glColor3f(0.6, 0.3, 0.0)      
    glVertex2f(625, 465)  
    glColor3f(0.0, 1.0, 0.0)
    glVertex2f(650, 350)  

    glColor3f(0.0, 1.0, 0.0)
    glVertex2f(650, 350)
    glColor3f(0.6, 0.3, 0.0)      
    glVertex2f(675, 465)  
    glColor3f(0.0, 1.0, 0.0)
    glVertex2f(700, 350)  

    glColor3f(0.0, 1.0, 0.0)
    glVertex2f(700, 350)
    glColor3f(0.6, 0.3, 0.0)      
    glVertex2f(725, 465)  
    glColor3f(0.0, 1.0, 0.0)
    glVertex2f(750, 350)  

    glColor3f(0.0, 1.0, 0.0)
    glVertex2f(750, 350)
    glColor3f(0.6, 0.3, 0.0)      
    glVertex2f(775, 465)  
    glColor3f(0.0, 1.0, 0.0)
    glVertex2f(800, 350)  
    
    glColor3f(0.0, 1.0, 0.0)
    glVertex2f(800, 350)
    glColor3f(0.6, 0.3, 0.0)      
    glVertex2f(825, 465)  
    glColor3f(0.0, 1.0, 0.0)
    glVertex2f(850, 350)  

    glColor3f(0.0, 1.0, 0.0)
    glVertex2f(850, 350)
    glColor3f(0.6, 0.3, 0.0)      
    glVertex2f(875, 465)  
    glColor3f(0.0, 1.0, 0.0)
    glVertex2f(900, 350)  

    glColor3f(0.0, 1.0, 0.0)
    glVertex2f(900, 350)
    glColor3f(0.6, 0.3, 0.0)      
    glVertex2f(925, 465)  
    glColor3f(0.0, 1.0, 0.0)
    glVertex2f(950, 350)  

    glColor3f(0.0, 1.0, 0.0)
    glVertex2f(950, 350)
    glColor3f(0.6, 0.3, 0.0)      
    glVertex2f(975, 465)  
    glColor3f(0.0, 1.0, 0.0)
    glVertex2f(1000, 350)  

    glColor3f(0.0, 1.0, 0.0)
    glVertex2f(1000, 350)
    glColor3f(0.6, 0.3, 0.0)      
    glVertex2f(1025, 465) 
    glColor3f(0.0, 1.0, 0.0) 
    glVertex2f(1050, 350)  

    glEnd()
   
    
    #House
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_TRIANGLES)
    glVertex2f(225, 250)  
    glVertex2f(225, 450)  
    glVertex2f(775, 250)  
    
    
    glVertex2f(225, 450)
    glVertex2f(775, 450)
    glVertex2f(775, 250)
    glEnd()
    
    #roof
    glColor3f(0.5, 0.0, 0.5)
    glBegin(GL_TRIANGLES)
    glVertex2f(190, 450)
    glVertex2f(500, 550)
    glVertex2f(810, 450)
    
    glEnd()
    
    #door
    glColor3f(0.0, 0.75, 1.0)
    
    glBegin(GL_TRIANGLES)
    glVertex2f(460, 250)
    glVertex2f(460, 375)
    glVertex2f(540, 250)
    
    glVertex2f(460, 375)
    glVertex2f(540, 375)
    glVertex2f(540, 250)
    
    glEnd()
    
    #door-handle
    glPointSize(7.5)
    glColor3f(0.0, 0.0, 0.0)
    glBegin(GL_POINTS)
    glVertex2f(523, 315)
    glEnd()

    #window 
    #Left
    glColor3f(0.0, 0.75, 1.0)
    glBegin(GL_TRIANGLES)
    
    glVertex2f(345, 325)
    glVertex2f(345, 375)
    glVertex2f(430, 325)
    
    glVertex2f(345, 375)
    glVertex2f(430, 375)
    glVertex2f(430, 325)
    
    glEnd()
    
    glColor3f(0.0, 0.0, 0.0)
    glBegin(GL_LINES)
    glVertex2f(387.5, 325)
    glVertex2f(387.5, 375)
    
    glVertex2f(345,350)
    glVertex2f(430,350)
    glEnd()
    
    
    #right
    glColor3f(0.0, 0.75, 1.0)
    glBegin(GL_TRIANGLES)
    glVertex2f(575, 325)
    glVertex2f(575, 375)
    glVertex2f(660, 325)
    
    glVertex2f(575, 375)
    glVertex2f(660, 375)
    glVertex2f(660, 325)
    glEnd()
    
    glColor3f(0.0, 0.0, 0.0)
    glBegin(GL_LINES)
    glVertex2f(617.5, 325)
    glVertex2f(617.5, 375)
    
    glVertex2f(575,350)
    glVertex2f(660,350)
    glEnd()
    
def animate() :
    drawRain()
    glutPostRedisplay()
    
      
def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    iterate() 
    drawing()
    drawRain()
    glutSwapBuffers()



glutInit()
glutInitDisplayMode(GLUT_RGBA)
glutInitWindowSize(1000,650) 
glutInitWindowPosition(0, 0)
wind = glutCreateWindow(b"House in Rain") 
glutDisplayFunc(showScreen)
glutKeyboardFunc(KeyboardListener)
glutSpecialFunc(specialKeyListener)
glutIdleFunc(animate)
glutMainLoop()

###########################################################################################################################################

# #task2

# from OpenGL.GL import *
# from OpenGL.GLUT import *
# from OpenGL.GLU import *
# import random



# points = [] 


# speed = 0.1
# blinking_mode = False  
# blink = True  
# frozen = False  


# def draw_point(x, y):
#     glPointSize(5)  
#     glBegin(GL_POINTS)
#     glVertex2f(x, y)
#     glEnd()


# def iterate():
#     glViewport(0, 0, 500, 500)
#     glMatrixMode(GL_PROJECTION)
#     glLoadIdentity()
#     glOrtho(0, 500, 0, 500, 0.0, 1.0)
#     glMatrixMode(GL_MODELVIEW)
#     glLoadIdentity()


# def display():
#     glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
#     glLoadIdentity()
#     iterate()

#     for i in points:
#         x, y = i[0]
#         a,b,c = i[2]


#         if blinking_mode and blink:
#             glColor3f(0, 0, 0)  
#         else:
#             glColor3f(a, b, c) 
#             draw_point(x, y)
#     glutSwapBuffers()


# def update():
#     if frozen:
#         return

#     global blink, blinking_mode

#     for i in range(len(points)):
#         (x, y), (dx, dy), color = points[i]

       
#         x += dx * speed
#         y += dy * speed

  
#         if x <= 0 or x >= 500:
#             dx *= -1
#         if y <= 0 or y >= 500:
#             dy *= -1

    
#         points[i] = ((x, y), (dx, dy), color)

#     glutPostRedisplay()  


# def mouse_click(button, state, x, y):
#     if frozen:
#         return

#     if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
#         new_x, new_y = convert_coordinates(x, y)
#         new_dx = random.choice([-1, 1])
#         new_dy = random.choice([-1, 1])
#         new_color = (random.random(), random.random(), random.random())
#         points.append(((new_x, new_y), (new_dx, new_dy), new_color))


# def handle_special_keys(key, x, y):
#     if frozen:
#         return

#     global speed, blinking_mode, blink

#     if key == GLUT_KEY_UP:
#         speed *= 1.5
#     elif key == GLUT_KEY_DOWN:
#         speed /= 1.5
#     elif key == GLUT_KEY_LEFT:
#         blinking_mode = not blinking_mode
#         if blinking_mode:
#             blink = True
#             glutTimerFunc(1000, toggle_blink, 0)


# def handle_keyboard(key,x,y):
#     global frozen
#     if key == b' ':
#         frozen = not frozen


# def toggle_blink(value):
#     global blink
#     if not frozen:
#         blink = not blink
#     if blinking_mode:
#         glutTimerFunc(1000, toggle_blink, 0) # 1st parameter time


# def convert_coordinates(x, y):
#     return x, 500 - y




# glutInit()
# glutInitDisplayMode(GLUT_RGBA)
# glutInitWindowSize(500, 500)
# glutInitWindowPosition(0, 0)
# glutCreateWindow(b"Magical Boxy")
# glutDisplayFunc(display)
# glutIdleFunc(update)
# glutMouseFunc(mouse_click)
# glutSpecialFunc(handle_special_keys)
# glutKeyboardFunc(handle_keyboard)

# glutMainLoop()