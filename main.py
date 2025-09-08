from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

import time
import random
import math

game_over = False 
is_fpp_mode = False
fpp_head_bob = 0.0
fovY = 120  
GRID_LENGTH = 600  
rand_var = 423
road_scroll = 0.0
LANE_X = [-300.0, 0.0, 300.0]
NUM_LANES = len(LANE_X)

player = {
    "lane": 1,           
    "x": LANE_X[1],
    "y": 2000,          
    "z": 40.0,         
    "width": 50.0,
    "height": 50.0
}

enemy_is_jumping = False
enemy_jump_velocity = 0.0
enemy_is_sliding = False
enemy_slide_timer = 0.0
enemy_decision_cooldown = 0.0
enemy_active = False
enemy_timer = 0.0
ENEMY_DURATION = 10.0

enemy = {
    "x": 0.0,
    "y": 0.0,
    "z": 40.0
}


camera_pos = (0, player["y"] + 400, 500)

obstacles = []


forward_speed = 400.0    
distance_traveled = 0.0
score = 0
lives = 3


spawn_interval = 0.9   
last_spawn_time = 0.0


last_time = time.time()

is_jumping = False
jump_velocity = 0.0
GRAVITY = -1000.0   
JUMP_SPEED = 500.0  
GROUND_Z = 40.0     


is_sliding = False
slide_duration = 0.5   
slide_timer = 0.0
SLIDE_HEIGHT = 25.0    
NORMAL_HEIGHT = 50.0
SLIDE_Z = -25.0      
   


is_hoverboard = False
hoverboard_height = 80.0  
hoverboard_tilt = 0.0     
hoverboard_bob = 0.0      
HOVERBOARD_BOB_SPEED = 4.0
HOVERBOARD_TILT_SPEED = 3.0
hoverboard_fast_mode = False  
 


SPAWN_Y = player["y"] - 1800   
DESPAWN_Y =player["y"] + 1000  


COLLIDE_Y_THRESHOLD = 30.0
COLLIDE_X_THRESHOLD = 40.0

combo_flag = 0
combo_start_time = 0.0 
COMBO_WINDOW_S = 3

two_x_flag = False
two_x_time = 0.0
MULTIPLIER_DURATION_S = 10.0
combo_multi = 5





def draw_text_line(x, y, s, font=GLUT_BITMAP_HELVETICA_18):
    """Draw one text line (assumes caller already set orthographic projection/modelview identity)."""
    glRasterPos2f(x, y)
    for ch in s:
        glutBitmapCharacter(font, ord(ch))

def draw_obstacle(obs):
    """Draw a goal-post style obstacle sized just smaller than lane width."""
    glPushMatrix()
    glTranslatef(obs["x"], obs["y"], obs["z"])
    glColor3f(1.0, 0.98, 0.80) 

    pillar_height = 120
    pillar_thickness = 12

    
    lane_width = LANE_X[1] - LANE_X[0]
    gap_width = lane_width * 0.8   

    
    glPushMatrix()
    glTranslatef(-gap_width/2, 0, pillar_height/2)
    glScalef(pillar_thickness, pillar_thickness, pillar_height)
    glutSolidCube(1)
    glPopMatrix()

    
    glPushMatrix()
    glTranslatef(gap_width/2, 0, pillar_height/2)
    glScalef(pillar_thickness, pillar_thickness, pillar_height)
    glutSolidCube(1)
    glPopMatrix()

    
    glPushMatrix()
    glTranslatef(0, 0, pillar_height)
    glScalef(gap_width + pillar_thickness, pillar_thickness, pillar_thickness)
    glutSolidCube(1)
    glPopMatrix()

    glPopMatrix()



def draw_dashed_line(x, y_start, y_end, width=4, dash_length=150, gap=120, color=(1,1,1), vertical=True, offset=0):
    glColor3f(*color)
    total_length = dash_length + gap

    
    phase = offset % total_length

    
    pos = y_start - (y_start % total_length) - total_length

    while pos < y_end + total_length:
        glBegin(GL_QUADS)
        if vertical:
            glVertex3f(x - width, pos + phase, 2)
            glVertex3f(x + width, pos + phase, 2)
            glVertex3f(x + width, pos + phase + dash_length, 2)
            glVertex3f(x - width, pos + phase + dash_length, 2)
        else:
            glVertex3f(pos + phase, x - width, 2)
            glVertex3f(pos + phase + dash_length, x - width, 2)
            glVertex3f(pos + phase + dash_length, x + width, 2)
            glVertex3f(pos + phase, x + width, 2)
        glEnd()
        pos += total_length



def draw_road():
    lane_width = 300
    total_width = lane_width * 3
    segment_length = 20000

    back_distance = 3000
    front_distance = 4500

    
    camera_y = camera_pos[1]  
    y_start = camera_y - back_distance  
    y_end   = camera_y + front_distance  

    
    offset = -(road_scroll % segment_length)
    y = y_start + offset
    glColor3f(0.13, 0.14, 0.16)  
    while y < y_end:
        glBegin(GL_QUADS)
        glVertex3f(-total_width/2, y, 1)
        glVertex3f(total_width/2, y, 1)
        glVertex3f(total_width/2, y + segment_length, 1)
        glVertex3f(-total_width/2, y + segment_length, 1)
        glEnd()
        y += segment_length

    
    dividers = [-lane_width/2, lane_width/2]
    for lane_divider in dividers:
        draw_dashed_line(lane_divider, y_start, y_end,
                         width=4, dash_length=150, gap=120,
                         color=(1,1,0), offset=road_scroll)

    edge_positions = [-total_width/2, total_width/2]
    for edge_x in edge_positions:
        draw_dashed_line(edge_x, y_start, y_end,
                         width=3, dash_length=150, gap=120,
                         color=(1,1,1), offset=road_scroll)


coin_rotation_angle = 0.0

import math

def draw_coin(c):
    """Draw a spinning coin perpendicular to the road using only GL_QUADS and GL_TRIANGLES."""
    global coin_rotation_angle

    x, y, z = c["x"], c["y"], c["z"]
    radius = c["size"] / 2
    height = c["size"] / 5  
    sides = 32  

    glPushMatrix()
    glTranslatef(x, y, z + height+10)
    glRotatef(90, 1, 0, 0)  
    glRotatef(coin_rotation_angle, 0, 1, 0)  

    glColor3f(1.0, 0.68, 0.0)  

    
    glBegin(GL_QUADS)
    for i in range(sides):
        theta1 = (2 * math.pi * i) / sides
        theta2 = (2 * math.pi * (i + 1)) / sides
        x1, y1 = radius * math.cos(theta1), radius * math.sin(theta1)
        x2, y2 = radius * math.cos(theta2), radius * math.sin(theta2)
        glVertex3f(x1, y1, -height/2)
        glVertex3f(x2, y2, -height/2)
        glVertex3f(x2, y2, height/2)
        glVertex3f(x1, y1, height/2)
    glEnd()

    
    for i in range(sides):
        theta1 = (2 * math.pi * i) / sides
        theta2 = (2 * math.pi * (i + 1)) / sides
        x1, y1 = radius * math.cos(theta1), radius * math.sin(theta1)
        x2, y2 = radius * math.cos(theta2), radius * math.sin(theta2)
        glBegin(GL_TRIANGLES)
        glVertex3f(0, 0, height/2)  
        glVertex3f(x1, y1, height/2)
        glVertex3f(x2, y2, height/2)
        glEnd()

    
    for i in range(sides):
        theta1 = (2 * math.pi * i) / sides
        theta2 = (2 * math.pi * (i + 1)) / sides
        x1, y1 = radius * math.cos(theta1), radius * math.sin(theta1)
        x2, y2 = radius * math.cos(theta2), radius * math.sin(theta2)
        glBegin(GL_TRIANGLES)
        glVertex3f(0, 0, -height/2)  
        glVertex3f(x2, y2, -height/2)
        glVertex3f(x1, y1, -height/2)
        glEnd()

    glPopMatrix()








def spawn_obstacle():
    """Spawn a single goal-post obstacle in a random lane in front of player."""
    lane = random.randint(0, NUM_LANES-1)
    obs = {
        "lane": lane,
        "x": LANE_X[lane],
        "y": SPAWN_Y - random.uniform(0.0, 300.0),
        "z": 1.0,   
        "size": 1.0 
    }
    obstacles.append(obs)

coins = []   
coin_count = 0  

COIN_SIZE = 70.0
COIN_Y_OFFSET = 1500  

def spawn_coin():
    """Spawn a coin randomly in one lane in front of the player"""
    lane = random.randint(0, NUM_LANES - 1)
    coin = {
        "lane": lane,
        "x": LANE_X[lane],
        "y": SPAWN_Y - random.uniform(0.0, 300.0),
        "z": 20.0,   
        "size": COIN_SIZE
    }
    coins.append(coin)

magnets = []   
MAGNET_SIZE = 80.0

magnets_collected = 0
magnet_spin_angle = 0.0

magnet_active = False
magnet_timer = 0.0
MAGNET_DURATION = 5.0   
MAGNET_RANGE = 800.0    


def spawn_magnet():
    """Spawn a magnet randomly in one lane, ensuring it does not overlap coins."""
    lane = random.randint(0, NUM_LANES - 1)
    y_pos = SPAWN_Y - random.uniform(0.0, 300.0)
    
    can_spawn = True
    
    for c in coins:
        if c["lane"] == lane and abs(c["y"] - y_pos) < 150:  
            can_spawn = False 
            break
    
    if can_spawn:
        magnet = {
            "lane": lane,
            "x": LANE_X[lane],
            "y": y_pos,
            "z": 50,
            "collision_z": -15.0,
            "size": MAGNET_SIZE
        }
        magnets.append(magnet)
        print("Spawned magnet at lane", lane, "y:", y_pos)


def draw_magnet(m):
    """Draw a horseshoe magnet."""
    global magnet_spin_angle
    x, y, z, size = m["x"], m["y"], m["z"], m["size"]
    
    glPushMatrix()
    glTranslatef(x, y, z+size/2)

    arm_height = size
    
    glTranslatef(0, 0, -arm_height / 2)
    
    glRotatef(-30, 0, 1, 0) 
    
    glRotatef(magnet_spin_angle, 1, 0, 1)
    
    
    arm_width = size * 0.25
    gap = size * 0.5

    arm_width = size * 0.25
    gap = size * 0.5

    
    glPushMatrix()
    glTranslatef(-gap/2, 0, 0)
    glScalef(arm_width, 20, arm_height)
    glColor3f(1.0, 0.0, 0.0)  
    glutSolidCube(1)
    glPopMatrix()

    
    glPushMatrix()
    glTranslatef(gap/2, 0, 0)
    glScalef(arm_width, 20, arm_height)
    glColor3f(1.0, 0.0, 0.0)  
    glutSolidCube(1)
    glPopMatrix()

    
    glPushMatrix()
    glTranslatef(0, 0, -arm_height/2)
    glScalef(gap + arm_width, 20, arm_width)
    glColor3f(0.204, 0.659, 0.922)
    glutSolidCube(1)
    glPopMatrix()

    
    for side in [-1, 1]:
        glPushMatrix()
        glTranslatef(side * gap/2, 0, -arm_height/2 + 5)
        glScalef(arm_width, 20, arm_width)
        glColor3f(0.204, 0.659, 0.922)
        glutSolidCube(1)
        glPopMatrix()

    glPopMatrix()





def keyboardListener(key, x, y):
    global player, obstacles, distance_traveled, score, lives, forward_speed,road_scroll,camera_pos,coin_count
    global is_jumping, jump_velocity, is_sliding, slide_timer, slide_duration
    global is_fpp_mode, is_hoverboard, hoverboard_height,hoverboard_fast_mode,enemy_active
    global enemy_timer, enemy_is_jumping, enemy_jump_velocity, enemy_is_sliding, enemy_slide_timer, enemy_decision_cooldown, enemy
    global magnet_spin_angle, magnets_collected, magnet_active, magnet_timer
    global hoverboard_tilt, hoverboard_bob, hoverboard_fast_mode,last_spawn_time,game_over
    global combo_flag, combo_start_time, two_x_flag, two_x_time, COMBO_WINDOW_S, MULTIPLIER_DURATION_S


    if key in [b'a', b'A',b'd', b'D']:
        if combo_flag != 1:
            combo_flag = 0
            combo_start_time = 0.0
    elif key in [b's', b'S']:
        if combo_flag != 2:
            combo_flag = 0
            combo_start_time = 0.0
    else:
        combo_flag = 0
        combo_start_time = 0.0

    if key in [b'a', b'A']:
        a = time.time()
        if player["lane"] < NUM_LANES - 1:
            player["lane"] += 1
            player["x"] = LANE_X[player["lane"]]

            if combo_flag == 1 and combo_start_time != 0.0 and (a - combo_start_time) <= COMBO_WINDOW_S:
                combo_flag = 2
                
                print("2. pressed lane switch")
            else:
                combo_flag = 0
                combo_start_time = 0.0


    elif key in [b'd', b'D']:
        a = time.time()
        if player["lane"] > 0:
            player["lane"] -= 1
            player["x"] = LANE_X[player["lane"]]

            if (combo_flag == 1) and (combo_start_time != 0.0) and ((a - combo_start_time) <= COMBO_WINDOW_S):
                combo_flag = 2
                print("2. pressed lane switch")
            else:
                combo_flag = 0
                combo_start_time = 0.0


    elif key in [b' ', b'SPACE']:
        if is_hoverboard:
            
            hoverboard_fast_mode = not hoverboard_fast_mode
            print(f"Hoverboard Fast Mode: {'ON' if hoverboard_fast_mode else 'OFF'}")

            combo_start_time = time.time()
            combo_flag = 1    
            print("1. pressed space")


        elif not is_jumping:
            is_jumping = True
            jump_velocity = JUMP_SPEED

            combo_start_time = time.time()
            combo_flag = 1    
            print("1. pressed space")
    
    elif key in [b's', b'S']:
        a = time.time()
        if is_hoverboard:
            
            if not is_sliding:
                is_sliding = True
                slide_timer = slide_duration
                player["height"] = SLIDE_HEIGHT
                player["z"] = SLIDE_Z
                if combo_flag == 2 and combo_start_time != 0.0:
                    print(a - combo_start_time)
                    if a - combo_start_time <= COMBO_WINDOW_S:
                        
                        two_x_flag = True
                        two_x_time = time.time()
                        combo_flag = 0
                        combo_start_time = 0.0
                        
                        print("3. pressed slide")
                    else:
                        combo_flag = 0
                        combo_start_time = 0.0

                
        elif not is_sliding and not is_jumping:
            is_sliding = True
            slide_timer = slide_duration
            player["height"] = SLIDE_HEIGHT
            player["z"] = SLIDE_Z

            if combo_flag == 2 and combo_start_time != 0.0:
                print("here")
                print(a - combo_start_time)
                if a - combo_start_time <= COMBO_WINDOW_S:
                        
                    two_x_flag = True
                    two_x_time = time.time()
                    combo_flag = 0
                    combo_start_time = 0.0
                        
                    print("3. pressed slide")
                else:
                    combo_flag = 0
                    combo_start_time = 0.0    
    
    
    elif key in [b'f', b'F']:
        is_fpp_mode = not is_fpp_mode
        print(f"FPP Mode: {'ON' if is_fpp_mode else 'OFF'}")
    
    
    elif key in [b'c', b'C']:
        is_hoverboard = not is_hoverboard
        if is_hoverboard:
            
            is_jumping = False
            is_sliding = False
            jump_velocity = 0.0
            slide_timer = 0.0
            player["z"] = GROUND_Z + hoverboard_height
            player["height"] = NORMAL_HEIGHT
        else:
            
            player["z"] = GROUND_Z
        print(f"Hoverboard Mode: {'ON' if is_hoverboard else 'OFF'}")

    elif key in [b'r', b'R']:
        
        obstacles.clear()
        coins.clear()
        magnets.clear()
        
        
        distance_traveled = 0.0
        score = 0
        lives = 3
        forward_speed = 400.0
        road_scroll = 0.0
        game_over=False
        
        
        player["lane"] = 1
        player["x"] = LANE_X[1]
        player["y"] = 2000
        player["z"] = GROUND_Z
        player["height"] = NORMAL_HEIGHT
        
        
        is_jumping = False
        jump_velocity = 0.0
        is_sliding = False
        slide_timer = 0.0
        
        
        is_fpp_mode = False
        is_hoverboard = False
        hoverboard_fast_mode = False
        
        
        hoverboard_tilt = 0.0
        hoverboard_bob = 0.0
        
        
        coin_count = 0
        magnets_collected = 0
        
        
        magnet_active = False
        magnet_timer = 0.0
        magnet_spin_angle = 0.0
        
        
        enemy_active = False
        enemy_timer = 0.0
        enemy_is_jumping = False
        enemy_is_sliding = False
        enemy_jump_velocity = 0.0
        enemy_slide_timer = 0.0
        enemy_decision_cooldown = 0.0
        enemy["x"] = 0.0
        enemy["y"] = 0.0
        enemy["z"] = 40.0
        
        
        camera_pos = (0, player["y"] + 400, 500)
        
        
        last_spawn_time = time.time() - 1.0  
        
        
        enemy_active = False
        enemy_timer = 0.0
        enemy["x"] = -1000  
        enemy["y"] = -1000
        enemy["z"] = 40.0
        
        print("Game Restarted!") 
    

def specialKeyListener(key, x, y):
    """
    Handles special key inputs (arrow keys) for adjusting the camera angle and height.
    """
    global camera_pos
    x_cam, y_cam, z_cam = camera_pos

    if key == GLUT_KEY_LEFT:
        x_cam -= 10.0
    elif key == GLUT_KEY_RIGHT:
        x_cam += 10.0
    elif key == GLUT_KEY_UP:
        y_cam += 10.0
    elif key == GLUT_KEY_DOWN:
        y_cam -= 10.0

    camera_pos = (x_cam, y_cam, z_cam)

def mouseListener(button, state, x, y):
    """Reserved for future features."""
    pass

def setupCamera():
    """
    Configures the camera's projection and view settings.
    Supports both third-person and first-person modes.
    """
    global fpp_head_bob
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY if not is_fpp_mode else 90, 1.25, 0.1, 4000)  
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if is_fpp_mode:
        
        
        t = time.time()
        if not is_jumping and not is_sliding and not is_hoverboard:
            fpp_head_bob = math.sin(t * 8) * 3  
        elif is_hoverboard:
            fpp_head_bob = math.sin(t * 4) * 2  
        else:
            fpp_head_bob = 0
        
        
        eye_height = 70  
        if is_sliding:
            eye_height = 20  
        elif is_hoverboard:
            eye_height = 80  
        
        camera_x = player["x"]
        camera_y = player["y"]+30 
        camera_z = player["z"] + 32 + eye_height + fpp_head_bob
        
        
        look_x = player["x"]
        look_y = player["y"] - 100  
        look_z = player["z"] + eye_height
        
        gluLookAt(camera_x, camera_y, camera_z,    
                  look_x, look_y, look_z,          
                  0, 0, 1)                         
    else:
        
        x, y, z = camera_pos
        gluLookAt(x, y, z,                          
                  0, 0, player["z"],                
                  0, 0, 1)



def idle():
    """
    Idle function that runs continuously:
    - update game state based on elapsed time
    - trigger screen redraw for real-time updates
    """
    global last_time
    now = time.time()
    dt = now - last_time
    if dt > 0.1:
        dt = 0.1

    update_game(dt)
    last_time = now

    glutPostRedisplay()


def draw_lamp_head():
    
    glColor3f(1.0, 0.5, 0.0)   
    glutSolidSphere(12, 16, 16)

    
    glTranslatef(0, 0, 10)
    glColor3f(1.0, 1.0, 0.0)   
    glutSolidSphere(8, 16, 16)

    
    glTranslatef(0, 0, 10)
    glColor3f(1.0, 0.2, 0.0)   
    gluCylinder(gluNewQuadric(), 5, 0, 15, 10, 10)

def draw_lamp_posts():
    pole_height = 250
    gap = 400
    back_distance = 3000
    front_distance = 5000

    
    camera_y = camera_pos[1]
    y_start = camera_y - back_distance
    y_end   = camera_y + front_distance

    

    
    scroll_offset = road_scroll % gap

    
    
    start_y = y_start - (y_start % gap) - gap 

    
    current_y = start_y
    while current_y < y_end:
        
        y_pos = current_y + scroll_offset

        
        glPushMatrix()
        glTranslatef(-470, y_pos, 0)
        glColor3f(0.55, 0.27, 0.07)
        gluCylinder(gluNewQuadric(), 5, 5, pole_height, 10, 10)
        glTranslatef(0, 0, pole_height)
        draw_lamp_head()
        glPopMatrix()

        
        glPushMatrix()
        glTranslatef(470, y_pos, 0)
        glColor3f(0.55, 0.27, 0.07)
        gluCylinder(gluNewQuadric(), 5, 5, pole_height, 10, 10)
        glTranslatef(0, 0, pole_height)
        draw_lamp_head()
        glPopMatrix()

        
        current_y += gap






def draw_hoverboard():
    """Draw a futuristic hoverboard with glowing effects, tilting animation, and rotating wheels."""
    global hoverboard_tilt, hoverboard_bob, forward_speed, hoverboard_fast_mode
    
    glPushMatrix()
    
    
    board_length = 120
    board_width = 40
    board_thickness = 8
    
    
    tilt_angle = math.sin(hoverboard_tilt * math.pi / 180) * 5  
    glRotatef(tilt_angle, 0, 0, 1)  
    
    
    glColor3f(0.2, 0.2, 0.2)  
    glPushMatrix()
    glScalef(board_length, board_width, board_thickness)  
    glutSolidCube(1)
    glPopMatrix()
    
    
    if hoverboard_fast_mode:
        
        glColor3f(1.0, 0.2, 0.0)  
        glPushMatrix()
        glScalef(board_length + 8, board_width + 8, board_thickness + 4)  
        glutWireCube(1)
        glPopMatrix()
    else:
        
        glColor3f(0.0, 0.8, 1.0)  
        glPushMatrix()
        glScalef(board_length + 4, board_width + 4, board_thickness + 2)  
        glutWireCube(1)
        glPopMatrix()
    
    
    wheel_radius = 8
    wheel_width = 5
    wheel_positions = [
        (-board_width/2 - 15, -board_length/2 + 20),  
        (-board_width/2 - 15, board_length/2 - 20),   
        (board_width/2 + 15, -board_length/2 + 20),   
        (board_width/2 + 15, board_length/2 - 20)     
    ]
    
    
    
    
    
    for i, (wheel_x, wheel_y) in enumerate(wheel_positions):
        glPushMatrix()
        glTranslatef(wheel_x, wheel_y, -board_thickness/2 - wheel_radius)
        
        
        
        
        glColor3f(0.1, 0.1, 0.1)  
        glRotatef(90, 0, 1, 0)  
        gluCylinder(gluNewQuadric(), wheel_radius, wheel_radius, wheel_width, 12, 2)
        
        
        glColor3f(0.0, 0.8, 1.0)  
        glPushMatrix()
        glTranslatef(-1, 0, 0)
        gluCylinder(gluNewQuadric(), wheel_radius + 1, wheel_radius + 1, 2, 12, 2)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(wheel_width, 0, 0)
        gluCylinder(gluNewQuadric(), wheel_radius + 1, wheel_radius + 1, 2, 12, 2)
        glPopMatrix()
        
        
        glColor3f(0.3, 0.3, 0.3)
        for spoke in range(6):
            glPushMatrix()
            glRotatef(spoke * 60, 1, 0, 0)  
            glTranslatef(wheel_width/2, 0, 0)
            glRotatef(90, 1, 0, 0)  
            gluCylinder(gluNewQuadric(), 1, 1, wheel_radius - 3, 4, 2)
            glPopMatrix()
        
        
        glColor3f(0.4, 0.4, 0.4)
        glTranslatef(wheel_width/2, 0, 0)
        glutSolidSphere(4, 8, 8)
        
        glPopMatrix()
    
    
    for side in [-1, 1]:
        glPushMatrix()
        glTranslatef(0, side * (board_length/2 - 15), -board_thickness/2 - 10)
        
        
        glColor3f(0.3, 0.3, 0.3)
        gluCylinder(gluNewQuadric(), 8, 6, 20, 8, 2)
        
        
        if hoverboard_fast_mode:
            
            glColor3f(1.0, 0.5, 0.0)  
            glTranslatef(0, 0, 20)
            glutSolidSphere(10, 8, 8)  
        else:
            
            glColor3f(0.0, 0.6, 1.0)
            glTranslatef(0, 0, 20)
            glutSolidSphere(6, 8, 8)
        glPopMatrix()
    
    
    for side in [-1, 1]:
        glPushMatrix()
        glTranslatef(0, side * (board_length/2 - 10), board_thickness/2 + 5)
        glColor3f(1.0, 1.0, 0.0)  
        glutSolidSphere(3, 6, 6)
        glPopMatrix()
    
    glPopMatrix()

def draw_player():
    """Draw a stylized human player with running, jumping, sliding, and hoverboard animations."""
    global jump_velocity, is_jumping, is_sliding, is_hoverboard

    
    head_radius = 15
    neck_height = 10
    torso_height = 60
    torso_width = 30
    torso_depth = 15
    arm_length = 60
    leg_length = 80

    
    t = time.time()
    
    
    base_swing_angle = math.sin(t * 6) * 60  
    base_leg_angle = math.sin(t * 6 + math.pi) * 40  
    
    
    if is_sliding and is_hoverboard:
        
        swing_angle = math.sin(t * 6) * 15  
        leg_angle = math.sin(t * 6 + math.pi) * 10  
    elif is_sliding:
        swing_angle = 0
        leg_angle = 0
    
    elif is_hoverboard:
        if hoverboard_fast_mode:
            
            swing_angle = math.sin(t * 12) * 60  
            leg_angle = math.sin(t * 12 + math.pi) * 40  
        else:
            
            swing_angle = math.sin(t * 4) * 20  
            leg_angle = math.sin(t * 4 + math.pi) * 15  
    else:
        swing_angle = base_swing_angle
        leg_angle = base_leg_angle

    
    if is_jumping:
        swing_angle = 60 * math.sin(t * 10)  
        leg_angle = 45 * math.sin(t * 10)    

    
    jump_z = 0
    if is_jumping:
        
        
        jump_z = 0

    
    if is_sliding and is_hoverboard:
        
        player_z_pos = player["z"] + jump_z+30 
    elif is_sliding:
        player_z_pos = 5.0  
    elif is_hoverboard:
        
        player_z_pos = player["z"] + jump_z  
    else:
        player_z_pos = player["z"] + jump_z

    glPushMatrix()
    glTranslatef(player["x"], player["y"], player_z_pos)
    
    
    if is_hoverboard:
        glPushMatrix()
        glTranslatef(0, 0, 0)  
        draw_hoverboard()
        glPopMatrix()

    if is_sliding and is_hoverboard:
        
        
        
        
        
        for i, lx in enumerate([-10, 10]):
            glPushMatrix()
            glTranslatef(lx, 0, 32)  
            
            
            glRotatef(90, 1, 0, 0)  
            
            glColor3f(0.96, 0.96, 0.86)  
            gluCylinder(gluNewQuadric(), 8, 6, leg_length, 8, 2)
            
            
            glTranslatef(0, 0, leg_length+32)
            glColor3f(0.0, 0.0, 0.0)  
            glutSolidSphere(12, 10, 10)
            glPopMatrix()

        
        glPushMatrix()
        glTranslatef(0, 0, 30)  
        glRotatef(90, 1, 0, 0)  
        
        glColor3f(0.5, 0.25, 0.25)  
        glBegin(GL_QUADS)
        
        reduced_height = 20  
        glVertex3f(-torso_width/2, -torso_depth/2, 0)
        glVertex3f(torso_width/2, -torso_depth/2, 0)
        glVertex3f(torso_width/2*0.8, -torso_depth/2, reduced_height)
        glVertex3f(-torso_width/2*0.8, -torso_depth/2, reduced_height)
        
        glVertex3f(-torso_width/2, torso_depth/2, 0)
        glVertex3f(torso_width/2, torso_depth/2, 0)
        glVertex3f(torso_width/2*0.8, torso_depth/2, reduced_height)
        glVertex3f(-torso_width/2*0.8, torso_depth/2, reduced_height)
        glEnd()
        glPopMatrix()

        
        for side in [-1, 1]:
            glPushMatrix()
            glTranslatef(side * (torso_width/2 + 5), 0, 10)
            
            
            glRotatef(90, 1, 0, 0)  
            
            glColor3f(0.9, 0.75, 0.65)  
            gluCylinder(gluNewQuadric(), 5, 4, arm_length, 8, 2)
            
            
            glTranslatef(0, 0, arm_length)
            glColor3f(0.9, 0.75, 0.65)
            glutSolidSphere(8, 10, 10)
            glPopMatrix()

        
        glPushMatrix()
        glTranslatef(0, torso_height/2 + 10, 15+50)  
        glColor3f(0.9, 0.75, 0.65)  
        glutSolidSphere(head_radius, 12, 12)
        
        
        glColor3f(0.55, 0.27, 0.07)
        glPushMatrix()
        glScalef(2.5, 2.5, 0.2)
        glutSolidSphere(head_radius + 5, 12, 12)
        glPopMatrix()
        glTranslatef(0, 0, 8)
        gluCylinder(gluNewQuadric(), 15, 12, 12, 12, 2)
        glPopMatrix()
        
    elif is_sliding:
        
        
        
        
        
        for i, lx in enumerate([-10, 10]):
            glPushMatrix()
            glTranslatef(lx, 0, 5)  
            
            
            glRotatef(90, 1, 0, 0)  
            
            glColor3f(0.96, 0.96, 0.86)  
            gluCylinder(gluNewQuadric(), 8, 6, leg_length, 8, 2)
            
            
            glTranslatef(0, 0, leg_length)
            glColor3f(0.0, 0.0, 0.0)  
            glutSolidSphere(12, 10, 10)
            glPopMatrix()

        
        glPushMatrix()
        glTranslatef(0, 0, 10)  
        glRotatef(90, 1, 0, 0)  
        
        glColor3f(0.5, 0.25, 0.25)  
        glBegin(GL_QUADS)
        
        reduced_height = 20  
        glVertex3f(-torso_width/2, -torso_depth/2, 0)
        glVertex3f(torso_width/2, -torso_depth/2, 0)
        glVertex3f(torso_width/2*0.8, -torso_depth/2, reduced_height)
        glVertex3f(-torso_width/2*0.8, -torso_depth/2, reduced_height)
        
        glVertex3f(-torso_width/2, torso_depth/2, 0)
        glVertex3f(torso_width/2, torso_depth/2, 0)
        glVertex3f(torso_width/2*0.8, torso_depth/2, reduced_height)
        glVertex3f(-torso_width/2*0.8, torso_depth/2, reduced_height)
        glEnd()
        glPopMatrix()

        
        for side in [-1, 1]:
            glPushMatrix()
            glTranslatef(side * (torso_width/2 + 5), 0, 8)
            
            
            glRotatef(90, 1, 0, 0)  
            
            glColor3f(0.9, 0.75, 0.65)  
            gluCylinder(gluNewQuadric(), 5, 4, arm_length, 8, 2)
            
            
            glTranslatef(0, 0, arm_length)
            glColor3f(0.9, 0.75, 0.65)
            glutSolidSphere(8, 10, 10)
            glPopMatrix()

        
        glPushMatrix()
        glTranslatef(0, torso_height/2 + 10, 15)  
        glColor3f(0.9, 0.75, 0.65)  
        glutSolidSphere(head_radius, 12, 12)
        
        
        glColor3f(0.55, 0.27, 0.07)
        glPushMatrix()
        glScalef(2.5, 2.5, 0.2)
        glutSolidSphere(head_radius + 5, 12, 12)
        glPopMatrix()
        glTranslatef(0, 0, 8)
        gluCylinder(gluNewQuadric(), 15, 12, 12, 12, 2)
        glPopMatrix()

    else:
        
        
        
        
        
        
        glPushMatrix()
        glTranslatef(-10, 0, leg_length)
        glRotatef(180, 1, 0, 0)
        glRotatef(leg_angle, 1, 0, 0)
        glColor3f(0.96, 0.96, 0.67)  
        gluCylinder(gluNewQuadric(), 8, 6, leg_length, 8, 2)
        glTranslatef(0, 0, leg_length)
        glColor3f(0.0, 0.0, 0.0)  
        glutSolidSphere(12, 10, 10)
        glPopMatrix()

        
        glPushMatrix()
        glTranslatef(10, 0, leg_length)
        glRotatef(180, 1, 0, 0)
        glRotatef(-leg_angle, 1, 0, 0)
        glColor3f(0.96, 0.96, 0.67)   
        gluCylinder(gluNewQuadric(), 8, 6, leg_length, 8, 2)
        glTranslatef(0, 0, leg_length)
        glColor3f(0.0, 0.0, 0.0)  
        glutSolidSphere(12, 10, 10)
        glPopMatrix()

        
        glPushMatrix()
        glTranslatef(0, 0, leg_length)
        glColor3f(0.5, 0, 0)  
        glBegin(GL_QUADS)
        
        glVertex3f(-torso_width/2, -torso_depth/2, 0)
        glVertex3f(torso_width/2, -torso_depth/2, 0)
        glVertex3f(torso_width/2*0.8, -torso_depth/2, torso_height)
        glVertex3f(-torso_width/2*0.8, -torso_depth/2, torso_height)
        
        glVertex3f(-torso_width/2, torso_depth/2, 0)
        glVertex3f(torso_width/2, torso_depth/2, 0)
        glVertex3f(torso_width/2*0.8, torso_depth/2, torso_height)
        glVertex3f(-torso_width/2*0.8, torso_depth/2, torso_height)
        
        glVertex3f(-torso_width/2, -torso_depth/2, 0)
        glVertex3f(-torso_width/2, torso_depth/2, 0)
        glVertex3f(-torso_width/2*0.8, torso_depth/2, torso_height)
        glVertex3f(-torso_width/2*0.8, -torso_depth/2, torso_height)
        
        glVertex3f(torso_width/2, -torso_depth/2, 0)
        glVertex3f(torso_width/2, torso_depth/2, 0)
        glVertex3f(torso_width/2*0.8, torso_depth/2, torso_height)
        glVertex3f(torso_width/2*0.8, -torso_depth/2, torso_height)
        glEnd()
        glPopMatrix()

        
        for side, ang in [(-1, swing_angle), (1, -swing_angle)]:
            glPushMatrix()
            glTranslatef(side * (torso_width/2 + 5), 0, leg_length + torso_height - 10)
            glRotatef(90, 1, 0, 0)
            glRotatef(ang, 1, 0, 0)
            glColor3f(0.9, 0.75, 0.65)  
            gluCylinder(gluNewQuadric(), 5, 4, arm_length, 8, 2)
            glTranslatef(0, 0, arm_length)
            glColor3f(0.9, 0.75, 0.65)
            glutSolidSphere(8, 10, 10)  
            glPopMatrix()

        
        glPushMatrix()
        glTranslatef(0, 0, leg_length + torso_height)
        glColor3f(0.9, 0.75, 0.65)  
        gluCylinder(gluNewQuadric(), 5, 5, neck_height, 8, 2)
        glPopMatrix()

        
        glPushMatrix()
        glTranslatef(0, 0, leg_length + torso_height + neck_height + head_radius)
        glColor3f(0.9, 0.75, 0.65)  
        glutSolidSphere(head_radius, 12, 12)
        
        
        glColor3f(0.55, 0.27, 0.07)  
        
        glPushMatrix()
        glScalef(2.5, 2.5, 0.2)
        glutSolidSphere(head_radius + 5, 12, 12)
        glPopMatrix()
        
        glTranslatef(0, 0, 10)
        gluCylinder(gluNewQuadric(), 15, 12, 15, 12, 2)
        glPopMatrix()

    glPopMatrix()  


def draw_enemy():
    """Draw a stylized human player with running, jumping, and sliding animations."""
    global enemy_is_jumping, enemy_is_sliding

    
    head_radius = 15
    neck_height = 10
    torso_height = 60
    torso_width = 30
    torso_depth = 15
    arm_length = 60
    leg_length = 80

    
    t = time.time()
    
    
    base_swing_angle = math.sin(t * 6) * 60  
    base_leg_angle = math.sin(t * 6 + math.pi) * 40  
    
    
    if enemy_is_sliding:
        swing_angle = 0
        leg_angle = 0
    elif enemy_is_jumping:
        swing_angle = 60 * math.sin(t * 10)  
        leg_angle = 45 * math.sin(t * 10)
    else:
        
        swing_angle = base_swing_angle
        leg_angle = base_leg_angle

    
    if enemy_is_sliding:
        enemy_z_pos = 5.0  
    else:
        enemy_z_pos = enemy["z"]

    glPushMatrix()
    glTranslatef(enemy["x"], enemy["y"], enemy_z_pos)

    if enemy_is_sliding:
        
        
        
        
        
        for i, lx in enumerate([-10, 10]):
            glPushMatrix()
            glTranslatef(lx, 0, 5)  
            
            
            glRotatef(90, 1, 0, 0)  
            
            glColor3f(0.96, 0.96, 0.86)  
            gluCylinder(gluNewQuadric(), 8, 6, leg_length, 8, 2)
            
            
            glTranslatef(0, 0, leg_length)
            glColor3f(0.0, 0.0, 0.0)  
            glutSolidSphere(12, 10, 10)
            glPopMatrix()

        
        glPushMatrix()
        glTranslatef(0, 0, 10)  
        glRotatef(90, 1, 0, 0)  
        
        glColor3f(0.5, 0.25, 0.25)  
        glBegin(GL_QUADS)
        
        reduced_height = 20  
        glVertex3f(-torso_width/2, -torso_depth/2, 0)
        glVertex3f(torso_width/2, -torso_depth/2, 0)
        glVertex3f(torso_width/2*0.8, -torso_depth/2, reduced_height)
        glVertex3f(-torso_width/2*0.8, -torso_depth/2, reduced_height)
        
        glVertex3f(-torso_width/2, torso_depth/2, 0)
        glVertex3f(torso_width/2, torso_depth/2, 0)
        glVertex3f(torso_width/2*0.8, torso_depth/2, reduced_height)
        glVertex3f(-torso_width/2*0.8, torso_depth/2, reduced_height)
        glEnd()
        glPopMatrix()

        
        for side in [-1, 1]:
            glPushMatrix()
            glTranslatef(side * (torso_width/2 + 5), 0, 8)
            
            
            glRotatef(90, 1, 0, 0)  
            
            glColor3f(0.9, 0.75, 0.65)  
            gluCylinder(gluNewQuadric(), 5, 4, arm_length, 8, 2)
            
            
            glTranslatef(0, 0, arm_length)
            glColor3f(0.9, 0.75, 0.65)
            glutSolidSphere(8, 10, 10)
            glPopMatrix()

        
        glPushMatrix()
        glTranslatef(0, torso_height/2 + 10, 15)  
        glColor3f(0.9, 0.75, 0.65)  
        glutSolidSphere(head_radius, 12, 12)
        
        
        glColor3f(0.55, 0.27, 0.07)
        glPushMatrix()
        glScalef(2.5, 2.5, 0.2)
        glutSolidSphere(head_radius + 5, 12, 12)
        glPopMatrix()
        glTranslatef(0, 0, 8)
        gluCylinder(gluNewQuadric(), 15, 12, 12, 12, 2)
        glPopMatrix()

    else:
        
        
        
        
        
        
        glPushMatrix()
        glTranslatef(-10, 0, leg_length)
        glRotatef(180, 1, 0, 0)
        glRotatef(leg_angle, 1, 0, 0)
        glColor3f(0.96, 0.96, 0.67)  
        gluCylinder(gluNewQuadric(), 8, 6, leg_length, 8, 2)
        glTranslatef(0, 0, leg_length)
        glColor3f(0.0, 0.0, 0.0)  
        glutSolidSphere(12, 10, 10)
        glPopMatrix()

        
        glPushMatrix()
        glTranslatef(10, 0, leg_length)
        glRotatef(180, 1, 0, 0)
        glRotatef(-leg_angle, 1, 0, 0)
        glColor3f(0.96, 0.96, 0.67)   
        gluCylinder(gluNewQuadric(), 8, 6, leg_length, 8, 2)
        glTranslatef(0, 0, leg_length)
        glColor3f(0.0, 0.0, 0.0)  
        glutSolidSphere(12, 10, 10)
        glPopMatrix()

        
        glPushMatrix()
        glTranslatef(0, 0, leg_length)
        glColor3f(0.0, 0.5, 0.8)  
        glBegin(GL_QUADS)
        
        glVertex3f(-torso_width/2, -torso_depth/2, 0)
        glVertex3f(torso_width/2, -torso_depth/2, 0)
        glVertex3f(torso_width/2*0.8, -torso_depth/2, torso_height)
        glVertex3f(-torso_width/2*0.8, -torso_depth/2, torso_height)
        
        glVertex3f(-torso_width/2, torso_depth/2, 0)
        glVertex3f(torso_width/2, torso_depth/2, 0)
        glVertex3f(torso_width/2*0.8, torso_depth/2, torso_height)
        glVertex3f(-torso_width/2*0.8, torso_depth/2, torso_height)
        
        glVertex3f(-torso_width/2, -torso_depth/2, 0)
        glVertex3f(-torso_width/2, torso_depth/2, 0)
        glVertex3f(-torso_width/2*0.8, torso_depth/2, torso_height)
        glVertex3f(-torso_width/2*0.8, -torso_depth/2, torso_height)
        
        glVertex3f(torso_width/2, -torso_depth/2, 0)
        glVertex3f(torso_width/2, torso_depth/2, 0)
        glVertex3f(torso_width/2*0.8, torso_depth/2, torso_height)
        glVertex3f(torso_width/2*0.8, -torso_depth/2, torso_height)
        glEnd()
        glPopMatrix()

        
        for side, ang in [(-1, swing_angle), (1, -swing_angle)]:
            glPushMatrix()
            glTranslatef(side * (torso_width/2 + 5), 0, leg_length + torso_height - 10)
            glRotatef(90, 1, 0, 0)
            glRotatef(ang/2, 1, 0, 0)
            glColor3f(0.9, 0.75, 0.65)  
            gluCylinder(gluNewQuadric(), 5, 4, arm_length, 8, 2)
            glTranslatef(0, 0, arm_length)
            glColor3f(0.9, 0.75, 0.65)
            glutSolidSphere(8, 10, 10)  
            glPopMatrix()

        
        glPushMatrix()
        glTranslatef(0, 0, leg_length + torso_height)
        glColor3f(0.9, 0.75, 0.65)  
        gluCylinder(gluNewQuadric(), 5, 5, neck_height, 8, 2)
        glPopMatrix()

        
        glPushMatrix()
        glTranslatef(0, 0, leg_length + torso_height + neck_height + head_radius)
        glColor3f(0.9, 0.75, 0.65)  
        glutSolidSphere(head_radius, 12, 12)

        
        glColor3f(0.55, 0.27, 0.07)  
        
        glPushMatrix()
        glScalef(2.5, 2.5, 0.2)
        glutSolidSphere(head_radius + 5, 12, 12)
        glPopMatrix()
        
        glTranslatef(0, 0, 10)
        gluCylinder(gluNewQuadric(), 15, 12, 15, 12, 2)
        glPopMatrix()

    glPopMatrix()


def check_obstacle_ahead(x, y, look_ahead_distance=400):
    """Check if there's an obstacle ahead in the enemy's path"""
    for obs in obstacles:
        
        if abs(obs["x"] - x) < 80:  
            
            if obs["y"] > y and obs["y"] - y < look_ahead_distance:
                return obs
    return None

def enemy_decide_action(obstacle, distance_to_obstacle):
    """Enemy decides whether to jump or slide based on obstacle distance"""
    global enemy_is_jumping, enemy_jump_velocity, enemy_is_sliding, enemy_slide_timer
    
    
    if enemy_is_jumping or enemy_is_sliding:
        return False
    
    
    if distance_to_obstacle < 200:  
        decision = random.choice(['jump', 'slide'])
        
        if decision == 'jump':
            enemy_is_jumping = True
            enemy_jump_velocity = JUMP_SPEED
            print(f"Enemy URGENT jump! Distance: {distance_to_obstacle:.1f}")
        else:
            enemy_is_sliding = True
            enemy_slide_timer = slide_duration
            print(f"Enemy URGENT slide! Distance: {distance_to_obstacle:.1f}")
        return True
    
    return False



def update_game(dt):

    global last_spawn_time, distance_traveled, score, lives, road_scroll
    global is_jumping, jump_velocity, is_sliding, coins, coin_count, slide_timer
    global magnet_spin_angle, magnets_collected, magnet_active, magnet_timer
    global enemy_active, enemy_timer, enemy_decision_cooldown
    global enemy_is_jumping, enemy_jump_velocity, enemy_is_sliding, enemy_slide_timer
    global is_hoverboard, hoverboard_tilt, hoverboard_bob,hoverboard_fast_mode
    global forward_speed, game_over
    global combo_multi, two_x_time, two_x_flag, MULTIPLIER_DURATION_S

   
    
    speed_increase_rate = 5.0  
    forward_speed += speed_increase_rate * dt

    to_remove_obs = []
    to_remove_magnets = []
    
    if is_hoverboard:
        OBSTACLE_HEIGHT = 120+60
    else:
        OBSTACLE_HEIGHT = 120
    
    
    current_despawn_y = camera_pos[1] + 1000

    
    if is_sliding:
        player_bottom_z = SLIDE_Z
        player_top_z = SLIDE_Z + SLIDE_HEIGHT
    elif is_hoverboard:
        
        
        if hoverboard_fast_mode:
            bob_speed = HOVERBOARD_BOB_SPEED * 2.5  
            tilt_speed = HOVERBOARD_TILT_SPEED * 2.5  
        else:
            bob_speed = HOVERBOARD_BOB_SPEED
            tilt_speed = HOVERBOARD_TILT_SPEED
            
        hoverboard_bob += bob_speed * dt
        hoverboard_tilt += tilt_speed * dt
        if hoverboard_tilt >= 360:
            hoverboard_tilt -= 360
        
        
        bob_offset = math.sin(hoverboard_bob) * 8.0  
        player["z"] = GROUND_Z + hoverboard_height + bob_offset
        
        
        if is_sliding:
            player_bottom_z = player["z"]
            player_top_z = player["z"] + player["height"]
        else:
            
            player_bottom_z = 0  
            player_top_z = player["z"] + player["height"]  
    else:
        player_bottom_z = player["z"]
        player_top_z = player["z"] + player["height"]

    
    for obs in obstacles:
        
        current_speed = forward_speed * (2.0 if hoverboard_fast_mode else 1.0)
        obs["y"] += current_speed * dt
        if (abs(obs["y"] - player["y"]) < COLLIDE_Y_THRESHOLD and
            abs(obs["x"] - player["x"]) < COLLIDE_X_THRESHOLD):
            obs_bottom = 0.0
            obs_top = OBSTACLE_HEIGHT
            if (player_top_z > obs_bottom) and (player_bottom_z < obs_top):
                to_remove_obs.append(obs)
                lives -= 1
                
                enemy_active = True
                enemy_timer = ENEMY_DURATION
                enemy["x"] = player["x"]
                enemy["y"] = player["y"] +190  
                enemy["z"] = player["z"]   
                if lives < 0:
                    lives = 0
                    game_over= True

    
    to_remove_coin = []
    for c in coins:
        
        current_speed = forward_speed * (2.0 if hoverboard_fast_mode else 1.0)
        c["y"] += current_speed * dt
        coin_bottom = c["z"] - c["size"] / 2
        coin_top = c["z"] + c["size"] / 2

        if magnet_active:
            dx = player["x"] - c["x"]
            dy = player["y"] - c["y"]
            distance = math.sqrt(dx*dx + dy*dy)

            if distance < MAGNET_RANGE:
                
                dir_x = dx / (distance + 1e-6)
                dir_y = dy / (distance + 1e-6)

                
                
                current_speed = forward_speed * (2.0 if hoverboard_fast_mode else 1.0)
                c["x"] += dir_x * current_speed * 2 * dt
                c["y"] += dir_y * current_speed * 2 * dt


        if (abs(c["y"] - player["y"]) < COLLIDE_Y_THRESHOLD and
            abs(c["x"] - player["x"]) < COLLIDE_X_THRESHOLD):
            if (player_top_z > coin_bottom) and (player_bottom_z < coin_top):
                to_remove_coin.append(c)
                coin_count += 1

    
    for m in magnets:
        
        
        current_speed = forward_speed * (2.0 if hoverboard_fast_mode else 1.0)
        m["y"] += (current_speed*2) * dt
        
        
        if abs(m["y"] - player["y"]) < 200:  
            print(f"Magnet at y={m['y']:.1f}, player at y={player['y']:.1f}")
        
        
        
        if is_sliding:
            magnet_bottom = m["collision_z"] - m["size"] / 2
            magnet_top = m["collision_z"] + m["size"] / 2
        else:
            
            magnet_bottom = m["z"] - m["size"] / 2
            magnet_top = m["z"] + m["size"] / 2
        
        if (abs(m["y"] - player["y"]) < COLLIDE_Y_THRESHOLD and
            abs(m["x"] - player["x"]) < COLLIDE_X_THRESHOLD):
            
            
            if is_sliding and is_hoverboard:
                
                player_bottom_z = player["z"]
                player_top_z = player["z"] + player["height"]
            elif is_sliding:
                player_bottom_z = SLIDE_Z
                player_top_z = SLIDE_Z + SLIDE_HEIGHT
            elif is_hoverboard:
                
                player_bottom_z = 0  
                player_top_z = player["z"] + player["height"]  
            else:
                player_bottom_z = player["z"]
                player_top_z = player["z"] + player["height"]
            
            print(f"Near collision! Magnet Z: {magnet_bottom:.1f}-{magnet_top:.1f}, Player Z: {player_bottom_z:.1f}-{player_top_z:.1f}")
            
            
            if (player_top_z > magnet_bottom) and (player_bottom_z < magnet_top):
                to_remove_magnets.append(m)
                magnets_collected += 1
                magnet_active = True
                magnet_timer = MAGNET_DURATION
                print(f"Magnet collected! Total: {magnets_collected}")

    
    for obs in list(obstacles):
        if obs in to_remove_obs or obs["y"] > current_despawn_y:
            obstacles.remove(obs)
    for c in list(coins):
        if c in to_remove_coin or c["y"] > current_despawn_y:
            coins.remove(c)
    for m in list(magnets):
        if m in to_remove_magnets or m["y"] > current_despawn_y:
            magnets.remove(m)

    
    
    current_speed = forward_speed * (2.0 if hoverboard_fast_mode else 1.0)
    distance_traveled += current_speed * dt
    
    base_score = int(distance_traveled // 10)
    if two_x_time != 0.0:
        score = base_score * combo_multi
    else:
        score = base_score

    road_scroll += current_speed * dt

    
    if is_jumping:
        player["z"] += jump_velocity * dt
        jump_velocity += GRAVITY * dt
        if player["z"] <= GROUND_Z:
            player["z"] = GROUND_Z
            is_jumping = False
            jump_velocity = 0.0

    
    global coin_rotation_angle
    coin_rotation_angle += 180 * dt
    if coin_rotation_angle >= 360:
        coin_rotation_angle -= 360

    magnet_spin_angle += 180 * dt
    if magnet_spin_angle >= 360:
        magnet_spin_angle -= 360

    
    if is_sliding:
        slide_timer -= dt
        if slide_timer <= 0:
            is_sliding = False
            player["height"] = NORMAL_HEIGHT
            player["z"] = GROUND_Z

    
    now = time.time()
    if now - last_spawn_time > spawn_interval:
        spawn_count = 1 if random.random() < 0.8 else 2
        for _ in range(spawn_count):
            spawn_obstacle()
            if random.random() < 0.75:
                spawn_coin()
            if random.random() < 0.15:
                spawn_magnet()
        last_spawn_time = now
    
    if magnet_active:
        magnet_timer -= dt
        if magnet_timer <= 0:
            magnet_active = False

    if enemy_active:
        enemy_timer -= dt
        if enemy_timer <= 0:
            enemy_active = False
            
            enemy_is_jumping = False
            enemy_is_sliding = False
            enemy_jump_velocity = 0.0
            enemy_slide_timer = 0.0
        
        
        if enemy_decision_cooldown > 0:
            enemy_decision_cooldown -= dt
        
        
        target_lane_x = LANE_X[player["lane"]]
        if abs(enemy["x"] - target_lane_x) > 50:
            move_speed = 800.0
            if enemy["x"] < target_lane_x:
                enemy["x"] += move_speed * dt
                if enemy["x"] > target_lane_x:
                    enemy["x"] = target_lane_x
            else:
                enemy["x"] -= move_speed * dt
                if enemy["x"] < target_lane_x:
                    enemy["x"] = target_lane_x
        
        
        target_y = player["y"] + 180
        enemy["y"] += (target_y - enemy["y"]) * 2.0 * dt
        
        
        obstacle_ahead = check_obstacle_ahead(enemy["x"], enemy["y"], look_ahead_distance=600)
        
        
        if enemy_is_jumping or enemy_is_sliding:
            
            if not obstacle_ahead:
                print("Enemy cancelling unnecessary action - no obstacle in current lane!")
                enemy_is_jumping = False
                enemy_is_sliding = False
                enemy_jump_velocity = 0.0
                enemy_slide_timer = 0.0
                enemy["z"] = GROUND_Z
            
        else:
            
            if obstacle_ahead and enemy_decision_cooldown <= 0:
                distance_to_obstacle = obstacle_ahead["y"] - enemy["y"]
                action_taken = enemy_decide_action(obstacle_ahead, distance_to_obstacle)
                if action_taken:
                    enemy_decision_cooldown = 0.3
        
        
        if enemy_is_jumping:
            enemy["z"] += enemy_jump_velocity * dt
            enemy_jump_velocity += GRAVITY * dt
            if enemy["z"] <= GROUND_Z:
                enemy["z"] = GROUND_Z
                enemy_is_jumping = False
                enemy_jump_velocity = 0.0
        
        
        if enemy_is_sliding:
            enemy_slide_timer -= dt
            enemy["z"] = SLIDE_Z  
            if enemy_slide_timer <= 0:
                enemy_is_sliding = False
                enemy["z"] = GROUND_Z  
        
        
        if not enemy_is_jumping and not enemy_is_sliding:
            enemy["z"] = GROUND_Z

    if two_x_flag and two_x_time != 0.0:
        if time.time() - two_x_time > MULTIPLIER_DURATION_S:
            two_x_flag = False
            two_x_time = 0.0                
        


def showScreen():
    global game_over

    
    if game_over:
    
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, 1000, 0, 800)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        
        glColor3f(1.0, 0.0, 0.0)
        draw_text_line(400, 420, "GAME OVER", GLUT_BITMAP_TIMES_ROMAN_24)

        
        glColor3f(1.0, 1.0, 1.0)
        draw_text_line(400, 370, "Press 'R' to restart", GLUT_BITMAP_HELVETICA_18)

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

        glutSwapBuffers()
        return


    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)

    setupCamera()

    
    draw_road()
    draw_lamp_posts()
    
    for c in coins:
        draw_coin(c)

    for m in magnets:
        draw_magnet(m)

    for obs in obstacles:
        draw_obstacle(obs)

    
    if not is_fpp_mode:
        draw_player()
        if enemy_active:
            draw_enemy()

    
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    
    glColor3f(1, 1, 1)
    draw_text_line(10, 770, "Score: ")
    glColor3f(1, 1, 0)
    draw_text_line(80, 770, f"{score}")

    glColor3f(1, 1, 1)
    draw_text_line(10, 740, "Lives: ")
    glColor3f(1, 1, 0)
    draw_text_line(80, 740, f"{lives}")

    mode_text = "FPP" if is_fpp_mode else "TPP"
    glColor3f(1, 1, 1)
    draw_text_line(10, 710, "Camera: ")
    glColor3f(1, 1, 0)
    draw_text_line(90, 710, f"{mode_text} (Press F)")

    hoverboard_text = "HOVERBOARD" if is_hoverboard else "NORMAL"
    glColor3f(1, 1, 1)
    draw_text_line(10, 680, "Mode: ")
    glColor3f(1, 1, 0)
    draw_text_line(80, 680, f"{hoverboard_text} (Press C)")

    
    glColor3f(1, 1, 1)
    draw_text_line(590, 770, "Distance: ")
    glColor3f(1, 1, 0)
    draw_text_line(670, 770, f"{int(distance_traveled)} Meters")

    glColor3f(1, 1, 1)
    draw_text_line(590, 740, "Coins: ")
    glColor3f(1, 1, 0)
    draw_text_line(670, 740, f"{int(coin_count)}")

    glColor3f(1, 1, 1)
    draw_text_line(590, 710, "Magnets: ")
    glColor3f(1, 1, 0)
    draw_text_line(670, 710, f"{magnets_collected}")

    glColor3f(1, 1, 1)
    draw_text_line(10, 650, "Press 'R' to restart")

    if two_x_time != 0:
        glColor3f(1.0, 0.5, 0.0)   # orange
        draw_text_line(590, 680, "5x COMBO ACTIVE!",GLUT_BITMAP_TIMES_ROMAN_24)

    if hoverboard_fast_mode:
        glColor3f(1, 1, 1)
        draw_text_line(10, 620, "FAST MODE: ON")

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    glutSwapBuffers()







def main():
    global last_time, last_spawn_time
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    wind = glutCreateWindow(b"3D Endless Runner - Feature 1")

    
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.1, 0.1, 0.12, 1.0)

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    
    last_time = time.time()
    last_spawn_time = time.time() - 1.0  

    glutMainLoop()

if __name__ == "__main__":
    main()
