import random
import math
import time
from OpenGL.GL import *    
from OpenGL.GLUT import *  
from OpenGL.GLU import *   

#window var
window_width = 1000
window_height = 800
#grid and track var
grid_size = 3300
grid_divisions = 20
track_width = 150
track_innerx_radius = 1485
track_innery_radius = 990
#outer track radius
track_outer_x_radius = track_innerx_radius + track_width
track_outer_y_radius = track_innery_radius + track_width
track_segments = 64
track_height = 3.0
# Vehicle constants
max_speed = 4.0
acceleration = 0.5
friction = 0.02
turn_speed = 3.0
slow_factor = 0.3  # Speed reduction when off track
# Camera settings
cam_initial_dist = 20.0
cam_initial_height = 10.0
cam_min_dist = 10.0
cam_max_dist = 40.0
cam_min_height = 5.0
cam_max_height = 20.0
cam_dist_step = 2.0
cam_angle_step = 5.0
# Obstacle and power-up properties
cone_base_size = 20
cone_height = 30
cone_count = 25
pothole_rad = 15
pothole_count = 17
min_obs_dist = 50
respawn_display = 2.0
flicker_count = 4
# Health and damage settings
max_health = 100
health_decrement = 25
pothole_speed_reduce = 0.7
# Bike-specific dynamics
bike_acceleration = 0.1
bike_friction = 0.03
bike_turn_speed = 2.0
bike_max_lean = 25.0
# Game timing and objectives
total_time = 180.0
req_laps = 5
# Power-up and power-down settings
powerup_count = 5
powerup_rad = 15
powerup_duration = 3.0
powerup_speed_multiplier = 2.0
powerdown_count = 5
powerdown_rad = 15
powerdown_time_reduce = 30.0
banana_pill_count = 5
banana_pill_rad = 15
banana_pill_duration = 4.0

class Gamestate:
    def __init__(self):
        # player er position at the center 
        self.player_x = track_innerx_radius + track_width / 2
        self.player_y = 0.0
        self.player_angle = 0.0  # Player's orientation in degrees
        self.prev_angle = 0.0  #  lap detection er jonno
        self.player_speed = 0.0  
        self.health = max_health  
        self.keys_pressed = set()  # jekono button pressed kina ta check korar jonno
        self.laps_completed = 0  
        self.crossed_start_line = False  # checker if crossed start line
        self.last_time = time.time()  
        # Camera properties
        self.cam_distance = cam_initial_dist
        self.cam_height = cam_initial_height
        self.cam_angle_offset = 90.0  # Camera angle relative to player
        # repawn er jonno prev states saved
        self.last_valid_x = self.player_x
        self.last_valid_y = self.player_y
        self.last_valid_angle = self.player_angle
        # obstacles and other feautres
        self.cones = []
        self.potholes = []
        self.powerups = []
        self.powerdowns = []
        self.banana_pills = []  
        self.banana_pill_active = False  
        self.banana_pill_timer = 0.0  
        self.game_over = False  
        self.start_screen = True  
        self.vehicle_type = None  
        self.bike_lean_angle = 0.0  # Bike lean for visual effect
        self.start_time = None  # Game start time
        self.final_time = None  # Time at game end
        self.first_person = False  # Camera mode (first or third person)
        self.powerup_active = False  # Power-up active status
        self.powerup_timer = 0.0  # Power-up duration timer
        self.original_max_speed = max_speed 
        

        
        
        #  cones kothay boshbe 
        angle_step = 2 * math.pi / cone_count
        for i in range(cone_count):
            angle = i * angle_step
            t = random.uniform(0, 1)  
            x_radius = track_innerx_radius + t * (track_outer_x_radius - track_innerx_radius)
            y_radius = track_innery_radius + t * (track_outer_y_radius - track_innery_radius)
            x = x_radius * math.cos(angle)
            y = y_radius * math.sin(angle)
            start_x = track_innerx_radius + track_width / 2
            start_y = 0.0
            dist_to_start = math.sqrt((x - start_x)**2 + (y - start_y)**2)
            # Ensure cones are not near start line
            if abs(angle) > 0.1 and abs(angle - 2 * math.pi) > 0.1 and dist_to_start > min_obs_dist:
                self.cones.append((x, y))
        # Place potholes randomly, avoiding cones and start line
        for i in range(pothole_count):
            # max_attempts = 100
            # for _ in range(max_attempts):
                angle = random.uniform(0, 2 * math.pi)
                t = random.uniform(0, 1)
                x_radius = track_innerx_radius + t * (track_outer_x_radius - track_innerx_radius)
                y_radius = track_innery_radius + t * (track_outer_y_radius - track_innery_radius)
                x = x_radius * math.cos(angle)
                y = y_radius * math.sin(angle)
                start_x = track_innerx_radius + track_width / 2
                start_y = 0.0
                dist_to_start = math.sqrt((x - start_x)**2 + (y - start_y)**2)
                if abs(angle) > 0.1 and abs(angle - 2 * math.pi) > 0.1 and dist_to_start > min_obs_dist:
                    valid = True
                    for cx, cy in self.cones:
                        dist = math.sqrt((x - cx)**2 + (y - cy)**2)
                        if dist < min_obs_dist:
                            valid = False
                            break
                    for px, py in self.potholes:
                        dist = math.sqrt((x - px)**2 + (y - py)**2)
                        if dist < min_obs_dist:
                            valid = False
                            break
                    if valid:
                        self.potholes.append((x, y))
                        break
        # Place power-ups randomly, avoiding other obstacles
        for i in range(powerup_count):
            max_attempts = 10
            for j in range(max_attempts):
                angle = random.uniform(0, 2 * math.pi)
                t = random.uniform(0, 1)
                x_radius = track_innerx_radius + t * (track_outer_x_radius - track_innerx_radius)
                y_radius = track_innery_radius + t * (track_outer_y_radius - track_innery_radius)
                x = x_radius * math.cos(angle)
                y = y_radius * math.sin(angle)
                start_x = track_innerx_radius + track_width / 2
                start_y = 0.0
                dist_to_start = math.sqrt((x - start_x)**2 + (y - start_y)**2)
                if abs(angle) > 0.1 and abs(angle - 2 * math.pi) > 0.1 and dist_to_start > min_obs_dist:
                    valid = True
                    for cx, cy in self.cones:
                        dist = math.sqrt((x - cx)**2 + (y - cy)**2)
                        if dist < min_obs_dist:
                            valid = False
                            break
                    for px, py in self.potholes:
                        dist = math.sqrt((x - px)**2 + (y - py)**2)
                        if dist < min_obs_dist:
                            valid = False
                            break
                    for ppx, ppy in self.powerups:
                        dist = math.sqrt((x - ppx)**2 + (y - ppy)**2)
                        if dist < min_obs_dist:
                            valid = False
                            break
                    if valid:
                        self.powerups.append((x, y))
                        break
        # Place power-downs randomly, avoiding other objects
        for i in range(powerdown_count):
            max_attempts = 20
            for k in range(max_attempts):
                angle = random.uniform(0, 2 * math.pi)
                t = random.uniform(0, 1)
                x_radius = track_innerx_radius + t * (track_outer_x_radius - track_innerx_radius)
                y_radius = track_innery_radius + t * (track_outer_y_radius - track_innery_radius)
                x = x_radius * math.cos(angle)
                y = y_radius * math.sin(angle)
                start_x = track_innerx_radius + track_width / 2
                start_y = 0.0
                dist_to_start = math.sqrt((x - start_x)**2 + (y - start_y)**2)
                if abs(angle) > 0.1 and abs(angle - 2 * math.pi) > 0.1 and dist_to_start > min_obs_dist:
                    valid = True
                    for cx, cy in self.cones:
                        dist = math.sqrt((x - cx)**2 + (y - cy)**2)
                        if dist < min_obs_dist:
                            valid = False
                            break
                    for px, py in self.potholes:
                        dist = math.sqrt((x - px)**2 + (y - py)**2)
                        if dist < min_obs_dist:
                            valid = False
                            break
                    for ppx, ppy in self.powerups:
                        dist = math.sqrt((x - ppx)**2 + (y - ppy)**2)
                        if dist < min_obs_dist:
                            valid = False
                            break
                    for pdx, pdy in self.powerdowns:
                        dist = math.sqrt((x - pdx)**2 + (y - pdy)**2)
                        if dist < min_obs_dist:
                            valid = False
                            break
                    if valid:
                        self.powerdowns.append((x, y))
                        break
        # Initialize respawn and flicker states
        for i in range(banana_pill_count):
            max_attempts = 20
            for l in range(max_attempts):
                angle = random.uniform(0, 2 * math.pi)
                t = random.uniform(0, 1)
                x_radius = track_innerx_radius + t * (track_outer_x_radius - track_innerx_radius)
                y_radius = track_innery_radius + t * (track_outer_y_radius - track_innery_radius)
                x = x_radius * math.cos(angle)
                y = y_radius * math.sin(angle)
                start_x = track_innerx_radius + track_width / 2
                start_y = 0.0
                dist_to_start = math.sqrt((x - start_x)**2 + (y - start_y)**2)
                if abs(angle) > 0.1 and abs(angle - 2 * math.pi) > 0.1 and dist_to_start > min_obs_dist:
                    valid = True
                    for cx, cy in self.cones:
                        dist = math.sqrt((x - cx)**2 + (y - cy)**2)
                        if dist < min_obs_dist:
                            valid = False
                            break
                    for px, py in self.potholes:
                        dist = math.sqrt((x - px)**2 + (y - py)**2)
                        if dist < min_obs_dist:
                            valid = False
                            break
                    for ppx, ppy in self.powerups:
                        dist = math.sqrt((x - ppx)**2 + (y - ppy)**2)
                        if dist < min_obs_dist:
                            valid = False
                            break
                    for pdx, pdy in self.powerdowns:
                        dist = math.sqrt((x - pdx)**2 + (y - pdy)**2)
                        if dist < min_obs_dist:
                            valid = False
                            break
                    for bpx, bpy in self.banana_pills:
                        dist = math.sqrt((x - bpx)**2 + (y - bpy)**2)
                        if dist < min_obs_dist:
                            valid = False
                            break
                    if valid:
                        self.banana_pills.append((x, y))
                        break
        self.respawn_timer = 0.0
        self.flicker_state = False
        self.flicker_count = 0
        self.last_collision_time = 0.0
        self.is_colliding = False

game_state = Gamestate()  

def init():
    glClearColor(0.529, 0.808, 0.922, 1.0)  # background er color at start
    glEnable(GL_DEPTH_TEST)  # Enable depth testing to prevent seeing through objects

def draw_grid():
    cell_size = grid_size / grid_divisions  # every cell er size
    half_grid = grid_size / 2  # boundary er jonno half size
    glBegin(GL_QUADS)  # Begin drawing grid as quads
    for i in range(-grid_divisions//2, grid_divisions//2):
        for j in range(-grid_divisions//2, grid_divisions//2):
            x1 = i * cell_size
            y1 = j * cell_size
            x2 = (i + 1) * cell_size
            y2 = (j + 1) * cell_size
            if (i + j) % 2 == 0:
                glColor3f(0.4, 0.8, 0.4)  # Light green f
            else:
                glColor3f(0.0, 0.5, 0.0)  # Dark green 
            glVertex3f(x1, y1, 0)
            glVertex3f(x2, y1, 0)
            glVertex3f(x2, y2, 0)
            glVertex3f(x1, y2, 0)
    glEnd()
    wall_height = 50  
    glBegin(GL_QUADS)  
    glColor3f(1.0, 0.0, 0.0)
    # Top wall
    glVertex3f(-half_grid, half_grid, 0)
    glVertex3f(half_grid, half_grid, 0)
    glVertex3f(half_grid, half_grid, wall_height)
    glVertex3f(-half_grid, half_grid, wall_height)
    # Bottom wall
    glVertex3f(-half_grid, -half_grid, 0)
    glVertex3f(half_grid, -half_grid, 0)
    glVertex3f(half_grid, -half_grid, wall_height)
    glVertex3f(-half_grid, -half_grid, wall_height)
    # Left wall
    glVertex3f(-half_grid, -half_grid, 0)
    glVertex3f(-half_grid, half_grid, 0)
    glVertex3f(-half_grid, half_grid, wall_height)
    glVertex3f(-half_grid, -half_grid, wall_height)
    # Right wall
    glVertex3f(half_grid, -half_grid, 0)
    glVertex3f(half_grid, half_grid, 0)
    glVertex3f(half_grid, half_grid, wall_height)
    glVertex3f(half_grid, -half_grid, wall_height)
    glEnd()

def draw_oval_track():
    glBegin(GL_QUADS)  # track er side draw korar jonno
    glColor3f(0.3, 0.3, 0.3) 
    for i in range(track_segments):
        angle1 = 2.0 * math.pi * i / track_segments
        angle2 = 2.0 * math.pi * (i+1) / track_segments
        # Inner track side
        inner_x1 = track_innerx_radius * math.cos(angle1)
        inner_y1 = track_innery_radius * math.sin(angle1)
        inner_x2 = track_innerx_radius * math.cos(angle2)
        inner_y2 = track_innery_radius * math.sin(angle2)
        glVertex3f(inner_x1, inner_y1, 0)
        glVertex3f(inner_x2, inner_y2, 0)
        glVertex3f(inner_x2, inner_y2, track_height)
        glVertex3f(inner_x1, inner_y1, track_height)
        # Outer track side
        outer_x1 = track_outer_x_radius * math.cos(angle1)
        outer_y1 = track_outer_y_radius * math.sin(angle1)
        outer_x2 = track_outer_x_radius * math.cos(angle2)
        outer_y2 = track_outer_y_radius * math.sin(angle2)
        glVertex3f(outer_x1, outer_y1, 0)
        glVertex3f(outer_x2, outer_y2, 0)
        glVertex3f(outer_x2, outer_y2, track_height)
        glVertex3f(outer_x1, outer_y1, track_height)
    glEnd()
    glBegin(GL_QUADS)  # Draw inner water area
    glColor3f(0.0, 0.5, 1.0)  
    for i in range(track_segments):
        angle1 = 2.0 * math.pi * i / track_segments
        angle2 = 2.0 * math.pi * (i+1) / track_segments
        inner_x1 = track_innerx_radius * math.cos(angle1)
        inner_y1 = track_innery_radius * math.sin(angle1)
        inner_x2 = track_innerx_radius * math.cos(angle2)
        inner_y2 = track_innery_radius * math.sin(angle2)
        glVertex3f(0, 0, track_height)
        glVertex3f(inner_x1, inner_y1, track_height)
        glVertex3f(inner_x2, inner_y2, track_height)
        glVertex3f(0, 0, track_height)
    glEnd()
    glBegin(GL_QUADS)  # Draw track surface
    for i in range(track_segments):
        angle1 = 2.0 * math.pi * i / track_segments
        angle2 = 2.0 * math.pi * (i+1) / track_segments
        inner_x1 = track_innerx_radius * math.cos(angle1)
        inner_y1 = track_innery_radius * math.sin(angle1)
        outer_x1 = track_outer_x_radius * math.cos(angle1)
        outer_y1 = track_outer_y_radius * math.sin(angle1)
        inner_x2 = track_innerx_radius * math.cos(angle2)
        inner_y2 = track_innery_radius * math.sin(angle2)
        outer_x2 = track_outer_x_radius * math.cos(angle2)
        outer_y2 = track_outer_y_radius * math.sin(angle2)
        glColor3f(0.3, 0.3, 0.3)  # Gray for track surface
        glVertex3f(outer_x1, outer_y1, track_height)
        glVertex3f(inner_x1, inner_y1, track_height)
        glVertex3f(inner_x2, inner_y2, track_height)
        glVertex3f(outer_x2, outer_y2, track_height)
    glEnd()
    glBegin(GL_LINES)  # outer lane markings
    for i in range(track_segments):
        if i % 4 < 2:
            if i % 8 < 4:
                glColor3f(1.0, 1.0, 1.0)  # White lines
            else:
                glColor3f(0.0, 0.0, 0.0)  # Black lines
            angle1 = 2.0 * math.pi * i / track_segments
            angle2 = 2.0 * math.pi * (i+1) / track_segments
            outer_x1 = track_outer_x_radius * math.cos(angle1)
            outer_y1 = track_outer_y_radius * math.sin(angle1)
            outer_x2 = track_outer_x_radius * math.cos(angle2)
            outer_y2 = track_outer_y_radius * math.sin(angle2)
            glVertex3f(outer_x1, outer_y1, track_height + 0.1)
            glVertex3f(outer_x2, outer_y2, track_height + 0.1)
    glEnd()
    glBegin(GL_LINES)  # Draw inner lane markings
    for i in range(track_segments):
        if i % 4 < 2:
            if i % 8 < 4:
                glColor3f(1.0, 0.0, 1.0)  
            else:
                glColor3f(0.0, 0.0, 0.0)  
            angle1 = 2.0 * math.pi * i / track_segments
            angle2 = 2.0 * math.pi * (i+1) / track_segments
            inner_x1 = track_innerx_radius * math.cos(angle1)
            inner_y1 = track_innery_radius * math.sin(angle1)
            inner_x2 = track_innerx_radius * math.cos(angle2)
            inner_y2 = track_innery_radius * math.sin(angle2)
            glVertex3f(inner_x1, inner_y1, track_height + 0.1)
            glVertex3f(inner_x2, inner_y2, track_height + 0.1)
    glEnd()
    curb_width = 10  # Width of track curbs
    glBegin(GL_QUADS)  # outer curbs hocche markings er outer side er jonno
    for i in range(track_segments):
        if i % 4 < 2:
            if i % 8 < 4:
                glColor3f(1.0, 0.0, 0.0)  # Red curbs
            else:
                glColor3f(0.2, 0.2, 0.8)  # Blue curbs
            angle1 = 2.0 * math.pi * i / track_segments
            angle2 = 2.0 * math.pi * (i+1) / track_segments
            outer_x1 = (track_outer_x_radius + curb_width) * math.cos(angle1)
            outer_y1 = (track_outer_y_radius + curb_width) * math.sin(angle1)
            outer_x2 = (track_outer_x_radius + curb_width) * math.cos(angle2)
            outer_y2 = (track_outer_y_radius + curb_width) * math.sin(angle2)
            curb_x1 = track_outer_x_radius * math.cos(angle1)
            curb_y1 = track_outer_y_radius * math.sin(angle1)
            curb_x2 = track_outer_x_radius * math.cos(angle2)
            curb_y2 = track_outer_y_radius * math.sin(angle2)
            glVertex3f(curb_x1, curb_y1, track_height + 0.2)
            glVertex3f(curb_x2, curb_y2, track_height + 0.2)
            glVertex3f(outer_x2, outer_y2, track_height + 0.2)
            glVertex3f(outer_x1, outer_y1, track_height + 0.2)
    glEnd()
    glBegin(GL_QUADS)  # inner curbs hocche markings er inner side er jonno
    for i in range(track_segments):
        if i % 4 < 2:
            if i % 8 < 4:
                glColor3f(1.0, 0.0, 0.0)  # Red curbs
            else:
                glColor3f(1.0, 1.0, 1.0)  # White curbs
            angle1 = 2.0 * math.pi * i / track_segments
            angle2 = 2.0 * math.pi * (i+1) / track_segments
            inner_x1 = (track_innerx_radius - curb_width) * math.cos(angle1)
            inner_y1 = (track_innery_radius - curb_width) * math.sin(angle1)
            inner_x2 = (track_innerx_radius - curb_width) * math.cos(angle2)
            inner_y2 = (track_innery_radius - curb_width) * math.sin(angle2)
            curb_x1 = track_innerx_radius * math.cos(angle1)
            curb_y1 = track_innery_radius * math.sin(angle1)
            curb_x2 = track_innerx_radius * math.cos(angle2)
            curb_y2 = track_innery_radius * math.sin(angle2)
            glVertex3f(curb_x1, curb_y1, track_height + 0.2)
            glVertex3f(curb_x2, curb_y2, track_height + 0.2)
            glVertex3f(inner_x2, inner_y2, track_height + 0.2)
            glVertex3f(inner_x1, inner_y1, track_height + 0.2)
    glEnd()
    glBegin(GL_QUADS)  # checkered pattern er jonno
    finish_line_angle = 0
    inner_x = track_innerx_radius * math.cos(finish_line_angle)
    inner_y = track_innery_radius * math.sin(finish_line_angle)
    outer_x = track_outer_x_radius * math.cos(finish_line_angle)
    outer_y = track_outer_y_radius * math.sin(finish_line_angle)
    track_direction_x = -math.sin(finish_line_angle)
    track_direction_y = math.cos(finish_line_angle)
    line_length = 30
    rows = 5
    cols = 5
    track_width = math.sqrt((outer_x - inner_x)**2 + (outer_y - inner_y)**2)
    square_width = track_width / cols
    square_height = line_length / rows
    for row in range(rows):
        for col in range(cols):
            pos_factor = col / cols
            base_x = inner_x + (outer_x - inner_x) * pos_factor
            base_y = inner_y + (outer_y - inner_y) * pos_factor
            next_pos_factor = (col + 1) / cols
            next_x = inner_x + (outer_x - inner_x) * next_pos_factor
            next_y = inner_y + (outer_y - inner_y) * next_pos_factor
            row_start = -line_length/2 + row * square_height
            row_end = -line_length/2 + (row + 1) * square_height
            if (row + col) % 2 == 0:
                glColor3f(0.0, 0.0, 0.0)  
            else:
                glColor3f(1.0, 1.0, 1.0)  
            x1 = base_x + track_direction_x * row_start
            y1 = base_y + track_direction_y * row_start
            x2 = next_x + track_direction_x * row_start
            y2 = next_y + track_direction_y * row_start
            x3 = next_x + track_direction_x * row_end
            y3 = next_y + track_direction_y * row_end
            x4 = base_x + track_direction_x * row_end
            y4 = base_y + track_direction_y * row_end
            glVertex3f(x1, y1, track_height + 0.1)
            glVertex3f(x2, y2, track_height + 0.1)
            glVertex3f(x3, y3, track_height + 0.1)
            glVertex3f(x4, y4, track_height + 0.1)
    glEnd()



def draw_cones():
    segments = 12  # Number of segments for cone geometry
    for x, y in game_state.cones:
        glPushMatrix()
        glTranslatef(x, y, track_height)
        base_height = 2  # Height of cone base
        half_size = cone_base_size / 2
        glColor3f(1.0, 0.5, 0.0)  
        glBegin(GL_QUADS)  # base and sides er jonno
        # Top face of base
        glVertex3f(-half_size, -half_size, base_height)
        glVertex3f(half_size, -half_size, base_height)
        glVertex3f(half_size, half_size, base_height)
        glVertex3f(-half_size, half_size, base_height)
        # Bottom face of base
        glVertex3f(-half_size, -half_size, 0)
        glVertex3f(half_size, -half_size, 0)
        glVertex3f(half_size, half_size, 0)
        glVertex3f(-half_size, half_size, 0)
        # Side faces of base
        glVertex3f(-half_size, -half_size, 0)
        glVertex3f(-half_size, -half_size, base_height)
        glVertex3f(-half_size, half_size, base_height)
        glVertex3f(-half_size, half_size, 0)
        glVertex3f(half_size, -half_size, 0)
        glVertex3f(half_size, -half_size, base_height)
        glVertex3f(half_size, half_size, base_height)
        glVertex3f(half_size, half_size, 0)
        glVertex3f(-half_size, -half_size, 0)
        glVertex3f(-half_size, -half_size, base_height)
        glVertex3f(half_size, -half_size, base_height)
        glVertex3f(half_size, -half_size, 0)
        glVertex3f(-half_size, half_size, 0)
        glVertex3f(-half_size, half_size, base_height)
        glVertex3f(half_size, half_size, base_height)
        glVertex3f(half_size, half_size, 0)
        glEnd()
        num_stripes = 4  # Number of alternating color stripes
        section_height = cone_height / (num_stripes * 2)
        for i in range(num_stripes * 2):
            z_bottom = base_height + i * section_height
            z_top = base_height + (i + 1) * section_height
            radius_bottom = (cone_base_size / 2) * (1 - (z_bottom - base_height) / cone_height)
            radius_top = (cone_base_size / 2) * (1 - (z_top - base_height) / cone_height)
            if i % 2 == 0:
                glColor3f(1.0, 0.5, 0.0)  
            else:
                glColor3f(1.0, 1.0, 1.0)  
            glBegin(GL_QUADS)  # cone body
            for j in range(segments):
                angle1 = 2.0 * math.pi * j / segments
                angle2 = 2.0 * math.pi * (j + 1) / segments
                x_bottom1 = radius_bottom * math.cos(angle1)
                y_bottom1 = radius_bottom * math.sin(angle1)
                x_bottom2 = radius_bottom * math.cos(angle2)
                y_bottom2 = radius_bottom * math.sin(angle2)
                x_top1 = radius_top * math.cos(angle1)
                y_top1 = radius_top * math.sin(angle1)
                x_top2 = radius_top * math.cos(angle2)
                y_top2 = radius_top * math.sin(angle2)
                glVertex3f(x_bottom1, y_bottom1, z_bottom)
                glVertex3f(x_bottom2, y_bottom2, z_bottom)
                glVertex3f(x_top2, y_top2, z_top)
                glVertex3f(x_top1, y_top1, z_top)
            glEnd()
        glPopMatrix() 

def draw_potholes():
    segments = 12  
    for x, y in game_state.potholes:
        glPushMatrix()  
        glTranslatef(x, y, track_height + 0.05)  
        glColor3f(0.5, 0.3, 0.1)  
        glBegin(GL_QUADS)  
        for i in range(segments):
            angle1 = 2.0 * math.pi * i / segments
            angle2 = 2.0 * math.pi * (i + 1) / segments
            px1 = pothole_rad * math.cos(angle1)
            py1 = pothole_rad * math.sin(angle1)
            px2 = pothole_rad * math.cos(angle2)
            py2 = pothole_rad * math.sin(angle2)
            glVertex3f(0, 0, 0)
            glVertex3f(px1, py1, 0)
            glVertex3f(px2, py2, 0)
            glVertex3f(0, 0, 0)
        glEnd()
        glPopMatrix()  

def draw_powerups():
    segments = 12  
    for x, y in game_state.powerups:
        glPushMatrix() 
        glTranslatef(x, y, track_height + 0.05)  
        glColor3f(1.0, 1.0, 0.0) 
        glBegin(GL_QUADS)  
        for i in range(segments):
            angle1 = 2.0 * math.pi * i / segments
            angle2 = 2.0 * math.pi * (i + 1) / segments
            px1 = powerup_rad * math.cos(angle1)
            py1 = powerup_rad * math.sin(angle1)
            px2 = powerup_rad * math.cos(angle2)
            py2 = powerup_rad * math.sin(angle2)
            glVertex3f(0, 0, 0)
            glVertex3f(px1, py1, 0)
            glVertex3f(px2, py2, 0)
            glVertex3f(0, 0, 0)
        glEnd()
        glPopMatrix()  

def draw_powerdowns():
    segments = 12  
    for x, y in game_state.powerdowns:
        glPushMatrix()  
        glTranslatef(x, y, track_height + 0.05)  
        glColor3f(1.0, 0.0, 0.0)  
        glBegin(GL_QUADS)  
        for i in range(segments):
            angle1 = 2.0 * math.pi * i / segments
            angle2 = 2.0 * math.pi * (i + 1) / segments
            px1 = powerdown_rad * math.cos(angle1)
            py1 = powerdown_rad * math.sin(angle1)
            px2 = powerdown_rad * math.cos(angle2)
            py2 = powerdown_rad * math.sin(angle2)
            glVertex3f(0, 0, 0)
            glVertex3f(px1, py1, 0)
            glVertex3f(px2, py2, 0)
            glVertex3f(0, 0, 0)
        glEnd()
        glPopMatrix()  

def draw_banana_pills():
    segments = 12  
    for x, y in game_state.banana_pills:
        glPushMatrix() 
        glTranslatef(x, y, track_height + 0.05)  
        glColor3f(1.0, 0.5, 0.0)  
        glBegin(GL_QUADS) 
        for i in range(segments):
            angle1 = 2.0 * math.pi * i / segments
            angle2 = 2.0 * math.pi * (i + 1) / segments
            px1 = banana_pill_rad * math.cos(angle1)
            py1 = banana_pill_rad * math.sin(angle1)
            px2 = banana_pill_rad * math.cos(angle2)
            py2 = banana_pill_rad * math.sin(angle2)
            glVertex3f(0, 0, 0)
            glVertex3f(px1, py1, 0)
            glVertex3f(px2, py2, 0)
            glVertex3f(0, 0, 0)
        glEnd()
        glPopMatrix()  

def draw_vehicle():
    # only draw vehivle jokhon respawn timer 0 er kom or flicker state false
    # jokhon flicker state true, tokhon flicker count er mod 2 er shathe check korbe
    if game_state.respawn_timer <= 0 or (game_state.flicker_state and game_state.flicker_count % 2 == 0):
        glPushMatrix()  
        if game_state.vehicle_type == 'car':
            glTranslatef(game_state.player_x, game_state.player_y, track_height + 1.5)
        else:
            glTranslatef(game_state.player_x, game_state.player_y, track_height + 4.5)

        if game_state.vehicle_type == 'car':
            glRotatef(90, 0, 0, 1)  
        glRotatef(game_state.player_angle, 0, 0, 1)  # Rotate to player angle
        glRotatef(90.0, 0, 0, 1)
        if game_state.vehicle_type == 'car':
            glScalef(0.15, 0.15, 0.15)  
            glColor3f(1.0, 1.0, 0.0)  
            # Draw car body (main block)
            glPushMatrix()
            glTranslatef(0, -10, 20)
            glScalef(35, 40, 15)
            glutSolidCube(1)
            glPopMatrix()
            # Draw car rear section
            glColor3f(1.0, 1.0, 0.0)
            glPushMatrix()
            glTranslatef(0, -40, 15)
            glScalef(38, 20, 10)
            glutSolidCube(1)
            glPopMatrix()
            # Draw car front section
            glColor3f(1.0, 1.0, 0.0)
            glPushMatrix()
            glTranslatef(0, 14, 15)
            glScalef(38, 10, 10)
            glutSolidCube(1)
            glPopMatrix()
            # Draw front windshield
            glColor3f(0.3, 0.3, 0.8)
            glPushMatrix()
            glTranslatef(0, -30, 25)
            glRotatef(-45, 1, 0, 0)
            glScalef(34, 1, 10)
            glutSolidCube(1)
            glPopMatrix()
            # Draw rear windshield
            glColor3f(0.3, 0.3, 0.8)
            glPushMatrix()
            glTranslatef(0, 12, 25)
            glRotatef(45, 1, 0, 0)
            glScalef(34, 1, 10)
            glutSolidCube(1)
            glPopMatrix()
            # Draw front left light
            glColor3f(1.0, 1.0, 1.0)
            glPushMatrix()
            glTranslatef(-15, -50, 17)
            glScalef(8, 2, 5)
            glutSolidCube(1)
            glPopMatrix()
            # Draw front right light
            glPushMatrix()
            glTranslatef(15, -50, 17)
            glScalef(8, 2, 5)
            glutSolidCube(1)
            glPopMatrix()
            # Draw rear left light
            glColor3f(1.0, 0.0, 0.0)
            glPushMatrix()
            glTranslatef(-15, 20, 17)
            glScalef(8, 2, 5)
            glutSolidCube(1)
            glPopMatrix()
            # Draw rear right light
            glPushMatrix()
            glTranslatef(15, 20, 17)
            glScalef(8, 2, 5)
            glutSolidCube(1)
            glPopMatrix()
            # Draw front left wheel
            glColor3f(0.1, 0.1, 0.1)
            glPushMatrix()
            glTranslatef(-22, -35, 0)
            glRotatef(90, 0, 1, 0)
            gluCylinder(gluNewQuadric(), 10, 10, 10, 12, 2)
            glPopMatrix()
            # Draw front left wheel hub
            glColor3f(0.8, 0.8, 0.8)
            glPushMatrix()
            glTranslatef(-17, -35, 0)
            glRotatef(90, 0, 1, 0)
            gluCylinder(gluNewQuadric(), 6.0, 6.0, 1.0, 10, 1)  
            glTranslatef(0.0, 0.0, 0.5) 
            glColor3f(0.5, 0.5, 0.5)  
            gluSphere(gluNewQuadric(), 2.0, 10, 10)
            glPopMatrix() 
            # Draw front right wheel
            glColor3f(0.1, 0.1, 0.1)
            glPushMatrix()
            glTranslatef(22, -35, 0)
            glRotatef(-90, 0, 1, 0)
            gluCylinder(gluNewQuadric(), 10, 10, 10, 12, 2)
            glPopMatrix()
            # Draw front right wheel hub
            glColor3f(0.8, 0.8, 0.8)
            glPushMatrix()
            glTranslatef(17, -35, 0)
            glRotatef(-90, 0, 1, 0)
            gluCylinder(gluNewQuadric(), 6.0, 6.0, 1.0, 10, 1)  
            glTranslatef(0.0, 0.0, 0.5) 
            glColor3f(0.5, 0.5, 0.5)  
            gluSphere(gluNewQuadric(), 2.0, 10, 10)  
            glPopMatrix()
            # Draw rear left wheel
            glColor3f(0.1, 0.1, 0.1)
            glPushMatrix()
            glTranslatef(-22, 13, 0.5)
            glRotatef(90, 0, 1, 0)
            gluCylinder(gluNewQuadric(), 10, 10, 10, 12, 2)
            glPopMatrix()
            # Draw rear left wheel hub
            glColor3f(0.8, 0.8, 0.8)
            glPushMatrix()
            glTranslatef(-17, 13, 0.5)
            glRotatef(90, 0, 1, 0)
            gluCylinder(gluNewQuadric(), 6.0, 6.0, 1.0, 10, 1)  
            glTranslatef(0.0, 0.0, 0.5) 
            glColor3f(0.5, 0.5, 0.5) 
            gluSphere(gluNewQuadric(), 2.0, 10, 10)  
            glPopMatrix()
            
            # Draw rear right wheel
            glColor3f(0.1, 0.1, 0.1)
            glPushMatrix()
            glTranslatef(22, 13, 0.5)
            glRotatef(-90, 0, 1, 0)
            gluCylinder(gluNewQuadric(), 10, 10, 10, 12, 2)
            glPopMatrix()
            # Draw rear right wheel hub
            glColor3f(0.8, 0.8, 0.8)
            glPushMatrix()
            glTranslatef(17, 13, 0.5)
            glRotatef(-90, 0, 1, 0)
            gluCylinder(gluNewQuadric(), 6.0, 6.0, 1.0, 10, 1)  
            glTranslatef(0.0, 0.0, 0.5)  
            glColor3f(0.5, 0.5, 0.5)  
            gluSphere(gluNewQuadric(),2.0, 10, 10)  
            glPopMatrix()

        elif game_state.vehicle_type == 'bike':
            glScalef(0.1, 0.1, 0.1)  
            glRotatef(game_state.bike_lean_angle, 1, 0, 0)  
            glColor3f(0.7, 0.0, 0.0)  
            glPushMatrix()
            glTranslatef(0, 0, 30)  
            # Draw bike frame components
            glPushMatrix()
            glTranslatef(20, 0, 20)
            glRotatef(-15, 0, 1, 0)
            glScalef(3.0, 0.6, 0.6)
            glutSolidCube(40)
            glPopMatrix()
            glPushMatrix()
            glTranslatef(20, 0, 0)
            glRotatef(-25, 0, 1, 0)
            glScalef(2.5, 0.5, 0.5)
            glutSolidCube(40)
            glPopMatrix()
            glPushMatrix()
            glTranslatef(-30, 0, 20)
            glRotatef(30, 0, 1, 0)
            glScalef(2.0, 0.5, 0.5)
            glutSolidCube(40)
            glPopMatrix()
            glPopMatrix()
            # Draw bike seat
            glColor3f(0.1, 0.1, 0.1)
            glPushMatrix()
            glTranslatef(-25, 0, 50)
            glScalef(1.8, 0.8, 0.3)
            glutSolidCube(35)
            glPopMatrix()
            # Draw fuel tank
            glColor3f(0.8, 0.8, 0.8)
            glPushMatrix()
            glTranslatef(70, 0, 25)
            glRotatef(60, 0, 1, 0)
            gluCylinder(gluNewQuadric(), 4, 4, 55, 10, 10)
            glPopMatrix()
            # Draw engine
            glColor3f(0.7, 0.0, 0.0)
            glPushMatrix()
            glTranslatef(70, 0, 30)
            glRotatef(60, 0, 1, 0)
            gluCylinder(gluNewQuadric(), 6, 6, 45, 10, 10)
            glPopMatrix()
            # Draw front mudguard
            glPushMatrix()
            glTranslatef(80, 0, 75)
            glColor3f(0.7, 0.7, 0.7)
            glutSolidCube(10)
            glPushMatrix()
            glTranslatef(0, -25, 0)
            glRotatef(90, 1, 0, 0)
            glColor3f(0.2, 0.2, 0.2)
            gluCylinder(gluNewQuadric(), 3, 3, 25, 8, 2)
            glPopMatrix()
            glPushMatrix()
            glTranslatef(0, 25, 0)
            glRotatef(-90, 1, 0, 0)
            glColor3f(0.2, 0.2, 0.2)
            gluCylinder(gluNewQuadric(), 3, 3, 25, 8, 2)
            glPopMatrix()
            glPopMatrix()
            # Draw bike body
            glColor3f(0.3, 0.3, 0.3)
            glPushMatrix()
            glTranslatef(0, 0, 15)
            glScalef(1.0, 0.8, 0.8)
            glutSolidCube(40)
            glPushMatrix()
            glTranslatef(0, 0, 25)
            glColor3f(0.4, 0.4, 0.4)
            glScalef(0.8, 0.7, 0.5)
            glutSolidCube(30)
            glPopMatrix()
            glPopMatrix()
            # Draw handlebars
            glColor3f(0.5, 0.5, 0.5)
            glPushMatrix()
            glTranslatef(-10, 0, 20)
            glRotatef(70, 0, 1, 0)
            gluCylinder(gluNewQuadric(), 5, 5, 30, 8, 2)
            glPopMatrix()
            # Draw exhaust
            glColor3f(0.6, 0.6, 0.6)
            glPushMatrix()
            glTranslatef(-40, 0, 15)
            glRotatef(90, 0, 1, 0)
            gluCylinder(gluNewQuadric(), 7, 8, 60, 10, 3)
            glPopMatrix()
            # Draw front wheel
            glColor3f(0.1, 0.1, 0.1)
            glPushMatrix()
            glTranslatef(90, 0, 0)
            glRotatef(90, 1, 0, 0)
            gluCylinder(gluNewQuadric(), 45, 45, 8, 20, 5)
            glColor3f(0.75, 0.75, 0.75)
            #lTranslatef(0, 0, 4)
            glTranslatef(0.0, 0.0, 0.5)  
            gluCylinder(gluNewQuadric(), 15.0, 15.0, 0.5, 10, 1)  
            glTranslatef(0.0, 0.0, 0.25)
            glColor3f(0.6, 0.6, 0.6)  
            gluSphere(gluNewQuadric(),5.0, 10, 10)  
 
            glPopMatrix()
            # Draw rear wheel
            glColor3f(0.1, 0.1, 0.1)
            glPushMatrix()
            glTranslatef(-75, 4.65, 0)
            glRotatef(90, 1, 0, 0)
            gluCylinder(gluNewQuadric(), 35, 35, 8, 20, 5)
            glColor3f(0.75, 0.75, 0.75)
            glTranslatef(0, 0, 4)
            glTranslatef(0.0, 0.0, 0.5)  
            gluCylinder(gluNewQuadric(), 15.0, 15.0, 0.5, 10, 1)  
            glTranslatef(0.0, 0.0, 0.25)
            glColor3f(0.6, 0.6, 0.6)
            gluSphere(gluNewQuadric(),5.0, 10, 10)  
            glPopMatrix()
            # Draw bike fairing
            glColor3f(0.8, 0.0, 0.0)
            glPushMatrix()
            glTranslatef(20, 0, 60)
            glPushMatrix()
            glScalef(1.8, 1.0, 0.8)
            glutSolidCube(30)
            glPopMatrix()
            glTranslatef(0, 0, 15)
            glScalef(1.8, 1.0, 0.3)
            glutSolidCube(30)
            glPopMatrix()
            # Draw headlight
            glPushMatrix()
            glTranslatef(95, 0, 40)
            glRotatef(20, 1, 0, 0)
            gluCylinder(gluNewQuadric(), 15, 13, 10, 16, 4)
            glColor3f(0.9, 0.9, 0.7)
            glTranslatef(0, 0, 9)
            glRotatef(90, 0, 1, 0)
            glScalef(13.0, 13.0, 0.5) 
            gluSphere(gluNewQuadric(),1.0, 16, 16)  
            glPopMatrix()
            # Draw rear light
            glColor3f(0.8, 0.1, 0.1)
            glPushMatrix()
            glTranslatef(-80, 0, 40)
            glScalef(0.3, 1.0, 0.5)
            glutSolidCube(15)
            glPopMatrix()
            # Draw left foot peg
            glColor3f(0.7, 0.0, 0.0)
            glPushMatrix()
            glTranslatef(-20, 15, 30)
            glRotatef(15, 0, 0, 1)
            glScalef(1.5, 0.1, 0.8)
            glutSolidCube(40)
            glPopMatrix()
            # Draw right foot peg
            glColor3f(0.7, 0.0, 0.0)
            glPushMatrix()
            glTranslatef(-20, -15, 30)
            glRotatef(-15, 0, 0, 1)
            glScalef(1.5, 0.1, 0.8)
            glutSolidCube(40)
            glPopMatrix()
        glPopMatrix()  

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1.0, 1.0, 1.0)  
    glMatrixMode(GL_PROJECTION)  
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, window_width, 0, window_height)  
    glMatrixMode(GL_MODELVIEW)  
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)  
    for ch in text:
        glutBitmapCharacter(font, ord(ch))  
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

def draw_start_screen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # screen clear kore
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, window_width, 0, window_height) 
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    draw_text(window_width/2 - 60, window_height/2 + 50, "Select Vehicle:")
    draw_text(window_width/2 - 60, window_height/2 + 10, "Press 'b' for Bike")
    draw_text(window_width/2 - 60, window_height/2 - 30, "Press 'c' for Car")
    glMatrixMode(GL_PROJECTION)

    glBegin(GL_QUADS)  # black bg for vehicle selection
    glColor3f(0.0, 0.0, 0.0)
    glVertex2f(window_width/2 - 200, window_height/2 - 100)
    glVertex2f(window_width/2 + 200, window_height/2 - 100)
    glVertex2f(window_width/2 + 200, window_height/2 + 100)
    glVertex2f(window_width/2 - 200, window_height/2 + 100)
    glEnd()

    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

def draw_hud():# shob bars related object draw kora hoy ekhane
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, window_width, 0, window_height)  
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    # Draw health bar
    glBegin(GL_QUADS)
    glColor3f(0.0, 1.0, 0.0)  #
    glVertex2f(10, window_height - 50)
    glVertex2f(10 + game_state.health * 2, window_height - 50)
    glVertex2f(10 + game_state.health * 2, window_height - 70)
    glVertex2f(10, window_height - 70)
    glEnd()
    speed = abs(game_state.player_speed)  
    # Draw speed bar
    glBegin(GL_QUADS)
    glColor3f(0.0, 0.0, 1.0)  # Blue for speed
    glVertex2f(10, window_height - 110)
    glVertex2f(10 + speed * 50, window_height - 110)
    glVertex2f(10 + speed * 50, window_height - 130)
    glVertex2f(10, window_height - 130)
    glEnd()
    # Draw HUD text
    draw_text(10, window_height - 30, f"Health: {game_state.health}%")
    draw_text(10, window_height - 90, f"Speed: {speed:.1f}")
    draw_text(window_width - 150, window_height - 30, f"Laps: {game_state.laps_completed}/5")
    if game_state.start_time:
        if game_state.game_over and game_state.final_time is not None:
            time_remaining = game_state.final_time
        else:
            time_remaining = max(0, total_time - (time.time() - game_state.start_time))
        minutes = int(time_remaining // 60)
        seconds = int(time_remaining % 60)
        draw_text(window_width - 150, window_height - 50, f"Time: {minutes:02d}:{seconds:02d}")
    if game_state.powerup_active:
        powerup_time_left = max(0, powerup_duration - game_state.powerup_timer)
        draw_text(10, window_height - 150, f"Speed Boost: {powerup_time_left:.1f}s")

    if game_state.game_over:  # Draw game over background
        if game_state.laps_completed >= req_laps:
            draw_text(window_width/2 - 50, window_height/2 + 10, "JITSEN BHAI!")  
        else:
            draw_text(window_width/2 - 60, window_height/2 + 10, "Game Over!")
        glBegin(GL_QUADS)
        glColor3f(0.0, 0.0, 0.0)
        glVertex2f(window_width/2 - 150, window_height/2 - 50)
        glVertex2f(window_width/2 + 150, window_height/2 - 50)
        glVertex2f(window_width/2 + 150, window_height/2 + 50)
        glVertex2f(window_width/2 - 150, window_height/2 + 50)
        glEnd()

    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

def setup_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, window_width / window_height, 0.1, 3000)  # Set perspective projection
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    if game_state.first_person:
        angle_rad = math.radians(game_state.player_angle + 90)  # Player's forward direction
        if game_state.vehicle_type == 'car':
            offset_x = 3.0 * math.cos(angle_rad)
            offset_y = 3.0 * math.sin(angle_rad)
            cam_height = track_height + 5.0
        else:
            offset_x = 9.0 * math.cos(angle_rad)
            offset_y = 3.5 * math.sin(angle_rad)
            cam_height = track_height + 10.0
        cam_x = game_state.player_x + offset_x
        cam_y = game_state.player_y + offset_y
        look_x = cam_x + math.cos(angle_rad)
        look_y = cam_y + math.sin(angle_rad)
        gluLookAt(
            cam_x, cam_y, cam_height,  # Camera position
            look_x, look_y, cam_height,  # Look-at point
            0, 0, 1  # Up vector
        )
    else:
        angle_rad = math.radians(game_state.player_angle + game_state.cam_angle_offset)
        cam_x = game_state.player_x - game_state.cam_distance * math.cos(angle_rad)
        cam_y = game_state.player_y - game_state.cam_distance * math.sin(angle_rad)
        gluLookAt(
            cam_x, cam_y, game_state.cam_height,  # Camera position
            game_state.player_x, game_state.player_y, track_height + 3.75,  # Look-at point
            0, 0, 1  # Up vector
        )

def is_on_track(x, y):
    # track boundaries er moddhe ache ki na
    norm_x = x / track_outer_x_radius
    norm_y = y / track_outer_y_radius
    outer_dist = math.sqrt(norm_x**2 + norm_y**2)
    norm_x_inner = x / track_innerx_radius
    norm_y_inner = y / track_innery_radius
    inner_dist = math.sqrt(norm_x_inner**2 + norm_y_inner**2)
    return outer_dist <= 1.0 and inner_dist >= 1.0

def is_in_water(x, y):
    # water e neme gese ki na
    norm_x_inner = x / track_innerx_radius
    norm_y_inner = y / track_innery_radius
    inner_dist = math.sqrt(norm_x_inner**2 + norm_y_inner**2)
    return inner_dist < 1.0

def check_collision(x, y):
    current_time = time.time()
    if current_time - game_state.last_collision_time < 0.5:  
        return False
    kart_x = x
    kart_y = y
    kart_half_width = 1.9
    kart_half_length = 2.5
    half_cone_size = cone_base_size / 2
    #  cone collisions
    for cone_x, cone_y in game_state.cones:
        if (abs(kart_x - cone_x) < (kart_half_width + half_cone_size) and
            abs(kart_y - cone_y) < (kart_half_length + half_cone_size)):
            return True
    #  pothole collisions
    for pothole_x, pothole_y in game_state.potholes:
        dist = math.sqrt((kart_x - pothole_x)**2 + (kart_y - pothole_y)**2)
        if dist < (pothole_rad + max(kart_half_width, kart_half_length)):
            return True
    return False

def check_powerup_collision(x, y):
    kart_x = x
    kart_y = y
    kart_half_width = 1.9
    kart_half_length = 2.5
    to_remove = None
    #  power-up collisions
    for powerup_x, powerup_y in game_state.powerups:
        dist = math.sqrt((kart_x - powerup_x)**2 + (kart_y - powerup_y)**2)
        if dist < (powerup_rad + max(kart_half_width, kart_half_length)):
            to_remove = (powerup_x, powerup_y)
            break
    if to_remove:
        game_state.powerups.remove(to_remove)
        return True
    return False

def check_powerdown_collision(x, y):
    kart_x = x
    kart_y = y
    kart_half_width = 1.9
    kart_half_length = 2.5
    to_remove = None
    #  power-down collisions
    for powerdown_x, powerdown_y in game_state.powerdowns:
        dist = math.sqrt((kart_x - powerdown_x)**2 + (kart_y - powerdown_y)**2)
        if dist < (powerdown_rad + max(kart_half_width, kart_half_length)):
            to_remove = (powerdown_x, powerdown_y)
            break
    if to_remove:
        game_state.powerdowns.remove(to_remove)
        return True
    return False

def check_banana_pill_collision(x, y):
    kart_x = x
    kart_y = y
    kart_half_width = 1.9
    kart_half_length = 2.5
    to_remove = None
    #  banana pill collisions
    for banana_pill_x, banana_pill_y in game_state.banana_pills:
        dist = math.sqrt((kart_x - banana_pill_x)**2 + (kart_y - banana_pill_y)**2)
        if dist < (banana_pill_rad + max(kart_half_width, kart_half_length)):
            to_remove = (banana_pill_x, banana_pill_y)
            break
    if to_remove:
        game_state.banana_pills.remove(to_remove)
        return True
    return False

def check_boundary_collision():
    current_time = time.time()
    if current_time - game_state.last_collision_time < 0.5:  # Boundary collision cooldown
        return False
    half_grid = grid_size / 2
    kart_half_width = 1.9
    kart_half_length = 2.5
    # grid boundaries hits or not
    if (abs(game_state.player_x) + kart_half_width >= half_grid or
        abs(game_state.player_y) + kart_half_length >= half_grid):
        game_state.health = max(0, game_state.health - health_decrement)
        game_state.last_collision_time = current_time
        if game_state.health <= 0:
            game_state.game_over = True
        return True
    return False

def reset_game():
    # player er shob reset
    game_state.player_x = track_innerx_radius + track_width / 2
    game_state.player_y = 0.0
    game_state.player_speed = 0.0
    game_state.player_angle = 0.0
    game_state.prev_angle = 0.0
    game_state.health = max_health
    # Reset camera
    game_state.cam_distance = cam_initial_dist
    game_state.cam_height = cam_initial_height
    game_state.cam_angle_offset = 0.0
    # Reset last valid position
    game_state.last_valid_x = game_state.player_x
    game_state.last_valid_y = game_state.player_y
    game_state.last_valid_angle = game_state.player_angle
    # Clear obstacles and power-ups
    game_state.cones = []
    game_state.potholes = []
    game_state.powerups = []
    game_state.powerdowns = []
    game_state.banana_pills = []
    # Reset game state flags
    game_state.game_over = False
    game_state.start_screen = True
    game_state.vehicle_type = None
    game_state.bike_lean_angle = 0.0
    game_state.start_time = None
    game_state.final_time = None
    game_state.first_person = False
    game_state.powerup_active = False
    game_state.powerup_timer = 0.0
    game_state.banana_pill_active = False
    game_state.banana_pill_timer = 0.0
    game_state.original_max_speed = max_speed
    # Repopulate cones
    angle_step = 2 * math.pi / cone_count
    for i in range(cone_count):
        angle = i * angle_step
        t = random.uniform(0, 1)
        x_radius = track_innerx_radius + t * (track_outer_x_radius - track_innerx_radius)
        y_radius = track_innery_radius + t * (track_outer_y_radius - track_innery_radius)
        x = x_radius * math.cos(angle)
        y = y_radius * math.sin(angle)
        start_x = track_innerx_radius + track_width / 2
        start_y = 0.0
        dist_to_start = math.sqrt((x - start_x)**2 + (y - start_y)**2)
        if abs(angle) > 0.1 and abs(angle - 2 * math.pi) > 0.1 and dist_to_start > min_obs_dist:
            game_state.cones.append((x, y))
    # Repopulate potholes
    for i in range(pothole_count):
        max_attempts = 100
        for _ in range(max_attempts):
            angle = random.uniform(0, 2 * math.pi)
            t = random.uniform(0, 1)
            x_radius = track_innerx_radius + t * (track_outer_x_radius - track_innerx_radius)
            y_radius = track_innery_radius + t * (track_outer_y_radius - track_innery_radius)
            x = x_radius * math.cos(angle)
            y = y_radius * math.sin(angle)
            start_x = track_innerx_radius + track_width / 2
            start_y = 0.0
            dist_to_start = math.sqrt((x - start_x)**2 + (y - start_y)**2)
            if abs(angle) > 0.1 and abs(angle - 2 * math.pi) > 0.1 and dist_to_start > min_obs_dist:
                valid = True
                for cx, cy in game_state.cones:
                    dist = math.sqrt((x - cx)**2 + (y - cy)**2)
                    if dist < min_obs_dist:
                        valid = False
                        break
                for px, py in game_state.potholes:
                    dist = math.sqrt((x - px)**2 + (y - py)**2)
                    if dist < min_obs_dist:
                        valid = False
                        break
                if valid:
                    game_state.potholes.append((x, y))
                    break
    # Repopulate power-ups
    for i in range(powerup_count):
        max_attempts = 100
        for _ in range(max_attempts):
            angle = random.uniform(0, 2 * math.pi)
            t = random.uniform(0, 1)
            x_radius = track_innerx_radius + t * (track_outer_x_radius - track_innerx_radius)
            y_radius = track_innery_radius + t * (track_outer_y_radius - track_innery_radius)
            x = x_radius * math.cos(angle)
            y = y_radius * math.sin(angle)
            start_x = track_innerx_radius + track_width / 2
            start_y = 0.0
            dist_to_start = math.sqrt((x - start_x)**2 + (y - start_y)**2)
            if abs(angle) > 0.1 and abs(angle - 2 * math.pi) > 0.1 and dist_to_start > min_obs_dist:
                valid = True
                for cx, cy in game_state.cones:
                    dist = math.sqrt((x - cx)**2 + (y - cy)**2)
                    if dist < min_obs_dist:
                        valid = False
                        break
                for px, py in game_state.potholes:
                    dist = math.sqrt((x - px)**2 + (y - py)**2)
                    if dist < min_obs_dist:
                        valid = False
                        break
                for ppx, ppy in game_state.powerups:
                    dist = math.sqrt((x - ppx)**2 + (y - ppy)**2)
                    if dist < min_obs_dist:
                        valid = False
                        break
                if valid:
                    game_state.powerups.append((x, y))
                    break
    # Repopulate power-downs
    for i in range(powerdown_count):
        max_attempts = 100
        for _ in range(max_attempts):
            angle = random.uniform(0, 2 * math.pi)
            t = random.uniform(0, 1)
            x_radius = track_innerx_radius + t * (track_outer_x_radius - track_innerx_radius)
            y_radius = track_innery_radius + t * (track_outer_y_radius - track_innery_radius)
            x = x_radius * math.cos(angle)
            y = y_radius * math.sin(angle)
            start_x = track_innerx_radius + track_width / 2
            start_y = 0.0
            dist_to_start = math.sqrt((x - start_x)**2 + (y - start_y)**2)
            if abs(angle) > 0.1 and abs(angle - 2 * math.pi) > 0.1 and dist_to_start > min_obs_dist:
                valid = True
                for cx, cy in game_state.cones:
                    dist = math.sqrt((x - cx)**2 + (y - cy)**2)
                    if dist < min_obs_dist:
                        valid = False
                        break
                for px, py in game_state.potholes:
                    dist = math.sqrt((x - px)**2 + (y - py)**2)
                    if dist < min_obs_dist:
                        valid = False
                        break
                for ppx, ppy in game_state.powerups:
                    dist = math.sqrt((x - ppx)**2 + (y - ppy)**2)
                    if dist < min_obs_dist:
                        valid = False
                        break
                for pdx, pdy in game_state.powerdowns:
                    dist = math.sqrt((x - pdx)**2 + (y - pdy)**2)
                    if dist < min_obs_dist:
                        valid = False
                        break
                if valid:
                    game_state.powerdowns.append((x, y))
                    break
    # Repopulate banana pills
    for i in range(banana_pill_count):
        max_attempts = 100
        for _ in range(max_attempts):
            angle = random.uniform(0, 2 * math.pi)
            t = random.uniform(0, 1)
            x_radius = track_innerx_radius + t * (track_outer_x_radius - track_innerx_radius)
            y_radius = track_innery_radius + t * (track_outer_y_radius - track_innery_radius)
            x = x_radius * math.cos(angle)
            y = y_radius * math.sin(angle)
            start_x = track_innerx_radius + track_width / 2
            start_y = 0.0
            dist_to_start = math.sqrt((x - start_x)**2 + (y - start_y)**2)
            if abs(angle) > 0.1 and abs(angle - 2 * math.pi) > 0.1 and dist_to_start > min_obs_dist:
                valid = True
                for cx, cy in game_state.cones:
                    dist = math.sqrt((x - cx)**2 + (y - cy)**2)
                    if dist < min_obs_dist:
                        valid = False
                        break
                for px, py in game_state.potholes:
                    dist = math.sqrt((x - px)**2 + (y - py)**2)
                    if dist < min_obs_dist:
                        valid = False
                        break
                for ppx, ppy in game_state.powerups:
                    dist = math.sqrt((x - ppx)**2 + (y - ppy)**2)
                    if dist < min_obs_dist:
                        valid = False
                        break
                for pdx, pdy in game_state.powerdowns:
                    dist = math.sqrt((x - pdx)**2 + (y - pdy)**2)
                    if dist < min_obs_dist:
                        valid = False
                        break
                for bpx, bpy in game_state.banana_pills:
                    dist = math.sqrt((x - bpx)**2 + (y - bpy)**2)
                    if dist < min_obs_dist:
                        valid = False
                        break
                if valid:
                    game_state.banana_pills.append((x, y))
                    break
    
    game_state.respawn_timer = 0.0
    game_state.flicker_count = 0
    game_state.laps_completed = 0
    game_state.crossed_start_line = False
    game_state.last_collision_time = 0.0

def specialKeyListener(key, x, y):
    if not game_state.game_over and not game_state.start_screen:
        if key == GLUT_KEY_UP:
            # Zoom in
            game_state.cam_distance = max(cam_min_dist, game_state.cam_distance - cam_dist_step)
            t = (game_state.cam_distance - cam_min_dist) / (cam_max_dist - cam_min_dist)
            game_state.cam_height = cam_min_height + t * (cam_max_height - cam_min_height)
        elif key == GLUT_KEY_DOWN:
            # Zoom  out
            game_state.cam_distance = min(cam_max_dist, game_state.cam_distance + cam_dist_step)
            t = (game_state.cam_distance - cam_min_dist) / (cam_max_dist - cam_min_dist)
            game_state.cam_height = cam_min_height + t * (cam_max_height - cam_min_height)
        elif key == GLUT_KEY_LEFT:
            game_state.cam_angle_offset += cam_angle_step  # Rotate camera left
        elif key == GLUT_KEY_RIGHT:
            game_state.cam_angle_offset -= cam_angle_step  # Rotate camera right
        glutPostRedisplay()  


def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    if game_state.start_screen:
        draw_start_screen()
    else:
        setup_camera()

        draw_grid()
        draw_oval_track()
        draw_potholes()
        draw_cones()
        draw_powerups()
        draw_powerdowns()
        draw_banana_pills()
        if not game_state.game_over:
            draw_vehicle()
        draw_hud()
    glutSwapBuffers()


def timer(value):
    update()
    glutTimerFunc(16, timer, 0)


def keyboard(key, x, y):
    if game_state.start_screen:
        if key == b'b':
            game_state.vehicle_type = 'bike'
            game_state.start_screen = False
            game_state.cam_angle_offset = 90.0
            
        elif key == b'c':
            game_state.vehicle_type = 'car'
            game_state.start_screen = False
            game_state.cam_angle_offset = 90.0
            
        glutPostRedisplay()
        return
    game_state.keys_pressed.add(key)
    if key == b'\x1b':
                glutLeaveMainLoop()
    if key == b'r':
        
        reset_game()
    if key == b'f' and not game_state.game_over:
        game_state.first_person = not game_state.first_person
        
    if not game_state.game_over:
        glutPostRedisplay()

def keyboard_up(key, x, y):
    if key in game_state.keys_pressed:
        game_state.keys_pressed.remove(key)
    if not game_state.game_over and not game_state.start_screen:
        glutPostRedisplay()
    


def update():
    if game_state.start_screen:
        glutPostRedisplay()
        return
    current_time = time.time()
    dt = current_time - game_state.last_time
    game_state.last_time = current_time
    if game_state.game_over:
        if game_state.final_time is None:
            game_state.final_time = max(0, total_time - (current_time - game_state.start_time))
        glutPostRedisplay()
        return
    if game_state.start_time is None:
        game_state.start_time = current_time
    time_elapsed = current_time - game_state.start_time
    if time_elapsed >= total_time and game_state.laps_completed < req_laps:
        game_state.game_over = True
        game_state.final_time = 0
        glutPostRedisplay()
        return
    if game_state.laps_completed >= req_laps:
        game_state.game_over = True
        game_state.final_time = max(0, total_time - time_elapsed)
        glutPostRedisplay()
        return
    if game_state.powerup_active:
        game_state.powerup_timer += dt
        if game_state.powerup_timer >= powerup_duration:
            game_state.powerup_active = False
            game_state.powerup_timer = 0.0
            game_state.original_max_speed = max_speed
            if game_state.player_speed > game_state.original_max_speed:
                game_state.player_speed = game_state.original_max_speed
            elif game_state.player_speed < -game_state.original_max_speed / 2:
                game_state.player_speed = -game_state.original_max_speed / 2
    if game_state.banana_pill_active:
        game_state.banana_pill_timer += dt
        if game_state.banana_pill_timer >= banana_pill_duration:
            game_state.banana_pill_active = False
            game_state.banana_pill_timer = 0.0
    on_track = is_on_track(game_state.player_x, game_state.player_y)
    if on_track:
        game_state.last_valid_x = game_state.player_x
        game_state.last_valid_y = game_state.player_y
        game_state.last_valid_angle = game_state.player_angle
    if on_track:
        track_angle = math.atan2(game_state.player_y, game_state.player_x)
        if track_angle < 0:
            track_angle += 2 * math.pi
        if game_state.prev_angle < 0:
            game_state.prev_angle += 2 * math.pi
        finish_line_angle = 0
        angle_tolerance = math.radians(10)
        if abs(track_angle) < angle_tolerance or abs(track_angle - 2 * math.pi) < angle_tolerance:
            if game_state.prev_angle > math.pi and track_angle < math.pi:
                game_state.laps_completed += 1
                print(f"Lap completed: {game_state.laps_completed}")
        game_state.prev_angle = track_angle
    current_max_speed = (game_state.original_max_speed * slow_factor if not on_track else game_state.original_max_speed)
    if game_state.vehicle_type == 'bike':
        current_acceleration = bike_acceleration * slow_factor if not on_track else bike_acceleration
        current_friction = bike_friction * slow_factor if not on_track else bike_friction
        current_turn_speed = bike_turn_speed * slow_factor if not on_track else bike_turn_speed
    else:
        current_acceleration = acceleration * slow_factor if not on_track else acceleration
        current_friction = friction * slow_factor if not on_track else friction
        current_turn_speed = turn_speed * slow_factor if not on_track else turn_speed
    if game_state.respawn_timer > 0:
        game_state.respawn_timer -= dt
        if game_state.respawn_timer <= 0:
            game_state.flicker_count = 0
            game_state.bike_lean_angle = 0.0
        else:
            if game_state.flicker_count < flicker_count:
                if dt >= 0.5:
                    game_state.flicker_state = not game_state.flicker_state
                    game_state.flicker_count += 1
                    game_state.last_time = current_time
        if game_state.respawn_timer > 0:
            game_state.player_speed = 0
            return
    if b'w' in game_state.keys_pressed:
        if game_state.banana_pill_active:
            game_state.player_speed -= current_acceleration * dt * 60  # Reversed: 'w' moves backward
        else:
            game_state.player_speed += current_acceleration * dt * 60  # Normal: 'w' moves forward
    elif b's' in game_state.keys_pressed:
        if game_state.banana_pill_active:
            game_state.player_speed += current_acceleration * dt * 60  # Reversed: 's' moves forward
        else:
            game_state.player_speed -= current_acceleration * dt * 60  # Normal: 's' moves backward
    else:
        if game_state.player_speed > 0:
            game_state.player_speed = max(0, game_state.player_speed - current_friction * dt * 60)
        else:
            game_state.player_speed = min(0, game_state.player_speed + current_friction * dt * 60)
    game_state.player_speed = max(-current_max_speed/2, min(current_max_speed, game_state.player_speed))
    movement_angle = game_state.player_angle + 90
    if game_state.vehicle_type == 'bike':
        if abs(game_state.player_speed) > 0.01:
            speed_factor = abs(game_state.player_speed) / game_state.original_max_speed
            target_lean = 0.0
            lean_rate = current_turn_speed * 2.0
            if b'a' in game_state.keys_pressed:
                if game_state.banana_pill_active:
                    game_state.player_angle -= current_turn_speed * dt * 60  # Reversed: 'a' turns right
                    target_lean = -bike_max_lean * speed_factor  # Reversed: lean right
                else:
                    game_state.player_angle += current_turn_speed * dt * 60  # Normal: 'a' turns left
                    target_lean = bike_max_lean * speed_factor  # Normal: lean left
            elif b'd' in game_state.keys_pressed:
                if game_state.banana_pill_active:
                    game_state.player_angle += current_turn_speed * dt * 60  # Reversed: 'd' turns left
                    target_lean = bike_max_lean * speed_factor  # Reversed: lean left
                else:
                    game_state.player_angle -= current_turn_speed * dt * 60  # Normal: 'd' turns right
                    target_lean = -bike_max_lean * speed_factor  # Normal: lean right
            lean_diff = target_lean - game_state.bike_lean_angle
            game_state.bike_lean_angle += lean_diff * min(1.0, lean_rate * dt * 60)
            game_state.bike_lean_angle = max(-bike_max_lean, min(bike_max_lean, game_state.bike_lean_angle))
        else:
            game_state.bike_lean_angle = 0.0
    else:
        if abs(game_state.player_speed) > 0.01:
            turn_factor = 1.0 if game_state.player_speed > 0 else -1.0
            if b'a' in game_state.keys_pressed:
                if game_state.banana_pill_active:
                    game_state.player_angle -= current_turn_speed * turn_factor * dt * 60  # Reversed: 'a' turns right
                else:
                    game_state.player_angle += current_turn_speed * turn_factor * dt * 60  # Normal: 'a' turns left
            if b'd' in game_state.keys_pressed:
                if game_state.banana_pill_active:
                    game_state.player_angle += current_turn_speed * turn_factor * dt * 60  # Reversed: 'd' turns left
                else:
                    game_state.player_angle -= current_turn_speed * turn_factor * dt * 60  # Normal: 'd' turns right
    angle_rad = math.radians(movement_angle)
    new_x = game_state.player_x + game_state.player_speed * math.cos(angle_rad) * dt * 60
    new_y = game_state.player_y + game_state.player_speed * math.sin(angle_rad) * dt * 60
    half_grid = grid_size / 2
    if is_in_water(new_x, new_y):
        game_state.health = 0
        game_state.game_over = True
        game_state.player_speed = 0.0
        game_state.bike_lean_angle = 0.0
        game_state.final_time = max(0, total_time - (current_time - game_state.start_time))
    elif new_x < -half_grid or new_x > half_grid or new_y < -half_grid or new_y > half_grid:
        game_state.player_speed = 0.0
        game_state.bike_lean_angle = 0.0
        if check_boundary_collision():
            game_state.player_x = game_state.last_valid_x
            game_state.player_y = game_state.last_valid_y
            game_state.player_angle = game_state.last_valid_angle
            game_state.respawn_timer = respawn_display
            game_state.flicker_state = True
            game_state.flicker_count = 0
            game_state.bike_lean_angle = 0.0
    elif check_collision(new_x, new_y) and not check_collision(game_state.player_x, game_state.player_y):
        game_state.player_speed = 0.0
        game_state.bike_lean_angle = 0.0
        game_state.health = max(0, game_state.health - health_decrement)
        game_state.last_collision_time = time.time()
        if game_state.health <= 0:
            game_state.game_over = True
            game_state.final_time = max(0, total_time - (current_time - game_state.start_time))
    elif check_powerup_collision(new_x, new_y):
        game_state.powerup_active = True
        game_state.powerup_timer = 0.0
        game_state.original_max_speed = max_speed * powerup_speed_multiplier
        game_state.player_speed *= powerup_speed_multiplier
    elif check_powerdown_collision(new_x, new_y):
        if game_state.start_time:
            game_state.start_time -= powerdown_time_reduce
            if total_time - (current_time - game_state.start_time) <= 0:
                game_state.game_over = True
                game_state.final_time = 0
    elif check_banana_pill_collision(new_x, new_y):
        game_state.banana_pill_active = True
        game_state.banana_pill_timer = 0.0
    else:
        game_state.player_x = new_x
        game_state.player_y = new_y
        if is_on_track(game_state.player_x, game_state.player_y):
            game_state.last_valid_x = game_state.player_x
            game_state.last_valid_y = game_state.player_y
            game_state.last_valid_angle = game_state.player_angle
    glutPostRedisplay()
 


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(window_width, window_height)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"FORMULA 423")
    init()
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)
    glutKeyboardUpFunc(keyboard_up)
    glutSpecialFunc(specialKeyListener)
    glutTimerFunc(0, timer, 0)
    glutMainLoop()

if __name__ == "__main__":
    
    main()