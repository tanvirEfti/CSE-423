from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math


camera_pos = (300,-5,250)

fovY = 120  # Field of view
GRID_LENGTH = 600  


human_x = 300  
human_y = 300
human_z = 30 
human_size=[40, 40, 40] #for collusion detection
human_rotation = 0

player_life = 5
cheat_health = 5  # Initialize to current player life
game_over = False
cheat_mode = False
camera_following_player = False

enemy_positions = []  
enemy_size_factor = 1.0  
enemy_size_increasing = True

bullets = []  
bullet_speed = 5
bullets_missed = 0
game_score = 0


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1,1,1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    # Set up an orthographic projection that matches window coordinates
    gluOrtho2D(0, 1000, 0, 800)  # left, right, bottom, top

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Draw text at (x, y) in screen coordinates
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    # Restore original projection and modelview matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_human():
    glPushMatrix()
    glTranslatef(human_x, human_y, human_z)
    if game_over:
        glRotatef(180, 1, 0, 0) #upside down player
    else:
        glRotatef(human_rotation, 0, 0, 1) 
    
    #body
    glTranslatef(0, 0, 10)
    glScalef(1.8, 1, 1.4)
    glColor3f(0.2, 0.5, 0.2)  
    glutSolidCube(40)
        
    #head
    glPushMatrix()
    glTranslatef(0, 0, 30)
    glColor3f(0, 0, 0)
    gluSphere(gluNewQuadric(), 12, 15, 15)
    glPopMatrix()

    #hands
    glPushMatrix()
    glTranslatef(10, 14, 5)
    glRotatef(90, 0, 1, 0)
    glColor3f(.93, 0.68, 0.53)  
    gluCylinder(gluNewQuadric(), 10, 2, 30, 10, 10) #base,top,height, around z, along z
    glPopMatrix()

    glPushMatrix()
    glTranslatef(10, -14, 5)
    glRotatef(90, 0, 1, 0)
    glColor3f(.93, 0.68, 0.53)  
    gluCylinder(gluNewQuadric(), 10, 2, 30, 10, 10)
    glPopMatrix()
        
    #Left leg
    glPushMatrix()
    glTranslatef(0, 15, -35)
    glColor3f(0, 0, 1)  
    gluCylinder(gluNewQuadric(), 10, 3, 30, 10, 10)
    glPopMatrix()
        
    #Right leg
    glPushMatrix()
    glTranslatef(0, -17, -35)
    glColor3f(0, 0, 1)  
    gluCylinder(gluNewQuadric(), 10, 3, 30, 10, 10)
    glPopMatrix()

    #gun 
    glPushMatrix()
    glTranslatef(10, 0, 5)
    glRotatef(90, 0, 1, 0)
    glColor3f(0.3, 0.3, 0.3) 
    gluCylinder(gluNewQuadric(), 10, 2, 60, 10, 10)
    glPopMatrix()
        
    glPopMatrix()





def check_collision(obj1_pos, obj1_size, obj2_pos, obj2_size):
    
    #half calculation bcz calculatuion is done from the center point
    h_w_1 = obj1_size[0] / 2
    h_h_1 = obj1_size[1] / 2
    h_depth_1 = obj1_size[2] / 2
    h_size_1 = [h_w_1, h_h_1, h_depth_1]

    h_w_2 = obj2_size[0] / 2
    h_h_2 = obj2_size[1] / 2
    h_depth_2 = obj2_size[2] / 2
    h_size_2 = [h_w_2, h_h_2, h_depth_2]
        
    
    min1_x = obj1_pos[0] -h_size_1[0]  
    min1_y = obj1_pos[1] -h_size_1[1]  
    min1_z = obj1_pos[2] -h_size_1[2]  
    min1 = [min1_x, min1_y, min1_z]       

    max1_x = obj1_pos[0] +h_size_1[0]  
    max1_y = obj1_pos[1] +h_size_1[1]  
    max1_z = obj1_pos[2] +h_size_1[2]  
    max1 = [max1_x, max1_y, max1_z]       

    
    min2_x = obj2_pos[0] -h_size_2[0]  
    min2_y = obj2_pos[1] -h_size_2[1]  
    min2_z = obj2_pos[2] -h_size_2[2] 
    min2 = [min2_x, min2_y, min2_z]       

    max2_x = obj2_pos[0] +h_size_2[0]  
    max2_y = obj2_pos[1] +h_size_2[1]  
    max2_z = obj2_pos[2] +h_size_2[2]  
    max2 = [max2_x, max2_y, max2_z]      
    
   
    x_over = min1[0] < max2[0] and max1[0] > min2[0]
    y_over = min1[1] < max2[1] and max1[1] > min2[1]
    z_over = min1[2] < max2[2] and max1[2] > min2[2]
    
    return x_over and y_over and z_over


######bullets########

def draw_bullets():
    for bullet in bullets:
        glPushMatrix()
        glTranslatef(bullet['pos'][0], bullet['pos'][1], bullet['pos'][2])
        glColor3f(1.0, 0.0, 0.0)  
        glutSolidSphere(3, 8, 8)  
        glPopMatrix()



def fire_bullet():
    if game_over:
        return
        
   
    gun_rad = human_rotation * (3.14159 / 180)  
    gun_length = 60  
    
    bullet_x = human_x + gun_length * math.cos(gun_rad)
    bullet_y = human_y + gun_length * math.sin(gun_rad)
    bullet_z = human_z + 5 
    
   
    bullets.append({
        'pos': [bullet_x, bullet_y, bullet_z],
        'dir': [math.cos(gun_rad), math.sin(gun_rad), 0],
        'lifetime': 100,  # Add a lifetime value
        'from_cheat_mode': cheat_mode 
    })



def update_bullets():
    global bullets, bullets_missed, game_score, enemy_positions, game_over
   
    if game_over:
        return
        
    bullets_to_remove = []
    for i, a in enumerate(bullets):
        # Move bullet
        a['pos'][0] += a['dir'][0] * bullet_speed
        a['pos'][1] += a['dir'][1] * bullet_speed
        a['lifetime'] -= 0.1 #kotokhn bullet dekha jabe. handles collusion with walls as well
        
        # collision detection
        bullet_pos = a['pos']
        bullet_size = [6, 6, 6] 
        
        enemy_hit = None
        for j, k in enumerate(enemy_positions):
            
            enemy_body_radius = 20 * enemy_size_factor
            enemy_size = [enemy_body_radius * 2, enemy_body_radius * 2, enemy_body_radius * 2]
            
            if check_collision(bullet_pos, bullet_size, k, enemy_size):
                enemy_hit = j
                game_score += 1
                bullets_to_remove.append(i)
                break
            
        # spawning a new one
        if enemy_hit is not None:
            enemy_positions.pop(enemy_hit)
            spawn_new_enemy()
        
        elif (a['lifetime'] <= 0 or 
            a['pos'][0] < 0 or a['pos'][0] > GRID_LENGTH or 
            a['pos'][1] < 0 or a['pos'][1] > GRID_LENGTH):
            bullets_to_remove.append(i)
            

            if not cheat_mode and not a.get('from_cheat_mode', False): #not increasing bullet missed in cheat mode
                bullets_missed += 1
                print("Bullet missed!", bullets_missed)

                if bullets_missed >= 10:
                    game_over = True
    
    
    for i in sorted(bullets_to_remove, reverse=True):
        if i < len(bullets):  
            del bullets[i]

########enemy#######

def draw_enemies():
    global enemy_positions
    
    if game_over:
        return
    else:
        for i in enemy_positions:
            glPushMatrix()
            glTranslatef(i[0], i[1], i[2])
            

            glColor3f(1.0, 0.0, 0.0)  
            body_radius = 20 * enemy_size_factor 
            gluSphere(gluNewQuadric(), body_radius, 16, 16)
            
        
            glTranslatef(0, 0, body_radius + 5)  
            glColor3f(0.0, 0.0, 0.0)  
            head_radius = 13 * enemy_size_factor  # pulsing effect
            gluSphere(gluNewQuadric(), head_radius, 16, 16)
            
            glPopMatrix()


def initialize_enemies():
    global enemy_positions
    enemy_positions = []  
    
    for i in range(5):
        x = random.randint(50, 580)  # 50 so that they wont collide with the walls
        y = random.randint(50, 580)
        z = 14  
        enemy_positions.append([x, y, z])


def spawn_new_enemy():
    global enemy_positions
    
    if len(enemy_positions) >= 5:
        return

    x = random.randint(50, 550)  # Keep away from edges
    y = random.randint(50, 550)
    z = 14  # Height above ground
    
    enemy_positions.append([x, y, z])


def update_enemy_size():
    global enemy_size_factor, enemy_size_increasing
    
    if game_over:
        return
        
    #  pulsing effect
    if enemy_size_increasing:
        enemy_size_factor += 0.01
        if enemy_size_factor >= 1.2:
            enemy_size_increasing = False
    else:
        enemy_size_factor -= 0.01
        if enemy_size_factor <= 0.8:
            enemy_size_increasing = True

def update_enemies():
    global player_life, game_over, bullets_missed
    
    if game_over:
        return
        

    for i, enemy in enumerate(enemy_positions):
        dx = human_x - enemy[0]
        dy = human_y - enemy[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 30:  
            enemy[0] += dx * 0.001  # Slow movement
            enemy[1] += dy * 0.001
        
       
        enemy[0] = max(30, min(enemy[0], 575))
        enemy[1] = max(30, min(enemy[1], 575))
        
       
        player_pos = [human_x, human_y, human_z + 10]  # body center
        player_size = [40 * 1.2, 40 * 0.7, 40 * 1.4]  
        
        enemy_body_radius = 20 * enemy_size_factor
        enemy_pos = [enemy[0], enemy[1], enemy[2]]
        enemy_size = [enemy_body_radius * 2, enemy_body_radius * 2, enemy_body_radius * 2]
        
        
        if check_collision(player_pos, player_size, enemy_pos, enemy_size):
            if not cheat_mode:  # Only reduce life if not in cheat mode
                player_life -= 1
                print("Player life:", player_life)
                if player_life <= 0:
                    game_over = True
            
            # Move the enemy to a new position regardless
            enemy_positions[i][0] = random.randint(30, 575)
            enemy_positions[i][1] = random.randint(30, 575)


def cheat_mode_function():
    global human_x, human_y, human_z, human_rotation, game_score, enemy_positions
    
    if cheat_mode and not game_over:
        
        human_rotation = (human_rotation + 5) % 360
        
        closest_enemy = None
        closest_angle_diff = 10  # Minimum angle for fire
        
        for i, enemy in enumerate(enemy_positions):
            dx = enemy[0] - human_x
            dy = enemy[1] - human_y
            
            if dx == 0 and dy == 0:
                continue
                
            enemy_angle = math.degrees(math.atan2(dy, dx)) % 360
            angle_diff = min((human_rotation - enemy_angle) % 360, (enemy_angle - human_rotation) % 360)
            
            if angle_diff < closest_angle_diff:
                closest_angle_diff = angle_diff
                closest_enemy = i
                
        if closest_enemy is not None and closest_angle_diff < 5:
            fire_bullet()
            


#########keyboard,mouse and speacial key listener##########


def keyboardListener(key, x, y):
    global human_x, human_y, human_rotation, cheat_mode
    global player_life, game_over, game_score, bullets_missed, cheat_health
    

    if game_over and key != b'r':
        return
    
   
    if key == b'w': 
        human_x += 10 * math.cos(math.radians(human_rotation))
        human_y += 10 * math.sin(math.radians(human_rotation))

   
    if key == b's':
        human_x -= 10*math.cos(math.radians(human_rotation))
        human_y -= 10*math.sin(math.radians(human_rotation))

 
    if key == b'a':
       human_rotation+=10  #baam e roation koray
    
 
    if key == b'd':
        human_rotation-=10 #daan e roation koray

    if key == b'c' and not game_over:
        if not cheat_mode:  # Store health only when entering cheat mode
            cheat_health = player_life
        cheat_mode = True
        print("Cheat mode activated. Health saved:", cheat_health)
    
    if key == b'v' and not game_over and cheat_mode:
        cheat_mode = False
        player_life = cheat_health  # Use assignment operator (=) not equality (==)
        print("Cheat mode deactivated. Health restored:", player_life)

    # Resting everything
    if key == b'r':
        # Reset player
        human_x = 300
        human_y = 300
        human_z = 30 
        human_rotation = 0
        player_life = 5
        cheat_health = 5  # Reset cheat_health too
        game_over = False
        cheat_mode = False  # Turn off cheat mode on restart
        game_score = 0
        bullets_missed = 0
        
        # Reset enemies
        initialize_enemies()
        
        # Clear bullets
        bullets.clear()

    human_x = max(10, min(human_x, 590))  # Keep within grid bounds
    human_y = max(10, min(human_y, 590))

def specialKeyListener(key, x, y):
    
    if game_over:
        return
        
    global camera_pos
    x, y, z = camera_pos
   
    if key == GLUT_KEY_UP:
        z+=6.5
    # Move camera down (DOWN arrow key)
    if key == GLUT_KEY_DOWN:
        z-=6.5
   
    if key == GLUT_KEY_LEFT:
        x-= 5 
        y-=2 

    # moving camera right (RIGHT arrow key)
    if key == GLUT_KEY_RIGHT:
        x+= 5
        y+=2 

    camera_pos = (x, y, z)

def mouseListener(button, state, x, y):
   
    if game_over and button == GLUT_LEFT_BUTTON:
        return
        
    global camera_following_player
    

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        fire_bullet()
        print("Player bullet fired")

    # Right mouse button toggles camera tracking mode
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        camera_following_player = not camera_following_player

#######camera############

def setupCamera():
   
    glMatrixMode(GL_PROJECTION)  
    glLoadIdentity()
   
    gluPerspective(fovY, 1.25, 0.1, 1500) 
    glMatrixMode(GL_MODELVIEW)  
    glLoadIdentity()


    if camera_following_player:
        angle_rad = human_rotation * (math.pi / 180)
        cam_x = human_x 
        cam_y = human_y 
        cam_z = human_z + 100 
    
        new_x = human_x +100 * math.cos(angle_rad)
        new_y = human_y + 100 * math.sin(angle_rad)
        new_z = human_z + 40

        gluLookAt(cam_x, cam_y, cam_z,  
                  new_x, new_y, new_z,        
                  0, 0, 1)                       
    else:
       
        x, y, z = camera_pos
        gluLookAt(x, y, z,          
                  300, 300, 0,      
                  0, 0, 1)
        


#########grid###########   

def draw_grid():
    GRID_LENGTH=600
    cell=GRID_LENGTH/13
    glBegin(GL_QUADS)
    for i in range (0,13,1):
        for j in range (0,13,1):
            x1=i*cell
            x2=(i+1)*cell
            y1=j*cell
            y2=(j+1)*cell
            
            if (i+j)%2==0:
                glColor3f(1.0, 1.0, 1.0)
            else:
                glColor3f(0.7, 0.5, 0.94)

            glVertex3f(x1, y1, 0)
            glVertex3f(x2, y1, 0)
            glVertex3f(x2, y2, 0)
            glVertex3f(x1, y2, 0)
    glEnd()
    
   
    wall_height = 100
    

    min_x = 0
    max_x = GRID_LENGTH
    min_y = 0
    max_y = GRID_LENGTH
    
    # North wall (front)
    glBegin(GL_QUADS)
    glColor3f(0.0, 0.9725, 1.0) 
    glVertex3f(min_x, max_y, 0)
    glVertex3f(max_x, max_y, 0)
    glVertex3f(max_x, max_y, wall_height)
    glVertex3f(min_x, max_y, wall_height)
    glEnd()
    
    # South wall (back)
    glBegin(GL_QUADS)
    glColor3f(1.0, 1.0, 1.0)  
    glVertex3f(min_x, min_y, 0)
    glVertex3f(max_x, min_y, 0)
    glVertex3f(max_x, min_y, wall_height)
    glVertex3f(min_x, min_y, wall_height)
    glEnd()
    
    # East wall (right)
    glBegin(GL_QUADS)
    glColor3f(0.0, 0.0, 1.0)  
    glVertex3f(max_x, min_y, 0)
    glVertex3f(max_x, max_y, 0)
    glVertex3f(max_x, max_y, wall_height)
    glVertex3f(max_x, min_y, wall_height)
    glEnd()
    
    # West wall (left)
    glBegin(GL_QUADS)
    glColor3f(0.0, 1.0, 0.149)   
    glVertex3f(min_x, min_y, 0)
    glVertex3f(min_x, max_y, 0)
    glVertex3f(min_x, max_y, wall_height)
    glVertex3f(min_x, min_y, wall_height)
    glEnd()



def showScreen():
   
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity() 
    glViewport(0, 0, 1000, 800)  
    glEnable(GL_DEPTH_TEST)  
    setupCamera()  

    if not game_over:
        draw_text(10, 770, f"Score: {game_score}\n  Lives: {player_life}\n  Bullets Missed: {bullets_missed}")
        if cheat_mode:
            draw_text(10, 700, "CHEAT MODE ACTIVE - Press V to disable")
            draw_text(850, 770, "Invincible!")
    else:
        if player_life <= 0:
            draw_text(10, 770, "No more lives left")
            draw_text(10, 750, "GAME OVER - Press R to restart")
           
        else:
            draw_text(10, 770, "Too many bullets missed")
            draw_text(10, 750, "GAME OVER - Press R to restart")
      
        
    
 
    draw_grid()
    if camera_pos[2] >= 0: ### camera niche gele jate na dekha ja
        draw_human()
        draw_enemies()
        draw_bullets()
    else:
        draw_grid()
    
    glutSwapBuffers()

def idle():
    
    update_enemy_size()
    
    update_enemies()
    
    update_bullets()
    
    if cheat_mode:
        cheat_mode_function()
    
    if len(enemy_positions) < 5:
        spawn_new_enemy()
    
    glutPostRedisplay()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)  
    glutInitWindowSize(1000, 800)  
    glutInitWindowPosition(300,30) 
    wind = glutCreateWindow(b"Shooter Game") 
    initialize_enemies()
    glutDisplayFunc(showScreen) 
    glutKeyboardFunc(keyboardListener)  
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)  
    glutMainLoop()

if __name__ == "__main__":
    main()